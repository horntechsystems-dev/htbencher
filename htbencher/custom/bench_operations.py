
import frappe
import os
import glob
from htbencher.custom.ssh_utils import execute_command

def install_dependencies(python_version, node_version="18", bench_doc=None, cwd=None, task_id=None, user=None):
    if task_id:
        frappe.publish_realtime('htbench_task_progress', {
            'task_id': task_id,
            'percentage': 15,
            'status': f"Checking/Installing dependencies (Python {python_version}, Node {node_version})..."
        }, user=user)

    # 1. Update and install base requirements
    execute_command(["sudo", "apt-get", "update", "-y"], bench_doc=bench_doc, cwd=cwd, task_id=task_id)
    execute_command(["sudo", "apt-get", "install", "-y", "software-properties-common", "curl", "wget"], bench_doc=bench_doc, cwd=cwd, task_id=task_id)
    execute_command(["sudo", "add-apt-repository", "-y", "ppa:deadsnakes/ppa"], bench_doc=bench_doc, cwd=cwd, task_id=task_id)
    execute_command(["sudo", "apt-get", "update", "-y"], bench_doc=bench_doc, cwd=cwd, task_id=task_id)

    # 2. Install requested python version and virtualenv dependencies
    py_deps = [python_version, f"{python_version}-venv", f"{python_version}-dev"]
    execute_command(["sudo", "apt-get", "install", "-y"] + py_deps, bench_doc=bench_doc, cwd=cwd, task_id=task_id)

    # 3. Install NVM
    nvm_cmd = "curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash"
    execute_command(nvm_cmd, bench_doc=bench_doc, cwd=cwd, task_id=task_id)

    # 4. Install Node via NVM
    node_cmd = f'bash -c "export NVM_DIR=\\"$HOME/.nvm\\" && [ -s \\"$NVM_DIR/nvm.sh\\" ] && \\. \\"$NVM_DIR/nvm.sh\\" && nvm install {node_version} && nvm use {node_version} && npm install -g yarn"'
    execute_command(node_cmd, bench_doc=bench_doc, cwd=cwd, task_id=task_id)

    return True

def create_bench(bench_name, server, python_version="python3.11", node_version="18", frappe_branch="version-15", apps=None, task_id=None):
    """
    Create a new bench with specified configuration
    """
    def update_progress(percentage, status):
        if task_id:
            frappe.publish_realtime('htbench_task_progress', {
                'task_id': task_id,
                'percentage': percentage,
                'status': status
            }, user=frappe.session.user)

    # Determine execution directory.
    from frappe.utils import get_bench_path
    parent_dir = os.path.dirname(get_bench_path())
    absolute_path = os.path.join(parent_dir, bench_name)

    try:
        update_progress(10, "Preparing Bench Record...")
        if task_id:
            frappe.cache().set_value(f"htbench_status::{task_id}", "running", expires_in_sec=3600)
            
        # Create HT Bench record first to get connection details or link it
        bench_doc = frappe.get_doc({
            "doctype": "HT Bench",
            "bench_name": bench_name,
            "server": server,
            "path": absolute_path, # Use absolute path
            "python_version": python_version,
            "node_version": node_version,
            "frappe_branch": frappe_branch,
            "status": "Inactive" # Mark active after success
        })
        bench_doc.insert(ignore_permissions=True)
        frappe.db.commit()

        # Install dependencies before init (python version, nvm, node, yarn)
        install_dependencies(python_version, node_version=node_version, bench_doc=bench_doc, cwd=parent_dir, task_id=task_id, user=frappe.session.user if frappe.session else "Administrator")

        cmd = [
            "bench", "init", bench_name,
            "--frappe-branch", frappe_branch,
            "--python", python_version
        ]
        
        update_progress(20, "Initializing Bench (this may take a few minutes)...")
        
        cwd = parent_dir
        
        # Execute command using the bench_doc which now has server link for sudo responder
        success, output = execute_command(
            cmd, 
            bench_doc=bench_doc, 
            cwd=cwd, 
            task_id=task_id, 
            env={"FRAPPE_DOCKER_BUILD": "1"}
        )

        if not success:
            if task_id:
                 frappe.cache().set_value(f"htbench_status::{task_id}", "failed", expires_in_sec=3600)
            frappe.publish_realtime('htbench_task_complete', {'task_id': task_id, 'status': 'failed'}, user=frappe.session.user)
            return False

        update_progress(60, "Bench Initialized. Finalizing setup...")
        # Mark bench as active
        bench_doc.status = "Active"
        bench_doc.save(ignore_permissions=True)
        frappe.db.commit()

        if apps:
            app_list = apps.split(',')
            total_apps = len(app_list)
            for idx, app_name in enumerate(app_list):
                app_name = app_name.strip()
                progress = 60 + int((idx / total_apps) * 35)
                update_progress(progress, f"Installing App: {app_name} ({idx+1}/{total_apps})...")
                get_app(bench_name, app_name, task_id=task_id, update_task=False)

        update_progress(100, "Bench Creation Successful!")
        if task_id:
             frappe.cache().set_value(f"htbench_status::{task_id}", "success", expires_in_sec=3600)
        frappe.publish_realtime('htbench_task_complete', {'task_id': task_id, 'status': 'success'}, user=frappe.session.user)
        return True
    except Exception as e:
        frappe.log_error(str(e), "Bench Creation Failed")
        if task_id:
             frappe.cache().set_value(f"htbench_status::{task_id}", "failed", expires_in_sec=3600)
        frappe.publish_realtime("htbench_task_log", {"task_id": task_id, "log": f"Error: {e}", "error": True}, user=frappe.session.user if frappe.session else "Administrator") # Log error to stream
        frappe.publish_realtime('htbench_task_complete', {'task_id': task_id, 'status': 'failed'}, user=frappe.session.user)
        return False

