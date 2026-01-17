import frappe
import requests
import json

def create_subdomain(root_domain_name, subdomain, ip_address, record_type="A"):
	"""
	Create a DNS subdomain record using GoDaddy API
	
	Args:
		root_domain_name: Name of the HT Root Domain document
		subdomain: Subdomain name (e.g., 'mysite' for mysite.horntech.cloud)
		ip_address: IP address to point to (for A records)
		record_type: Type of DNS record (A or CNAME)
	
	Returns:
		tuple: (success: bool, message: str)
	"""
	try:
		# Get root domain document
		root_domain = frappe.get_doc("HT Root Domain", root_domain_name)
		
		if not root_domain.is_active:
			return False, f"Root domain {root_domain_name} is not active"
		
		# Prepare API request
		base_url = root_domain.get_api_base_url()
		domain = root_domain.domain_name
		url = f"{base_url}/v1/domains/{domain}/records"
		
		headers = {
			"Authorization": root_domain.get_auth_header(),
			"Content-Type": "application/json"
		}
		
		# Prepare DNS record data
		record_data = [
			{
				"type": record_type,
				"name": subdomain,
				"data": ip_address,
				"ttl": root_domain.default_ttl or 600
			}
		]
		
		# Make API request
		response = requests.patch(url, headers=headers, json=record_data, timeout=30)
		
		if response.status_code == 200:
			full_domain = f"{subdomain}.{domain}"
			frappe.msgprint(f"Successfully created DNS record for {full_domain}")
			return True, f"DNS record created for {full_domain}"
		else:
			error_msg = f"GoDaddy API error: {response.status_code} - {response.text}"
			frappe.log_error(error_msg, "GoDaddy DNS Creation Failed")
			return False, error_msg
			
	except Exception as e:
		error_msg = f"Failed to create subdomain: {str(e)}"
		frappe.log_error(error_msg, "GoDaddy DNS Creation Failed")
		return False, error_msg



def update_subdomain(root_domain_name, subdomain, ip_address, record_type="A"):
	"""
	Update a DNS subdomain record using GoDaddy API
	
	Args:
		root_domain_name: Name of the HT Root Domain document
		subdomain: Subdomain name to update
		ip_address: New IP address
		record_type: Type of DNS record (A or CNAME)
	
	Returns:
		tuple: (success: bool, message: str)
	"""
	try:
		# Get root domain document
		root_domain = frappe.get_doc("HT Root Domain", root_domain_name)
		
		# Prepare API request
		base_url = root_domain.get_api_base_url()
		domain = root_domain.domain_name
		# Using PUT to replace records for this specific name and type
		url = f"{base_url}/v1/domains/{domain}/records/{record_type}/{subdomain}"
		
		headers = {
			"Authorization": root_domain.get_auth_header(),
			"Content-Type": "application/json"
		}
		
		# Prepare DNS record data
		# Note: The API expects a list of records for this PUT endpoint
		record_data = [
			{
				"data": ip_address,
				"ttl": root_domain.default_ttl or 600
			}
		]
		
		# Make API request
		response = requests.put(url, headers=headers, json=record_data, timeout=30)
		
		if response.status_code == 200:
			full_domain = f"{subdomain}.{domain}"
			frappe.msgprint(f"Successfully updated DNS record for {full_domain}")
			return True, f"DNS record updated for {full_domain}"
		else:
			error_msg = f"GoDaddy API error: {response.status_code} - {response.text}"
			frappe.log_error(error_msg, "GoDaddy DNS Update Failed")
			return False, error_msg
			
	except Exception as e:
		error_msg = f"Failed to update subdomain: {str(e)}"
		frappe.log_error(error_msg, "GoDaddy DNS Update Failed")
		return False, error_msg


def delete_subdomain(root_domain_name, subdomain, record_type="A"):
	"""
	Delete a DNS subdomain record using GoDaddy API
	
	Args:
		root_domain_name: Name of the HT Root Domain document
		subdomain: Subdomain name to delete
		record_type: Type of DNS record (A or CNAME)
	
	Returns:
		tuple: (success: bool, message: str)
	"""
	try:
		# Get root domain document
		root_domain = frappe.get_doc("HT Root Domain", root_domain_name)
		
		# Prepare API request
		base_url = root_domain.get_api_base_url()
		domain = root_domain.domain_name
		url = f"{base_url}/v1/domains/{domain}/records/{record_type}/{subdomain}"
		
		headers = {
			"Authorization": root_domain.get_auth_header()
		}
		
		# Make API request
		response = requests.delete(url, headers=headers, timeout=30)
		
		if response.status_code == 204:
			full_domain = f"{subdomain}.{domain}"
			return True, f"DNS record deleted for {full_domain}"
		elif response.status_code == 404:
			# Record already gone, consider success
			return True, "DNS record not found (already deleted)"
		else:
			error_msg = f"GoDaddy API error: {response.status_code} - {response.text}"
			frappe.log_error(error_msg, "GoDaddy DNS Deletion Failed")
			return False, error_msg
			
	except Exception as e:
		error_msg = f"Failed to delete subdomain: {str(e)}"
		frappe.log_error(error_msg, "GoDaddy DNS Deletion Failed")
		return False, error_msg


def get_dns_records(root_domain_name):
	"""
	Get all DNS records for a domain using GoDaddy API
	
	Args:
		root_domain_name: Name of the HT Root Domain document
	
	Returns:
		list: List of DNS records or empty list on error
	"""
	try:
		# Get root domain document
		root_domain = frappe.get_doc("HT Root Domain", root_domain_name)
		
		# Prepare API request
		base_url = root_domain.get_api_base_url()
		domain = root_domain.domain_name
		url = f"{base_url}/v1/domains/{domain}/records"
		
		headers = {
			"Authorization": root_domain.get_auth_header()
		}
		
		# Make API request
		response = requests.get(url, headers=headers, timeout=30)
		
		if response.status_code == 200:
			return response.json()
		else:
			error_msg = f"GoDaddy API error: {response.status_code} - {response.text}"
			frappe.log_error(error_msg, "GoDaddy DNS Fetch Failed")
			return []
			
	except Exception as e:
		frappe.log_error(str(e), "GoDaddy DNS Fetch Failed")
		return []

def check_domain_availability(root_domain_name, domain_to_check):
	"""
	Check if a domain is available for purchase
	
	Args:
		root_domain_name: Name of the HT Root Domain document (to get credentials)
		domain_to_check: Domain name to check availability for
		
	Returns:
		dict: API response or None on error
	"""
	try:
		# Get root domain document for credentials
		root_domain = frappe.get_doc("HT Root Domain", root_domain_name)
		
		# Prepare API request
		base_url = root_domain.get_api_base_url()
		url = f"{base_url}/v1/domains/available"
		
		headers = {
			"Authorization": root_domain.get_auth_header()
		}
		
		params = {
			"domain": domain_to_check,
			"checkType": "FAST", # Use FAST for quicker response
			"forTransfer": False
		}
		
		# Make API request
		response = requests.get(url, headers=headers, params=params, timeout=30)
		
		if response.status_code == 200:
			return response.json()
		else:
			error_msg = f"GoDaddy API error: {response.status_code} - {response.text}"
			frappe.log_error(error_msg, "GoDaddy Availability Check Failed")
			return None
			
	except Exception as e:
		frappe.log_error(str(e), "GoDaddy Availability Check Failed")
		return None
