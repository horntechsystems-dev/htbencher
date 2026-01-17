
import frappe
import psutil

def check_health():
    """
    Hourly task to check bench health
    """
    benches = frappe.get_all("HT Bench", filters={"status": "Active"}, fields=["name", "is_remote"])
    
    for bench in benches:
        try:
            # For now, we collect local system metrics as a proxy for bench health
            # In a more advanced setup, we would query the specific bench path or remote server
            cpu = psutil.cpu_percent(interval=1)
            ram = psutil.virtual_memory().percent
            disk = psutil.disk_usage('/').percent
            
            metric = frappe.get_doc({
                "doctype": "HT Bench Metric",
                "bench": bench.name,
                "cpu_percentage": cpu,
                "ram_percentage": ram,
                "disk_percentage": disk
            })
            metric.insert(ignore_permissions=True)
            
        except Exception as e:
            frappe.log_error(f"Failed to collect metrics for {bench.name}: {e}", "Bench Health")
    
    frappe.db.commit()
