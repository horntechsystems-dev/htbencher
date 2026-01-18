
import frappe
import subprocess,os
import select
from fabric import Connection

def execute_command(command, bench_doc=None, cwd=None, task_id=None, display_command=None, env=None):
    """
    Execute command either locally or remotely based on bench_doc configuration.
    Streams output to frontend if task_id is provided.
    'env' is a dictionary of environment variables to set.
    """
    if isinstance(command, list):
        command = " ".join(command)
    
    # Capture user and site for background threads/tasks
    user = frappe.session.user if (frappe.session and hasattr(frappe.session, 'user')) else "Administrator"
    site = frappe.local.site if hasattr(frappe.local, 'site') else None
    
    log_cmd = display_command if display_command else command
    log_stream(task_id, f"Executing: {log_cmd}", user=user, site=site)
    
    is_remote = False
    if bench_doc:
        if hasattr(bench_doc, 'server') and bench_doc.server:
            # Check Linked Server
            try:
                server_doc = frappe.get_doc("HT Server", bench_doc.server)
                is_local_server = server_doc.hostname in ["localhost", "127.0.0.1", "::1"] or server_doc.server_name.lower() == "local"
                is_remote = not is_local_server
            except Exception:
                # Fallback if server doc fetch fails
                 is_remote = bench_doc.is_remote
        elif hasattr(bench_doc, 'is_remote'):
            is_remote = bench_doc.is_remote
        
    if is_remote:
        return execute_remote_command(command, bench_doc, cwd, task_id, user=user, site=site, display_command=display_command, env=env)
    else:
        return execute_local_command(command, cwd, task_id, user=user, site=site, display_command=display_command, env=env)

def execute_local_command(command, cwd=None, task_id=None, user=None, site=None, display_command=None, env=None):
    """
    Execute command locally using subprocess with streaming
    """
    try:
        # Prep environment
        full_env = os.environ.copy()
        if env:
            full_env.update(env)
            
        if not user:
            user = frappe.session.user if (frappe.session and hasattr(frappe.session, 'user')) else "Administrator"
        if not site:
            site = frappe.local.site if hasattr(frappe.local, 'site') else None
            
        log_cmd = display_command if display_command else command
        frappe.log_error(f"Executing Local: {log_cmd} in {cwd}", "SSH Executor")
        
        process = subprocess.Popen(
            command, 
            shell=True, 
            cwd=cwd, 
            env=full_env,
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Stream output
        full_output = []
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                line = output.strip()
                full_output.append(line)
                log_stream(task_id, line, user=user, site=site)
                
        # Also catch stderr
        stderr_output = process.stderr.read()
        if stderr_output:
             log_stream(task_id, f"STDERR: {stderr_output}", error=True, user=user, site=site)
             full_output.append(stderr_output)
             
        rc = process.poll()
        if rc != 0:
            msg = f"Command Failed with Return Code {rc}"
            log_stream(task_id, msg, error=True, user=user, site=site)
            # Log potentially long output to error log but truncated
            err_details = "\n".join(full_output)
            frappe.log_error(f"Command Failed: {err_details[:2000]}", "SSH Executor Failed")
            return False, "\n".join(full_output)
            
        return True, "\n".join(full_output)
    except Exception as e:
        error_msg = str(e)[:140] # Truncate primarily for safety
        frappe.log_error(f"Local Execution Error: {str(e)[:2000]}", "SSH Executor")
        log_stream(task_id, f"Error: {error_msg}", error=True, user=user, site=site)
        return False, str(e)

def execute_remote_command(command, bench_doc, cwd=None, task_id=None, user=None, site=None, display_command=None, env=None):
    """
    Execute command remotely using fabric
    """
    try:
        # Prepend environment variables to command if provided
        if env:
            env_prefix = " ".join([f"{k}={v}" for k, v in env.items()])
            command = f"export {env_prefix} && {command}"
            if display_command:
                display_command = f"export {env_prefix} && {display_command}"
        
        from invoke import Responder
        if not user:
            user = frappe.session.user if (frappe.session and hasattr(frappe.session, 'user')) else "Administrator"
        if not site:
            site = frappe.local.site if hasattr(frappe.local, 'site') else None

        # Determine credentials
        password = None
        hostname = getattr(bench_doc, 'hostname', None)
        username = getattr(bench_doc, 'username', None)
        ssh_key_path = getattr(bench_doc, 'ssh_key_path', None)
        
        if bench_doc.server:
            server_doc = frappe.get_doc("HT Server", bench_doc.server)
            hostname = server_doc.hostname
            username = server_doc.username
            password = server_doc.get_password('password')
            ssh_key_path = server_doc.ssh_key_path or getattr(bench_doc, 'ssh_key_path', None)

        elif getattr(bench_doc, 'password', None):
            password = bench_doc.get_password('password')
        
        connect_kwargs = {}
        if password:
            connect_kwargs['password'] = password
        
        if ssh_key_path:
            connect_kwargs['key_filename'] = ssh_key_path
            
        c = Connection(
            host=hostname,
            user=username,
            port=bench_doc.port or 22,
            connect_kwargs=connect_kwargs
        )
        
        log_cmd = display_command if display_command else command
        frappe.log_error(f"Executing Remote ({hostname}): {log_cmd} in {cwd}", "SSH Executor")
        log_stream(task_id, f"Connected to {hostname}", user=user, site=site)
        
        # Sudo password responder
        watchers = []
        if password:
            # Matches strings like "[sudo] password for user: "
            sudo_responder = Responder(
                pattern=r"\[sudo\] password for .*: ",
                response=password + "\n"
            )
            watchers.append(sudo_responder)
        
        # Bench get-app overwrite confirmation responder
        # Matches: "Do you want to continue and overwrite it? [y/N]:"
        overwrite_responder = Responder(
            pattern=r"Do you want to continue and overwrite it\? \[y/N\]:",
            response="y\n"
        )
        watchers.append(overwrite_responder)
        
        class RealtimeStream:
            def write(self, text):
                if text.strip():
                     # Use the captured identities
                     log_stream(task_id, text, user=user, site=site)
            def flush(self):
                pass
                
        stream_logger = RealtimeStream()
        
        with c:
            run_kwargs = {
                "warn": True, 
                "out_stream": stream_logger, 
                "err_stream": stream_logger,
                "watchers": watchers,
                "pty": True, # Needed for proper sudo interaction sometimes
                "in_stream": False # Prevent OSError: [Errno 25] Inappropriate ioctl for device
            }
            
            if cwd:
                with c.cd(cwd):
                    result = c.run(command, **run_kwargs)
            else:
                result = c.run(command, **run_kwargs)
                
        if result.failed:
             msg = f"Remote Command Failed: {result.stderr}"
             log_stream(task_id, msg, error=True, user=user, site=site)
             return False, result.stderr
             
        return True, result.stdout
        
    except Exception as e:
        frappe.log_error(f"Remote Execution Error: {str(e)[:2000]}", "SSH Executor")
        log_stream(task_id, f"Error: {str(e)}", error=True, user=user, site=site)
        return False, str(e)

def log_stream(task_id, message, error=False, user=None, site=None):
    if task_id:
        # Ensure site context in background threads
        if site and not hasattr(frappe.local, 'site'):
            frappe.local.site = site
            
        if not user:
            try:
                user = frappe.session.user if (frappe.session and hasattr(frappe.session, 'user')) else "Administrator"
            except Exception:
                user = "Administrator"

        frappe.publish_realtime(
            event='htbench_task_log',
            message={
                'task_id': task_id,
                'log': message,
                'error': error
            },
            user=user
        )
