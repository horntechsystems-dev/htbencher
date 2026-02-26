
import frappe
import subprocess, os
import select
from fabric import Connection
import shlex
import tempfile

ALLOWED_COMMANDS = ['bench', 'cd', 'ls', 'git', 'echo', 'chmod', 'rm', 'sudo', 'service', 'systemctl', 'mktemp', 'python3', 'python', 'cat']
ALLOWED_BENCH_SUBCOMMANDS = [
    'init', 'get-app', 'new-site', 'drop-site', 'backup', 'migrate', 
    '--site', 'setup', 'restart', 'start', 'pip', 'console', 'destroy-all-sites',
    'remove-app', 'uninstall-app', 'install-app', 'build', 'execute'
]

def validate_command(command):
    """
    Validate if the command is allowed to be executed.
    """
    if not command:
        return False, "Empty command"
        
    # Split command into parts safely
    try:
        # Handle command chaining
        parts = []
        current_part = []
        tokens = shlex.split(command)
        
        for token in tokens:
            if token in ['&&', ';', '||']:
                if current_part:
                    parts.append(current_part)
                current_part = []
            else:
                current_part.append(token)
        if current_part:
            parts.append(current_part)
            
        for cmd_parts in parts:
            if not cmd_parts:
                continue
                
            base_cmd = cmd_parts[0]
            
            # Handle export (env vars)
            if base_cmd == 'export':
                continue
                
            # Handle variable assignments (e.g. temp_key=$(mktemp) or VAR=val)
            if '=' in base_cmd and not base_cmd.startswith('/'):
                continue
                
            if base_cmd not in ALLOWED_COMMANDS:
                return False, f"Command '{base_cmd}' is not allowed."
                
            if base_cmd == 'bench':
                if len(cmd_parts) > 1:
                    subcmd = cmd_parts[1]
                    # Handle 'bench --site site_name subcommand'
                    if subcmd == '--site':
                        if len(cmd_parts) > 3:
                            real_subcmd = cmd_parts[3]
                            if real_subcmd not in ALLOWED_BENCH_SUBCOMMANDS:
                                return False, f"Bench subcommand '{real_subcmd}' is not allowed."
                    elif subcmd not in ALLOWED_BENCH_SUBCOMMANDS:
                         return False, f"Bench subcommand '{subcmd}' is not allowed."
        
        return True, "Valid Command"
        
    except Exception as e:
        return False, f"Command validation error: {str(e)}"

def write_file(content, destination_path, bench_doc):
    """
    Write content to a file safely. Supports local and remote benches.
    """
    try:
        is_remote = False
        if bench_doc:
            if hasattr(bench_doc, 'server') and bench_doc.server:
                try:
                    server_doc = frappe.get_doc("HT Server", bench_doc.server)
                    is_local_server = server_doc.hostname in ["localhost", "127.0.0.1", "::1", "local"]
                    is_remote = not is_local_server
                except Exception:
                    is_remote = bench_doc.is_remote
            elif hasattr(bench_doc, 'is_remote'):
                is_remote = bench_doc.is_remote
        
        if is_remote:
            # Create a temp file locally first
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp_file:
                tmp_file.write(content)
                tmp_path = tmp_file.name
                
            try:
                # Use Fabric to upload
                # We need credentials logic duplicated from execute_remote_command or refactored
                # For brevity, I will refactor get_connection
                c = get_connection(bench_doc)
                c.put(tmp_path, destination_path)
                return True, "File uploaded successfully"
            finally:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
        else:
            # Local write
            # Check permissions/path safety? For now assume root is okay or bench user is okay.
            with open(destination_path, 'w') as f:
                f.write(content)
            return True, "File written successfully"
            
    except Exception as e:
        frappe.log_error(f"Write File Error: {str(e)}", "SSH File Writer")
        return False, str(e)

def get_connection(bench_doc):
    """
    Helper to get fabric connection
    """
    hostname = getattr(bench_doc, 'hostname', None)
    username = getattr(bench_doc, 'username', None)
    ssh_key_path = getattr(bench_doc, 'ssh_key_path', None)
    password = None
    
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
        
    return Connection(
        host=hostname,
        user=username,
        port=bench_doc.port or 22,
        connect_kwargs=connect_kwargs
    )

def execute_command(command, bench_doc=None, cwd=None, task_id=None, display_command=None, env=None, user=None, site=None):
    """
    Execute command either locally or remotely based on bench_doc configuration.
    Streams output to frontend if task_id is provided.
    'env' is a dictionary of environment variables to set.
    """
    if isinstance(command, list):
        command = " ".join(command)
        
    # Validate Command
    is_valid, reason = validate_command(command)
    if not is_valid:
        frappe.log_error(f"Blocked Command: {command} Reason: {reason}", "Security Audit")
        if task_id:
             log_stream(task_id, f"Security Block: {reason}", error=True)
        return False, f"Security Block: {reason}"
    
    # Capture user and site for background threads/tasks if not provided
    if not user:
        user = frappe.session.user if (frappe.session and hasattr(frappe.session, 'user')) else "Administrator"
    if not site:
        site = frappe.local.site if hasattr(frappe.local, 'site') else None
    
    log_cmd = display_command if display_command else command
    log_stream(task_id, f"Executing: {log_cmd}", user=user, site=site)
    
    is_remote = False
    if bench_doc:
        if hasattr(bench_doc, 'server') and bench_doc.server:
            # Check Linked Server
            try:
                server_doc = frappe.get_doc("HT Server", bench_doc.server)
                is_local_server = server_doc.hostname in ["localhost", "127.0.0.1", "::1", "local"]
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

        # Determine credentials - Refactored into get_connection but kept here for now for minimal change flow?
        # Actually I should use get_connection here too to be clean.
        c = get_connection(bench_doc)
        
        # We need password for watchers
        password = None
        if bench_doc.server:
             server_doc = frappe.get_doc("HT Server", bench_doc.server)
             password = server_doc.get_password('password')
        elif getattr(bench_doc, 'password', None):
             password = bench_doc.get_password('password')
        
        log_cmd = display_command if display_command else command
        frappe.log_error(f"Executing Remote: {log_cmd} in {cwd}", "SSH Executor")
        log_stream(task_id, f"Connected to {c.host}", user=user, site=site)
        
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
        
        # Also store in cache for API polling
        try:
            cache_key = f"htbench_logs::{task_id}"
            logs = frappe.cache().get_value(cache_key) or []
            logs.append({
                "log": message,
                "error": error,
                "timestamp": frappe.utils.now()
            })
            frappe.cache().set_value(cache_key, logs, expires_in_sec=3600)
            
            # If task complete/error, maybe set status? but logs are enough for now.
        except Exception:
            pass
