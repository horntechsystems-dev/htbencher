import frappe
from frappe.model.document import Document
import requests

class HTRootDomain(Document):
	def validate(self):
		"""Validate the root domain document before saving"""
		self.validate_godaddy_credentials()
		# Optionally test connection on first save
		if self.is_new() and self.godaddy_api_key and self.godaddy_api_secret:
			self.test_connection_on_save()
	
	def validate_godaddy_credentials(self):
		"""Validate that GoDaddy API credentials are provided"""
		if not self.godaddy_api_key:
			frappe.throw("GoDaddy API Key is required")
		
		if not self.godaddy_api_secret:
			frappe.throw("GoDaddy API Secret is required")
	
	def test_connection_on_save(self):
		"""Test API connection when saving for the first time"""
		try:
			base_url = self.get_api_base_url()
			url = f"{base_url}/v1/domains/{self.domain_name}"
			
			headers = {
				"Authorization": self.get_auth_header()
			}
			
			response = requests.get(url, headers=headers, timeout=5)
			
			if response.status_code == 401:
				frappe.throw("Invalid GoDaddy API credentials. Please check your API Key and Secret.")
			elif response.status_code == 403:
				frappe.msgprint(
					f"Warning: Access denied to domain '{self.domain_name}'. "
					"The API key may not have permission to manage this domain. "
					"Please ensure the domain is in the same GoDaddy account as the API key.",
					title="Access Denied",
					indicator="orange"
				)
			elif response.status_code == 404:
				frappe.msgprint(
					f"Warning: Domain '{self.domain_name}' not found in your GoDaddy account. "
					"Please ensure the domain is managed by this GoDaddy account.",
					title="Domain Not Found",
					indicator="orange"
				)
		except requests.exceptions.Timeout:
			frappe.msgprint(
				"Could not verify API credentials due to timeout. You can test the connection later.",
				title="Connection Timeout",
				indicator="orange"
			)
		except Exception as e:
			frappe.log_error(str(e), "GoDaddy API Test Failed")
	
	def get_auth_header(self):
		"""Get the authorization header for GoDaddy API"""
		api_key = self.get_password("godaddy_api_key")
		api_secret = self.get_password("godaddy_api_secret")
		return f"sso-key {api_key}:{api_secret}"
	
	def get_api_base_url(self):
		"""Get the base URL for GoDaddy API based on environment"""
		if self.api_environment == "OTE":
			return "https://api.ote-godaddy.com"
		return "https://api.godaddy.com"

	@frappe.whitelist()
	def check_availability(self):
		"""Check if this domain is available/valid"""
		from htbencher.custom.godaddy_client import check_domain_availability
		
		result = check_domain_availability(self.name, self.domain_name)
		if result:
			if result.get('available'):
				frappe.msgprint(f"Domain {self.domain_name} is available for purchase!")
			else:
				frappe.msgprint(f"Domain {self.domain_name} is NOT available.")
			return result
		return None
