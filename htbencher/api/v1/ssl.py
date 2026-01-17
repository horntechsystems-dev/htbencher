
import frappe
from htbencher.custom.ssl_operations import map_domain_to_site as _map_domain
from htbencher.custom.ssl_operations import setup_ssl_for_domain as _setup_ssl

@frappe.whitelist()
def map_domain(site_name, domain_name, bench_path):
    if not frappe.has_permission("HT Domain", "create"):
        frappe.throw("Not permitted", frappe.PermissionError)
        
    return _map_domain(site_name, domain_name, bench_path)

@frappe.whitelist()
def setup_ssl(domain_name, bench_path, email=None):
    if not frappe.has_permission("HT Domain", "write"):
        frappe.throw("Not permitted", frappe.PermissionError)
        
    return _setup_ssl(domain_name, bench_path, email)