def get_system_pythons(server=None):
    """
    Scan for available python versions in /usr/bin.
    Returns a list of versions like ['python3.10', 'python3.11']
    """
    pythons = []
    try:
        # Create a dummy object to leverage execute_command's server resolution logic
        class DummyBench:
            def __init__(self, server_name):
                self.server = server_name
                self.is_remote = 0 # Default, will be overridden by server link logic
                # server properties needed by execute_command if it decides to go remote:
                # server, hostname, username, ssh_key_path etc are fetched from HT Server doc 
                # inside execute_command logic if .server is present.
        
        bench_doc = DummyBench(server) if server else None
        
        # Command to list python versions. 
        # listing /usr/bin/python3* is standard for linux.
        # We use wildcards to catch python3, python3.11, etc.
        cmd = "ls -1 /usr/bin/python3*" 
        
        # We use execute_command which handles local/remote switch based on server
        success, output = execute_command(cmd, bench_doc=bench_doc)
        if success:
            frappe.log_error(f"Python detection output: {output}", "Bench Operations Debug")
            lines = output.strip().split('\n')
            for line in lines:
                line = line.strip()
                if not line: continue
                
                # line is full path e.g. /usr/bin/python3.10
                name = os.path.basename(line)
                
                # Filter unwanted binaries
                if any(x in name for x in ['config', 'pip', 'yamllint', 'paste', 'to']):
                    continue
                    
                # Accept 'python3' or 'python3.X'
                if name == 'python3' or (name.startswith('python3.') and name[-1].isdigit()):
                     pythons.append(name)
        else:
            frappe.log_error(f"Python detection failed: {output}", "Bench Operations Error")
        
        # Fallback to local glob if command failed or returned nothing (and no server specified)
        if not pythons and not server:
            paths = glob.glob('/usr/bin/python3.*')
            for p in paths:
                name = os.path.basename(p)
                if name[-1].isdigit():
                    pythons.append(name)

        # Add common versions if not present
        common_pythons = ['python3.10', 'python3.11', 'python3.12', 'python3.13']
        for cp in common_pythons:
            if cp not in pythons:
                pythons.append(cp)

        # Add historical versions from existing benches
        historical = frappe.get_all("HT Bench", fields=["python_version"], distinct=True)
        for h in historical:
            v = h.python_version
            if v and v not in pythons:
                pythons.append(v)

        pythons = sorted(list(set(pythons)))
        
        # Add 'python3' as generic option if not present
        if 'python3' not in pythons:
            pythons.insert(0, 'python3')
            
        # Add 'Other...' for manual entry
        pythons.append('Other...')
            
    except Exception as e:
        frappe.log_error(f"Error fetching pythons: {e}\n{frappe.get_traceback()}", "Bench Operations")
        pythons = ['python3', 'python3.10', 'python3.11']
        
    return pythons

