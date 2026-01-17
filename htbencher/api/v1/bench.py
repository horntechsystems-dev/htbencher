
import frappe
from htbencher.custom import bench_operations

@frappe.whitelist()
def create_bench(bench_name, server, python_version="python3.11", frappe_branch="version-15", apps=None):
    if not frappe.has_permission("HT Bench", "create"):
        frappe.throw("Not permitted", frappe.PermissionError)
        
    if not server:
        frappe.throw("Server is required")
        
    task_id = frappe.generate_hash(length=10)
    frappe.enqueue('htbencher.custom.bench_operations.create_bench', 
        queue='long', 
        timeout=3600,
        bench_name=bench_name, 
        server=server,
        python_version=python_version, 
        frappe_branch=frappe_branch, 
        apps=apps,
        task_id=task_id
    )
    return {"task_id": task_id}

@frappe.whitelist()
def clone_bench(source_bench, new_bench_name):
    if not frappe.has_permission("HT Bench", "create"):
        frappe.throw("Not permitted", frappe.PermissionError)
        
    task_id = frappe.generate_hash(length=10)
    frappe.enqueue('htbencher.custom.bench_operations.clone_bench',
        queue='long',
        timeout=3600,
        source_bench=source_bench,
        new_bench_name=new_bench_name,
        task_id=task_id
    )
    return {"task_id": task_id}

@frappe.whitelist()
def update_bench(bench_name):
    task_id = frappe.generate_hash(length=10)
    frappe.enqueue('htbencher.custom.bench_operations.update_bench',
        queue='long',
        timeout=3600,
        bench_name=bench_name,
        task_id=task_id
    )
    return {"task_id": task_id}

@frappe.whitelist()
def build_bench(bench_name):
    task_id = frappe.generate_hash(length=10)
    frappe.enqueue('htbencher.custom.bench_operations.build_bench',
        queue='long',
        timeout=3600,
        bench_name=bench_name,
        task_id=task_id
    )
    return {"task_id": task_id}

@frappe.whitelist()
def get_available_pythons(server=None):
    return bench_operations.get_system_pythons(server=server)

@frappe.whitelist()
def get_app(bench_name, app_name):
    """
    Install an app to a bench
    """
    if not frappe.has_permission("HT Bench", "write"):
        frappe.throw("Not permitted", frappe.PermissionError)
        
    task_id = frappe.generate_hash(length=10)
    frappe.enqueue('htbencher.custom.bench_operations.get_app',
        queue='long',
        timeout=3600,
        bench_name=bench_name,
        app_doc_name=app_name,
        task_id=task_id
    )
    return {"task_id": task_id}
