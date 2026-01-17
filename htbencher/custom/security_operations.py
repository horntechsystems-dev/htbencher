
import frappe
import socket
import ssl
import datetime

import os
import subprocess

def run_security_scan(bench_path):
    """
    Run comprehensive security scan on bench
    """
    results = {}
    
    if not os.path.exists(bench_path):
        return {"error": f"Path {bench_path} not found"}

    # Check directory permissions (sites directory)
    sites_path = os.path.join(bench_path, "sites")
    if os.path.exists(sites_path):
        mode = oct(os.stat(sites_path).st_mode & 0o777)
        results["sites_dir_perms"] = mode
        results["sites_security"] = "PASS" if mode == '0o755' or mode == '0o711' else "INFO"

    # Check firewall (local check logic)
    try:
        # systemctl is-active is safer than sudo ufw status for automated scripts
        ufw_active = subprocess.run(["systemctl", "is-active", "ufw"], capture_output=True, text=True).stdout.strip()
        results["firewall"] = "Active" if ufw_active == "active" else "Inactive"
    except Exception:
        results["firewall"] = "Unknown"

    # Check fail2ban
    try:
        f2b_active = subprocess.run(["systemctl", "is-active", "fail2ban"], capture_output=True, text=True).stdout.strip()
        results["fail2ban"] = "Active" if f2b_active == "active" else "Inactive"
    except Exception:
        results["fail2ban"] = "Unknown"

    return results

def check_ssl_expiry(domain_name):
    """
    Check SSL certificate expiry
    """
    try:
        context = ssl.create_default_context()
        with socket.create_connection((domain_name, 443)) as sock:
            with context.wrap_socket(sock, server_hostname=domain_name) as ssock:
                cert = ssock.getpeercert()
                not_after = cert['notAfter']
                # parsing date format needed
                # return datetime object
                return not_after
    except Exception as e:
        frappe.log_error(str(e), "SSL Check Failed")
        return None
