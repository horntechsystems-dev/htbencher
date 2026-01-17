
import frappe
from htbencher.custom.ssh_utils import execute_command
from htbencher.custom.site_operations import get_bench_doc_from_path

def map_domain_to_site(bench_path, site_name, domain_name):
    """
    Map a domain to a site
    """
    try:
        cmd = ["bench", "setup", "add-domain", domain_name, "--site", site_name]
        
        bench_doc = get_bench_doc_from_path(bench_path)
        success, output = execute_command(cmd, bench_doc=bench_doc, cwd=bench_path)
        
        if success:
             # Also need to reload nginx usually
             cmd_nginx = ["bench", "setup", "nginx"]
             execute_command(cmd_nginx, bench_doc=bench_doc, cwd=bench_path)
             
             cmd_reload = ["sudo", "service", "nginx", "reload"]
             # This requires sudo access which might be tricky via fabric without pty=True or sudo password
             # For now, let's assume passwordless sudo or handled by user config
             execute_command(cmd_reload, bench_doc=bench_doc, cwd=bench_path)

        return success
    except Exception as e:
        frappe.log_error(str(e), "Domain Mapping Failed")
        return False

def setup_ssl_for_domain(bench_path, site_name, domain_name):
    """
    Setup SSL for domain
    """
    try:
        cmd = ["sudo", "certbot", "--nginx", "-d", domain_name]
        # This is interactive usually! 'bench setup lets-encrypt' is better wrapper
        
        cmd = ["bench", "setup", "lets-encrypt", site_name, "--custom-domain", domain_name]
        
        bench_doc = get_bench_doc_from_path(bench_path)
        success, output = execute_command(cmd, bench_doc=bench_doc, cwd=bench_path)
        
        return success
    except Exception as e:
        frappe.log_error(str(e), "SSL Setup Failed")
        return False
