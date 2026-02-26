
import frappe
from htbencher.custom import site_operations

@frappe.whitelist()
def create_site(bench_name, site_name, admin_password, db_password, root_domain=None, subdomain=None, server_ip=None):
    if not frappe.has_permission("HT Site", "create"):
        frappe.throw("Not permitted", frappe.PermissionError)
    
    # Get bench document to retrieve the path
    bench_doc = frappe.get_doc("HT Bench", bench_name)
    if not bench_doc:
        frappe.throw(f"Bench {bench_name} not found")
    
    # Create HT Site document
    site_doc = frappe.get_doc({
        "doctype": "HT Site",
        "site_name": site_name,
        "bench": bench_name,
        "db_password": db_password,
        "root_domain": root_domain if root_domain else None,
        "subdomain": subdomain if subdomain else None,
        "server_ip": server_ip if server_ip else None
    })
    site_doc.insert()
    frappe.db.commit()
        
    task_id = frappe.generate_hash(length=10)
    frappe.enqueue('htbencher.custom.site_operations.create_site',
        queue='long',
        timeout=3600,
        bench_path=bench_doc.path,
        site_name=site_name,
        db_password=db_password,
        task_id=task_id,
        user=frappe.session.user
    )
    return {"task_id": task_id}

@frappe.whitelist()
def migrate_sites(bench_name, skip_failing=0):
    task_id = frappe.generate_hash(length=10)
    frappe.enqueue('htbencher.custom.site_operations.migrate_all_sites',
        queue='long',
        timeout=3600,
        bench_name=bench_name,
        skip_failing=skip_failing,
        task_id=task_id
    )
    return {"task_id": task_id}

@frappe.whitelist()
def backup_sites(bench_name, with_files=1):
    task_id = frappe.generate_hash(length=10)
    frappe.enqueue('htbencher.custom.site_operations.backup_all_sites',
        queue='long',
        timeout=3600,
        bench_name=bench_name,
        with_files=with_files,
        task_id=task_id
    )
    return {"task_id": task_id}

@frappe.whitelist()
def get_task_status(task_id):
    """
    Retrieve logs and status for a specific task from cache.
    """
    logs = frappe.cache().get_value(f"htbench_logs::{task_id}")
    status = frappe.cache().get_value(f"htbench_status::{task_id}")
    
    return {
        "logs": logs or [],
        "status": status or "running"
    }
@frappe.whitelist()
def get_sites(bench_name=None):
    """
    List all sites, optionally filtered by bench
    """
    filters = {}
    if bench_name and bench_name != "null":
        filters["bench"] = bench_name
    return frappe.get_all("HT Site", filters=filters, fields=["name", "site_name", "bench", "root_domain", "subdomain"])

@frappe.whitelist()
def install_app(site_name, app_name):
    """
    Install an app to a site
    """
    if not frappe.has_permission("HT Site", "write"):
        frappe.throw("Not permitted", frappe.PermissionError)
        
    site_doc = frappe.get_doc("HT Site", site_name)
    bench_doc = frappe.get_doc("HT Bench", site_doc.bench)
    
    task_id = frappe.generate_hash(length=10)
    frappe.enqueue('htbencher.custom.site_operations.install_app_to_site',
        queue='long',
        timeout=3600,
        bench_path=bench_doc.path,
        site_name=site_doc.site_name,
        app_name=app_name,
        task_id=task_id
    )
    return {"task_id": task_id}

@frappe.whitelist()
def uninstall_app(site_name, app_name):
    """
    Uninstall an app from a site
    """
    if not frappe.has_permission("HT Site", "write"):
        frappe.throw("Not permitted", frappe.PermissionError)
        
    site_doc = frappe.get_doc("HT Site", site_name)
    bench_doc = frappe.get_doc("HT Bench", site_doc.bench)
    
    task_id = frappe.generate_hash(length=10)
    frappe.enqueue('htbencher.custom.site_operations.uninstall_app_from_site',
        queue='long',
        timeout=3600,
        bench_path=bench_doc.path,
        site_name=site_doc.site_name,
        app_name=app_name,
        task_id=task_id
    )
    return {"task_id": task_id}

@frappe.whitelist()
def get_installed_apps(site_name):
    """
    Get list of apps installed on a site
    """
    site_doc = frappe.get_doc("HT Site", site_name)
    bench_doc = frappe.get_doc("HT Bench", site_doc.bench)
    return site_operations.get_site_installed_apps(bench_doc.path, site_doc.site_name)