def get_system_nodes(server=None):
    """
    Return a list of common Node mapping or valid inputs for nvm install.
    Includes historical versions from existing benches.
    """
    nodes = ["14", "16", "18", "20", "22", "23", "--lts", "--latest"]
    
    # Add historical
    try:
        historical = frappe.get_all("HT Bench", fields=["node_version"], distinct=True)
        for h in historical:
            v = h.node_version
            if v and v not in nodes:
                nodes.append(v)
    except Exception:
        pass

    nodes = sorted(list(set(nodes)), key=lambda x: (not x.isdigit(), int(x) if x.isdigit() else x))
    nodes.append('Other...')
    return nodes

def get_app(bench_name, app_doc_name, task_id=None, update_task=True):
    """
    Get app from HT App definition
    """
    import os
    import shlex
    
    if update_task and task_id:
        frappe.cache().set_value(f"htbench_status::{task_id}", "running", expires_in_sec=3600)
        
    try:
        app_doc = frappe.get_doc("HT App", app_doc_name)
        repo_url = app_doc.repo_url
        branch = app_doc.branch or "main"
        
        bench_doc = frappe.db.get_value("HT Bench", {"bench_name": bench_name}, "name")
        if bench_doc:
             bench_doc = frappe.get_doc("HT Bench", bench_doc)
        
        # Use stored absolute path or fallback to base directory
        bench_path = bench_doc.path if bench_doc and bench_doc.path else bench_name
        
        # Build base command
        bench_cmd = f"bench get-app {repo_url} --branch {branch}"
        
        # Handle SSH key for private repositories
        if app_doc.is_private and app_doc.ssh_private_key:
            # Generate a truly unique temp filename using current timestamp or similar to avoid collisions
            # but keep it simple for now. We will use mktemp in shell.
            
            # Ensure key ends with newline
            ssh_key_content = app_doc.ssh_private_key
            if not ssh_key_content.endswith('\n'):
                ssh_key_content += '\n'
            
            # Escape the key content for shell echo
            # We use a heredoc pattern or simple echo with careful quoting
            # Safer to write to a temp file via python? NO, that caused the permission issue.
            # We must create it AS the user.
            
            # Use 'cat' with heredoc to write key to a file on the target system
            # We wrap the key in a way that preserves newlines
            
            # We'll construct a complex shell command:
            # 1. Create temp file
            # 2. Write key to it
            # 3. Chmod it
            # 4. Run bench command
            # 5. Remove temp file
            
            # Use python's hex encoding to safely transport the key content without shell quoting hell
            import binascii
            key_hex = binascii.hexlify(ssh_key_content.encode('utf-8')).decode('utf-8')
            
            # python3 -c "import binascii, sys; sys.stdout.buffer.write(binascii.unhexlify('${key_hex}'))" > temp_key
            
            full_cmd = (
                f"temp_key=$(mktemp) && "
                f"python3 -c \"import binascii, sys; sys.stdout.buffer.write(binascii.unhexlify('{key_hex}'))\" > \"$temp_key\" && "
                f"chmod 600 \"$temp_key\" && "
                f"export GIT_SSH_COMMAND=\"ssh -i $temp_key -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null\" && "
                f"{bench_cmd}; "
                f"ret=$?; "
                f"rm -f \"$temp_key\"; "
                f"exit $ret"
            )
            
            # Log a sanitized version
            display_cmd = (
                f"export GIT_SSH_COMMAND='ssh -i [private_key_file] -o StrictHostKeyChecking=no' && "
                f"{bench_cmd}"
            )
            
            success, output = execute_command(
                full_cmd, 
                bench_doc=bench_doc if bench_doc else None, 
                cwd=bench_path, 
                task_id=task_id, 
                display_command=display_cmd,
                env={"FRAPPE_DOCKER_BUILD": "1"}
            )

        else:
            success, output = execute_command(
                bench_cmd, 
                bench_doc=bench_doc if bench_doc else None, 
                cwd=bench_path, 
                task_id=task_id,
                env={"FRAPPE_DOCKER_BUILD": "1"}
            )
        
        if update_task and task_id:
             frappe.cache().set_value(f"htbench_status::{task_id}", "success" if success else "failed", expires_in_sec=3600)
             frappe.publish_realtime('htbench_task_complete', {'task_id': task_id, 'status': 'success' if success else 'failed'}, user=frappe.session.user if frappe.session else "Administrator")
             
        return success
    except Exception as e:
        frappe.log_error(f"Failed to get app {app_doc_name}: {e}", "App Operations")
        frappe.publish_realtime("htbench_task_log", {"task_id": task_id, "log": f"Error getting app: {e}", "error": True}, user=frappe.session.user if frappe.session else "Administrator")
        
        if update_task and task_id:
             frappe.cache().set_value(f"htbench_status::{task_id}", "failed", expires_in_sec=3600)
             frappe.publish_realtime('htbench_task_complete', {'task_id': task_id, 'status': 'failed'}, user=frappe.session.user if frappe.session else "Administrator")
             
        return False

