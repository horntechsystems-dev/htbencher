import frappe
import requests

@frappe.whitelist()
def test_godaddy_connection(root_domain_name):
	"""
	Test GoDaddy API connection by fetching domain information
	
	Args:
		root_domain_name: Name of the HT Root Domain document
	
	Returns:
		dict: {success: bool, message: str, details: dict}
	"""
	try:
		# Get root domain document
		root_domain = frappe.get_doc("HT Root Domain", root_domain_name)
		
		# Prepare API request to get domain info
		base_url = root_domain.get_api_base_url()
		domain = root_domain.domain_name
		url = f"{base_url}/v1/domains/{domain}"
		
		headers = {
			"Authorization": root_domain.get_auth_header()
		}
		
		# Make API request
		response = requests.get(url, headers=headers, timeout=10)
		
		if response.status_code == 200:
			domain_info = response.json()
			return {
				"success": True,
				"message": f"✓ Successfully connected to GoDaddy API!\n\nDomain: {domain}\nStatus: {domain_info.get('status', 'N/A')}\nExpires: {domain_info.get('expires', 'N/A')}",
				"details": domain_info
			}
		elif response.status_code == 401:
			return {
				"success": False,
				"message": "✗ Authentication failed. Please check your API Key and Secret.",
				"details": {"status_code": response.status_code}
			}
		elif response.status_code == 403:
			return {
				"success": False,
				"message": (
					f"✗ Access Denied to domain '{domain}'\n\n"
					"Possible causes:\n"
					"1. The domain is not in the same GoDaddy account as the API key\n"
					"2. The API key doesn't have permission to manage this domain\n"
					"3. The domain is in a sub-account or delegated account\n\n"
					"Solutions:\n"
					"• Verify the domain is in the same GoDaddy account where you created the API key\n"
					"• Create a new API key in the account that owns this domain\n"
					"• Check if the domain is delegated to another account"
				),
				"details": {"status_code": response.status_code, "response": response.text}
			}
		elif response.status_code == 404:
			return {
				"success": False,
				"message": f"✗ Domain '{domain}' not found in your GoDaddy account.",
				"details": {"status_code": response.status_code}
			}
		else:
			return {
				"success": False,
				"message": f"✗ API Error: {response.status_code}\n{response.text}",
				"details": {"status_code": response.status_code, "response": response.text}
			}
			
	except requests.exceptions.Timeout:
		return {
			"success": False,
			"message": "✗ Connection timeout. Please check your internet connection.",
			"details": {}
		}
	except requests.exceptions.RequestException as e:
		return {
			"success": False,
			"message": f"✗ Network error: {str(e)}",
			"details": {}
		}
	except Exception as e:
		frappe.log_error(str(e), "GoDaddy Connection Test Failed")
		return {
			"success": False,
			"message": f"✗ Error: {str(e)}",
			"details": {}
		}


