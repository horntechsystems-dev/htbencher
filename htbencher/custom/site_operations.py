
import frappe
from htbencher.custom.ssh_utils import execute_command

def create_site(bench_path, site_name, db_password, install_apps=None, task_id=None):
    """
    Create a new site
    """
    try:
        cmd = [
            "bench", "new-site", site_name,
            "--admin-password", "admin", 
            "--db-root-password", db_password 
        ]
        
        # Should resolve bench doc from bench_path or name
        bench_doc = get_bench_doc_from_path(bench_path)
        
        success, output = execute_command(cmd, bench_doc=bench_doc, cwd=bench_path, task_id=task_id)
        
        if not success:
            frappe.log_error(f"Site creation failed for {site_name}: {output}", "Site Creation Failed")
            if task_id:
                frappe.publish_realtime('htbench_task_complete', {
                    'task_id': task_id, 
                    'status': 'failed'
                }, user=frappe.session.user if frappe.session else "Administrator")
            return False

        if install_apps:
            # Deduplicate apps to prevent infinite loops
            seen_apps = set()
            unique_apps = []
            
            for app in install_apps:
                app_name = app.get("app_name") if isinstance(app, dict) else app
                
                # Skip if we've already processed this app
                if app_name in seen_apps:
                    frappe.log_error(
                        f"Duplicate app '{app_name}' found in install list for site {site_name}. Skipping.",
                        "Duplicate App Installation"
                    )
                    continue
                
                seen_apps.add(app_name)
                unique_apps.append(app_name)
            
            # Install each unique app
            for app_name in unique_apps:
                success = install_app_to_site(bench_path, site_name, app_name)
                if not success:
                    frappe.log_error(
                        f"Failed to install app '{app_name}' to site {site_name}",
                        "App Installation Failed"
                    )
        
        if task_id:
            frappe.publish_realtime('htbench_task_complete', {
                'task_id': task_id, 
                'status': 'success'
            }, user=frappe.session.user if frappe.session else "Administrator")
        
        return True
    except Exception as e:
        frappe.log_error(str(e), "Site Creation Failed")
        if task_id:
            frappe.publish_realtime('htbench_task_complete', {
                'task_id': task_id, 
                'status': 'failed'
            }, user=frappe.session.user if frappe.session else "Administrator")
        return False

def install_app_to_site(bench_path, site_name, app_doc_name):
    """
    Install app to site
    """
    try:
        # Check if site document exists and if app is already installed
        site_doc = frappe.db.get_value("HT Site", {"site_name": site_name}, "name")
        if site_doc:
            existing_apps = frappe.db.get_all(
                "HT Site App",
                filters={"parent": site_doc, "app": app_doc_name},
                fields=["app"]
            )
            if existing_apps:
                frappe.msgprint(f"App '{app_doc_name}' is already installed on site {site_name}. Skipping.")
                return True
        
        app_doc = frappe.get_doc("HT App", app_doc_name)
        package_name = app_doc.app_name 
        
        cmd = ["bench", "--site", site_name, "install-app", package_name]
        
        bench_doc = get_bench_doc_from_path(bench_path)
        success, output = execute_command(cmd, bench_doc=bench_doc, cwd=bench_path)
        
        if not success:
            frappe.log_error(
                f"Failed to install app '{app_doc_name}' (package: {package_name}) to site {site_name}: {output}",
                "App Install Failed"
            )
        
        return success
    except Exception as e:
        frappe.log_error(str(e), "App Install Failed")
        return False

def get_bench_doc_from_path(path):
    # Helper to find bench doc by path
    name = frappe.db.get_value("HT Bench", {"path": path}, "name")
    if name:
        return frappe.get_doc("HT Bench", name)
    return None

def migrate_all_sites(bench_name, skip_failing=0, task_id=None):
    """
    Run migrate on all sites in a bench
    """
    try:
        bench_doc = frappe.get_doc("HT Bench", bench_name)
        
        cmd = ["bench", "migrate"]
        if skip_failing:
            cmd.append("--skip-failing")
        
        success, output = execute_command(cmd, bench_doc=bench_doc, cwd=bench_doc.path, task_id=task_id)
        
        frappe.publish_realtime('htbench_task_complete', {
            'task_id': task_id, 
            'status': 'success' if success else 'failed'
        }, user=frappe.session.user if frappe.session else "Administrator")
        
        return success
    except Exception as e:
        frappe.log_error(str(e), "Migration Failed")
        frappe.publish_realtime('htbench_task_complete', {
            'task_id': task_id, 
            'status': 'failed'
        }, user=frappe.session.user if frappe.session else "Administrator")
        return False

def backup_all_sites(bench_name, with_files=1, task_id=None):
    """
    Backup all sites in a bench
    """
    try:
        bench_doc = frappe.get_doc("HT Bench", bench_name)
        
        cmd = ["bench", "backup", "--all"]
        if with_files:
            cmd.append("--with-files")
        
        success, output = execute_command(cmd, bench_doc=bench_doc, cwd=bench_doc.path, task_id=task_id)
        
        frappe.publish_realtime('htbench_task_complete', {
            'task_id': task_id, 
            'status': 'success' if success else 'failed'
        }, user=frappe.session.user if frappe.session else "Administrator")
        
        return success
    except Exception as e:
        frappe.log_error(str(e), "Backup Failed")
        frappe.publish_realtime('htbench_task_complete', {
            'task_id': task_id, 
            'status': 'failed'
        }, user=frappe.session.user if frappe.session else "Administrator")
        return False
