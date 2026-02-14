
import frappe

@frappe.whitelist()
def get_task_status(task_id):
    """
    Retrieve logs and status for a specific task from cache.
    Works for bench, site, and app tasks.
    """
    logs = frappe.cache().get_value(f"htbench_logs::{task_id}")
    status = frappe.cache().get_value(f"htbench_status::{task_id}")
    
    return {
        "logs": logs or [],
        "status": status or "running"
    }
@frappe.whitelist()
def generate_ssh_keypair():
    """
    Generate a new SSH keypair (RSA 4096)
    """
    import subprocess
    import tempfile
    import os
    
    with tempfile.TemporaryDirectory() as tmpdir:
        key_file = os.path.join(tmpdir, "id_rsa")
        # Generate key without passphrase
        subprocess.run([
            "ssh-keygen", "-t", "rsa", "-b", "4096", "-m", "PEM", 
            "-f", key_file, "-N", "", "-q"
        ], check=True)
        
        with open(key_file, "r") as f:
            private_key = f.read()
        with open(key_file + ".pub", "r") as f:
            public_key = f.read()
            
    return {
        "private": private_key,
        "public": public_key
    }
