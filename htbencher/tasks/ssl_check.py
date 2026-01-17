
import frappe
from htbencher.custom.security_operations import check_ssl_expiry
from htbencher.config.config import DEFAULT_CONFIG

def check_expiry():
    """
    Daily task to check SSL expiry
    """
    frappe.log_error("Starting SSL Check", "SSL Task")
    # Get all domains with SSL
    domains = frappe.get_all("HT Domain", filters={"ssl_status": "Active"}, fields=["name", "domain_name"])
    for d in domains:
        expiry = check_ssl_expiry(d.domain_name)
        if expiry:
            # Update expiry date in Doctype
            try:
                # Convert expiry to date object if needed
                frappe.db.set_value("HT Domain", d.name, "expiry_date", expiry)
                frappe.db.commit()
                
                # Check if expiring soon (e.g. 7 days)
                # If so, and auto_renew is true, renew it.
            except Exception as e:
                frappe.log_error(f"Error updating expiry for {d.domain_name}: {e}", "SSL Task")