def update_bench(bench_name, task_id=None):
    """
    Run bench update
    """
    try:
        cmd = ["bench", "update"]
        
        bench_doc = frappe.db.get_value("HT Bench", {"bench_name": bench_name}, "name")
        if bench_doc:
             bench_doc = frappe.get_doc("HT Bench", bench_doc)

        # Use stored absolute path or fallback to name
        bench_path = bench_doc.path if bench_doc and bench_doc.path else bench_name

        success, output = execute_command(
            cmd, 
            bench_doc=bench_doc if bench_doc else None, 
            cwd=bench_path, 
            task_id=task_id,
            env={"FRAPPE_DOCKER_BUILD": "1"}
        )

        if task_id:
             frappe.cache().set_value(f"htbench_status::{task_id}", "success" if success else "failed", expires_in_sec=3600)
        frappe.publish_realtime('htbench_task_complete', {'task_id': task_id, 'status': 'success' if success else 'failed'}, user=frappe.session.user)
        return success
    except Exception as e:
        frappe.log_error(f"Failed to update bench {bench_name}: {e}", "Bench Update")
        if task_id:
             frappe.cache().set_value(f"htbench_status::{task_id}", "failed", expires_in_sec=3600)
        frappe.publish_realtime("htbench_task_log", {"task_id": task_id, "log": f"Error: {e}", "error": True}, user=frappe.session.user if frappe.session else "Administrator")
        frappe.publish_realtime('htbench_task_complete', {'task_id': task_id, 'status': 'failed'}, user=frappe.session.user)
        return False

def build_bench(bench_name, task_id=None):
    """
    Run bench build
    """
    try:
        cmd = ["bench", "build"]
        
        bench_doc = frappe.db.get_value("HT Bench", {"bench_name": bench_name}, "name")
        if bench_doc:
             bench_doc = frappe.get_doc("HT Bench", bench_doc)
             
        # Use stored absolute path or fallback to name
        bench_path = bench_doc.path if bench_doc and bench_doc.path else bench_name

        success, output = execute_command(
            cmd, 
            bench_doc=bench_doc if bench_doc else None, 
            cwd=bench_path, 
            task_id=task_id,
            env={"FRAPPE_DOCKER_BUILD": "1"}
        )

        if task_id:
             frappe.cache().set_value(f"htbench_status::{task_id}", "success" if success else "failed", expires_in_sec=3600)
        frappe.publish_realtime('htbench_task_complete', {'task_id': task_id, 'status': 'success' if success else 'failed'}, user=frappe.session.user)
        return success
    except Exception as e:
        frappe.log_error(f"Failed to build bench {bench_name}: {e}", "Bench Build")
        if task_id:
             frappe.cache().set_value(f"htbench_status::{task_id}", "failed", expires_in_sec=3600)
        frappe.publish_realtime("htbench_task_log", {"task_id": task_id, "log": f"Error: {e}", "error": True}, user=frappe.session.user if frappe.session else "Administrator")
        frappe.publish_realtime('htbench_task_complete', {'task_id': task_id, 'status': 'failed'}, user=frappe.session.user)
        return False

