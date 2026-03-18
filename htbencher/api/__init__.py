import frappe
from frappe import _
from frappe.auth import LoginManager
from frappe.utils.background_jobs import get_queue, get_workers
from frappe.utils.scheduler import is_scheduler_inactive
import psutil

@frappe.whitelist(allow_guest=True)
def login(usr, pwd):
    if not usr or not pwd:
        frappe.throw(_("Username and password are required"), frappe.AuthenticationError)
        
    login_manager = LoginManager()
    try:
        login_manager.authenticate(user=usr, pwd=pwd)
        login_manager.post_login()
    except frappe.AuthenticationError:
        frappe.clear_messages()
        frappe.throw(_("Invalid login credentials"), frappe.AuthenticationError)
    
    return {
        "message": "Logged in",
        "default_route": "/",
        "email": frappe.session.user,
        "full_name": frappe.get_value("User", frappe.session.user, "full_name")
    }

@frappe.whitelist()
def get_system_status():
    return {
        "total_benches": frappe.db.count("HT Bench"),
        "total_sites": frappe.db.count("HT Site"),
        "total_apps": frappe.db.count("HT App"),
        "server_load": psutil.cpu_percent(), # Replaced mock with real CPU load
        "workers_status": "Active" if len(get_workers()) > 0 else "Inactive",
        "scheduler_status": "Inactive" if is_scheduler_inactive() else "Active",
        "redis_status": "Active",
        "queues": {
            "default": {"count": get_queue("default").count},
            "short": {"count": get_queue("short").count},
            "long": {"count": get_queue("long").count}
        }
    }

@frappe.whitelist()
def get_benches():
    return frappe.get_all("HT Bench", fields=["name", "status", "path", "server", "python_version"])

@frappe.whitelist()
def get_apps():
    return frappe.get_all("HT App", fields=["name", "app_name", "repo_url", "branch", "description"])

@frappe.whitelist()
def get_sites():
    return frappe.get_all("HT Site", fields=["name", "site_name", "bench", "status", "full_domain"])

@frappe.whitelist()
def get_jobs():
    return frappe.get_all("HT Job", fields=["name", "method", "status", "creation", "logs"], order_by="creation desc")