@frappe.whitelist()
def run_diagnostics(root_domain_name):
	"""
	Run comprehensive diagnostics on GoDaddy API connection
	
	Args:
		root_domain_name: Name of the HT Root Domain document
	
	Returns:
		dict: Detailed diagnostic information
	"""
	try:
		root_domain = frappe.get_doc("HT Root Domain", root_domain_name)
		base_url = root_domain.get_api_base_url()
		headers = {"Authorization": root_domain.get_auth_header()}
		
		diagnostics = {
			"success": True,
			"checks": [],
			"summary": ""
		}
		
		# Check 1: API Key Format
		api_key = root_domain.get_password("godaddy_api_key")

		api_secret = root_domain.get_password("godaddy_api_secret")
		
		if api_key and api_secret:
			diagnostics["checks"].append({
				"name": "API Credentials Format",
				"status": "✓ Pass",
				"details": f"API Key length: {len(api_key)} chars, Secret length: {len(api_secret)} chars"
			})
		else:
			diagnostics["checks"].append({
				"name": "API Credentials Format",
				"status": "✗ Fail",
				"details": "Missing API key or secret"
			})
			diagnostics["success"] = False
		
		# Check 2: API Endpoint Reachability
		try:
			response = requests.get(f"{base_url}/v1/domains", headers=headers, timeout=10)
			if response.status_code in [200, 401, 403]:
				diagnostics["checks"].append({
					"name": "API Endpoint Reachability",
					"status": "✓ Pass",
					"details": f"GoDaddy API is reachable (Status: {response.status_code})"
				})
			else:
				diagnostics["checks"].append({
					"name": "API Endpoint Reachability",
					"status": "⚠ Warning",
					"details": f"Unexpected status code: {response.status_code}"
				})
		except Exception as e:
			diagnostics["checks"].append({
				"name": "API Endpoint Reachability",
				"status": "✗ Fail",
				"details": f"Cannot reach GoDaddy API: {str(e)}"
			})
			diagnostics["success"] = False
		
		# Check 3: List All Domains (to verify account access)
		try:
			response = requests.get(f"{base_url}/v1/domains", headers=headers, timeout=10)
			if response.status_code == 200:
				domains = response.json()
				domain_names = [d.get("domain", "Unknown") for d in domains[:10]]  # First 10
				diagnostics["checks"].append({
					"name": "Account Domain Access",
					"status": "✓ Pass",
					"details": f"Found {len(domains)} domain(s) in account. First 10: {', '.join(domain_names)}"
				})
				diagnostics["available_domains"] = domain_names
			elif response.status_code == 401:
				diagnostics["checks"].append({
					"name": "Account Domain Access",
					"status": "✗ Fail",
					"details": "Authentication failed - Invalid API credentials"
				})
				diagnostics["success"] = False
			elif response.status_code == 403:
				diagnostics["checks"].append({
					"name": "Account Domain Access",
					"status": "✗ Fail",
					"details": f"Access denied - API key lacks permissions. Response: {response.text}"
				})
				diagnostics["success"] = False
			else:
				diagnostics["checks"].append({
					"name": "Account Domain Access",
					"status": "⚠ Warning",
					"details": f"Unexpected response: {response.status_code}"
				})
		except Exception as e:
			diagnostics["checks"].append({
				"name": "Account Domain Access",
				"status": "✗ Fail",
				"details": f"Error: {str(e)}"
			})
		
		# Check 4: Specific Domain Access
		domain = root_domain.domain_name
		try:
			response = requests.get(f"{base_url}/v1/domains/{domain}", headers=headers, timeout=10)
			if response.status_code == 200:
				domain_info = response.json()
				diagnostics["checks"].append({
					"name": f"Domain '{domain}' Access",
					"status": "✓ Pass",
					"details": f"Domain found. Status: {domain_info.get('status', 'N/A')}, Expires: {domain_info.get('expires', 'N/A')}"
				})
			elif response.status_code == 403:
				diagnostics["checks"].append({
					"name": f"Domain '{domain}' Access",
					"status": "✗ Fail",
					"details": f"Access denied - Domain not in this account or insufficient permissions. Response: {response.text}"
				})
				diagnostics["success"] = False
			elif response.status_code == 404:
				diagnostics["checks"].append({
					"name": f"Domain '{domain}' Access",
					"status": "✗ Fail",
					"details": "Domain not found in this GoDaddy account"
				})
				diagnostics["success"] = False
			else:
				diagnostics["checks"].append({
					"name": f"Domain '{domain}' Access",
					"status": "⚠ Warning",
					"details": f"Unexpected status: {response.status_code}"
				})
		except Exception as e:
			diagnostics["checks"].append({
				"name": f"Domain '{domain}' Access",
				"status": "✗ Fail",
				"details": f"Error: {str(e)}"
			})
		
		# Check 5: DNS Records Access
		try:
			response = requests.get(f"{base_url}/v1/domains/{domain}/records", headers=headers, timeout=10)
			if response.status_code == 200:
				records = response.json()
				diagnostics["checks"].append({
					"name": "DNS Records Access",
					"status": "✓ Pass",
					"details": f"Can read DNS records. Found {len(records)} record(s)"
				})
			elif response.status_code == 403:
				diagnostics["checks"].append({
					"name": "DNS Records Access",
					"status": "✗ Fail",
					"details": f"Cannot access DNS records - Insufficient permissions. Response: {response.text}"
				})
				diagnostics["success"] = False
			else:
				diagnostics["checks"].append({
					"name": "DNS Records Access",
					"status": "⚠ Warning",
					"details": f"Status: {response.status_code}"
				})
		except Exception as e:
			diagnostics["checks"].append({
				"name": "DNS Records Access",
				"status": "⚠ Warning",
				"details": f"Could not check DNS access: {str(e)}"
			})
		
		# Generate summary
		passed = sum(1 for c in diagnostics["checks"] if c["status"].startswith("✓"))
		failed = sum(1 for c in diagnostics["checks"] if c["status"].startswith("✗"))
		warnings = sum(1 for c in diagnostics["checks"] if c["status"].startswith("⚠"))
		
		if diagnostics["success"]:
			diagnostics["summary"] = f"✓ All critical checks passed! ({passed} passed, {warnings} warnings)"
		else:
			diagnostics["summary"] = f"✗ Diagnostics failed ({failed} failed, {passed} passed, {warnings} warnings)"
		
		return diagnostics
		
	except Exception as e:
		frappe.log_error(str(e), "GoDaddy Diagnostics Failed")
		return {
			"success": False,
			"checks": [],
			"summary": f"✗ Diagnostic error: {str(e)}"
		}


@frappe.whitelist()
def list_available_domains(root_domain_name):
	"""
	List all domains available in the GoDaddy account
	
	Args:
		root_domain_name: Name of the HT Root Domain document
	
	Returns:
		dict: List of domains in the account
	"""
	try:
		root_domain = frappe.get_doc("HT Root Domain", root_domain_name)
		base_url = root_domain.get_api_base_url()
		headers = {"Authorization": root_domain.get_auth_header()}
		
		response = requests.get(f"{base_url}/v1/domains", headers=headers, timeout=10)
		
		if response.status_code == 200:
			domains = response.json()
			return {
				"success": True,
				"count": len(domains),
				"domains": [
					{
						"domain": d.get("domain"),
						"status": d.get("status"),
						"expires": d.get("expires"),
						"renewable": d.get("renewable", False)
					}
					for d in domains
				]
			}
		else:
			return {
				"success": False,
				"message": f"Failed to list domains: {response.status_code}",
				"details": response.text
			}
			
	except Exception as e:
		frappe.log_error(str(e), "List Domains Failed")
		return {
			"success": False,
			"message": f"Error: {str(e)}"
		}