def uninstall_app(bench_name, app_name, task_id=None):
    """
    Remove an app from a bench
    """
    try:
        cmd = ["bench", "remove-app", app_name, "--force"]
        
        bench_doc = frappe.db.get_value("HT Bench", {"bench_name": bench_name}, "name")
        if bench_doc:
             bench_doc = frappe.get_doc("HT Bench", bench_doc)
             
        bench_path = bench_doc.path if bench_doc and bench_doc.path else bench_name

        success, output = execute_command(
            cmd, 
            bench_doc=bench_doc if bench_doc else None, 
            cwd=bench_path, 
            task_id=task_id,
            env={"FRAPPE_DOCKER_BUILD": "1"}
        )

        if task_id:
             frappe.cache().set_value(f"htbench_status::{task_id}", "success" if success else "failed", expires_in_sec=3600)
        frappe.publish_realtime('htbench_task_complete', {'task_id': task_id, 'status': 'success' if success else 'failed'}, user=frappe.session.user)
        return success
    except Exception as e:
        frappe.log_error(f"Failed to remove app {app_name} from bench {bench_name}: {e}", "Bench App Removal")
        if task_id:
             frappe.cache().set_value(f"htbench_status::{task_id}", "failed", expires_in_sec=3600)
        frappe.publish_realtime("htbench_task_log", {"task_id": task_id, "log": f"Error: {e}", "error": True}, user=frappe.session.user if frappe.session else "Administrator")
        frappe.publish_realtime('htbench_task_complete', {'task_id': task_id, 'status': 'failed'}, user=frappe.session.user)
        return False

import frappe
import os

def get_installed_apps(bench_name):
    """
    Returns list of apps cloned in the bench's apps folder
    (i.e., apps available on the bench, not necessarily enabled in sites)
    """
    try:
        # Get bench path
        bench_doc_name = frappe.get_value("HT Bench", {"bench_name": bench_name}, "name")
        if bench_doc_name:
            bench_doc = frappe.get_doc("HT Bench", bench_doc_name)
            bench_path = bench_doc.path
        else:
            bench_path = bench_name  # fallback

        apps_path = os.path.join(bench_path, "apps")
        if not os.path.exists(apps_path):
            return []

        # List directories in apps folder
        apps = [
            d for d in os.listdir(apps_path)
            if os.path.isdir(os.path.join(apps_path, d))
        ]
        return apps

    except Exception as e:
        frappe.log_error(f"Failed to list apps in bench {bench_name}: {e}", "Bench App List")
        return []


def clone_bench(source_bench, new_bench_name, task_id=None):
    """
    Clone an existing bench configuration to a new bench
    """
    try:
        source_doc = frappe.get_doc("HT Bench", source_bench)
        
        # Get apps as comma separated string of HT App names
        apps = [d.app for d in source_doc.apps]
        apps_str = ",".join(apps) if apps else None
        
        success = create_bench(
            bench_name=new_bench_name,
            server=source_doc.server,
            python_version=source_doc.python_version,
            node_version=source_doc.node_version if hasattr(source_doc, 'node_version') else "18",
            frappe_branch=source_doc.frappe_branch,
            apps=apps_str,
            task_id=task_id
        )
        
        # In a real scenario, we might also want to copy sites/configs, 
        # but for this "cloning" we focus on the environment setup.
        
        return success
    except Exception as e:
        frappe.log_error(f"Failed to clone bench {source_bench}: {e}", "Bench Cloning")
        if task_id:
             frappe.cache().set_value(f"htbench_status::{task_id}", "failed", expires_in_sec=3600)
        frappe.publish_realtime("htbench_task_log", {"task_id": task_id, "log": f"Error: {e}", "error": True}, user=frappe.session.user if frappe.session else "Administrator")
        frappe.publish_realtime('htbench_task_complete', {'task_id': task_id, 'status': 'failed'}, user=frappe.session.user)
        return False
