
import frappe
from htbencher.custom.security_operations import run_security_scan

def run_monthly_scan():
    """
    Monthly security scan
    """
    benches = frappe.get_all("HT Bench", filters={"status": "Active"})
    for bench in benches:
        # doc = frappe.get_doc("HT Bench", bench.name)
        # res = run_security_scan(doc.path)
        # Create Security Scan Doc
        # new_scan = frappe.new_doc("HT Security Scan")
        pass
