
import frappe
import os
import glob
from htbencher.custom.ssh_utils import execute_command

def create_bench(bench_name, server, python_version="python3.11", frappe_branch="version-15", apps=None, task_id=None):
    """
    Create a new bench with specified configuration
    """
    try:
        # Create HT Bench record first to get connection details or link it
        bench_doc = frappe.get_doc({
            "doctype": "HT Bench",
            "bench_name": bench_name,
            "server": server,
            "path": bench_name, # Default path same as name
            "python_version": python_version,
            "frappe_branch": frappe_branch,
            "status": "Inactive" # Mark active after success
        })
        bench_doc.insert(ignore_permissions=True)
        frappe.db.commit()

        cmd = [
            "bench", "init", bench_name,
            "--frappe-branch", frappe_branch,
            "--python", python_version
        ]
        
        # Determine execution directory.
        from frappe.utils import get_bench_path
        cwd = os.path.dirname(get_bench_path())
        
        # Execute command using the bench_doc which now has server link for sudo responder
        success, output = execute_command(cmd, bench_doc=bench_doc, cwd=cwd, task_id=task_id)

        if not success:
            frappe.publish_realtime('htbench_task_complete', {'task_id': task_id, 'status': 'failed'}, user=frappe.session.user)
            return False

        # Mark bench as active
        bench_doc.status = "Active"
        bench_doc.save(ignore_permissions=True)
        frappe.db.commit()

        if apps:
            for app_name in apps.split(','): 
                get_app(bench_name, app_name.strip(), task_id=task_id)

        frappe.publish_realtime('htbench_task_complete', {'task_id': task_id, 'status': 'success'}, user=frappe.session.user)
        return True
    except Exception as e:
        frappe.log_error(str(e), "Bench Creation Failed")
        execute_command(f"Error: {e}", task_id=task_id) # Log error to stream
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
        
        # Fallback to local glob if command failed or returned nothing (and no server specified)
        if not pythons and not server:
            paths = glob.glob('/usr/bin/python3.*')
            for p in paths:
                name = os.path.basename(p)
                if name[-1].isdigit():
                    pythons.append(name)

        pythons = sorted(list(set(pythons)))
        
        # Add 'python3' as generic option if not present
        if 'python3' not in pythons:
            pythons.insert(0, 'python3')
            
    except Exception as e:
        frappe.log_error(f"Error fetching pythons: {e}", "Bench Operations")
        pythons = ['python3', 'python3.10', 'python3.11']
        
    return pythons

def get_app(bench_name, app_doc_name, task_id=None):
    """
    Get app from HT App definition
    """
    import os
    import shlex
    
    try:
        app_doc = frappe.get_doc("HT App", app_doc_name)
        repo_url = app_doc.repo_url
        branch = app_doc.branch or "main"
        
        bench_doc = frappe.db.get_value("HT Bench", {"bench_name": bench_name}, "name")
        if bench_doc:
             bench_doc = frappe.get_doc("HT Bench", bench_doc)
        
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
            
            success, output = execute_command(full_cmd, bench_doc=bench_doc if bench_doc else None, cwd=bench_name, task_id=task_id, display_command=display_cmd)

        else:
            success, output = execute_command(bench_cmd, bench_doc=bench_doc if bench_doc else None, cwd=bench_name, task_id=task_id)
        
        return success
    except Exception as e:
        frappe.log_error(f"Failed to get app {app_doc_name}: {e}", "App Operations")
        execute_command(f"Error getting app: {e}", task_id=task_id)
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

        success, output = execute_command(cmd, bench_doc=bench_doc if bench_doc else None, cwd=bench_name, task_id=task_id)
        
        frappe.publish_realtime('htbench_task_complete', {'task_id': task_id, 'status': 'success' if success else 'failed'}, user=frappe.session.user)
        return success
    except Exception as e:
        frappe.log_error(f"Failed to update bench {bench_name}: {e}", "Bench Update")
        execute_command(f"Error: {e}", task_id=task_id)
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
             
        success, output = execute_command(cmd, bench_doc=bench_doc if bench_doc else None, cwd=bench_name, task_id=task_id)
        
        frappe.publish_realtime('htbench_task_complete', {'task_id': task_id, 'status': 'success' if success else 'failed'}, user=frappe.session.user)
        return success
    except Exception as e:
        frappe.log_error(f"Failed to build bench {bench_name}: {e}", "Bench Build")
        execute_command(f"Error: {e}", task_id=task_id)
        frappe.publish_realtime('htbench_task_complete', {'task_id': task_id, 'status': 'failed'}, user=frappe.session.user)
        return False

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
            python_version=source_doc.python_version,
            frappe_branch=source_doc.frappe_branch,
            apps=apps_str,
            task_id=task_id
        )
        
        # In a real scenario, we might also want to copy sites/configs, 
        # but for this "cloning" we focus on the environment setup.
        
        return success
    except Exception as e:
        frappe.log_error(f"Failed to clone bench {source_bench}: {e}", "Bench Cloning")
        execute_command(f"Error: {e}", task_id=task_id)
        frappe.publish_realtime('htbench_task_complete', {'task_id': task_id, 'status': 'failed'}, user=frappe.session.user)
        return False
