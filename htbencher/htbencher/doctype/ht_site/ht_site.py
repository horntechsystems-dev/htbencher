import frappe
from frappe.model.document import Document
from htbencher.custom.godaddy_client import create_subdomain, update_subdomain, delete_subdomain

class HTSite(Document):
	def validate(self):
		"""Validate the site document before saving"""
		self.validate_duplicate_apps()
		self.compute_full_domain()
	
	def validate_duplicate_apps(self):
		"""Prevent duplicate apps in installed_apps table"""
		if not self.installed_apps:
			return
		
		seen_apps = set()
		duplicate_apps = []
		
		for app_row in self.installed_apps:
			if app_row.app in seen_apps:
				duplicate_apps.append(app_row.app)
			else:
				seen_apps.add(app_row.app)
		
		if duplicate_apps:
			frappe.throw(
				f"Duplicate apps found in installed apps list: {', '.join(duplicate_apps)}. "
				"Please remove duplicate entries.",
				title="Duplicate Apps Not Allowed"
			)
	
	def compute_full_domain(self):
		"""Compute the full domain name from root domain and subdomain"""
		if self.root_domain and self.subdomain:
			root_domain_doc = frappe.get_doc("HT Root Domain", self.root_domain)
			self.full_domain = f"{self.subdomain}.{root_domain_doc.domain_name}"
		else:
			self.full_domain = None
	
	def after_insert(self):
		"""Create DNS record after site is created"""
		if self.root_domain and self.subdomain and self.server_ip:
			success, message = create_subdomain(
				self.root_domain,
				self.subdomain,
				self.server_ip
			)
			if not success:
				frappe.log_error(
					f"Failed to create DNS record for {self.full_domain}: {message}",
					"DNS Creation Failed"
				)
				frappe.msgprint(
					f"Site created but DNS record creation failed: {message}",
					title="DNS Warning",
					indicator="orange"
				)
	def on_update(self):
		"""Update DNS record if relevant fields change"""
		# Check if we have required fields
		if not (self.root_domain and self.subdomain and self.server_ip):
			return
			
		# Check if this is not a new document (already saved)
		if self.is_new():
			return
			
		doc_before_save = self.get_doc_before_save()
		if not doc_before_save:
			return
			
		# Check if relevant fields changed
		ip_changed = self.server_ip != doc_before_save.server_ip
		subdomain_changed = self.subdomain != doc_before_save.subdomain
		root_domain_changed = self.root_domain != doc_before_save.root_domain
		
		if ip_changed and not subdomain_changed and not root_domain_changed:
			# Simple IP update
			success, message = update_subdomain(
				self.root_domain,
				self.subdomain,
				self.server_ip
			)
			if success:
				frappe.msgprint(f"DNS record updated: {message}")
			else:
				frappe.msgprint(
					f"Failed to update DNS record: {message}",
					title="DNS Update Failed",
					indicator="orange"
				)
				
		elif subdomain_changed or root_domain_changed:
			# Complex change requiring delete + create
			# First delete old record
			if doc_before_save.root_domain and doc_before_save.subdomain:
				delete_subdomain(
					doc_before_save.root_domain,
					doc_before_save.subdomain
				)
			
			# Then create new record
			success, message = create_subdomain(
				self.root_domain,
				self.subdomain,
				self.server_ip
			)
			if success:
				frappe.msgprint(f"DNS record recreated: {message}")
			else:
				frappe.msgprint(
					f"Failed to create new DNS record: {message}",
					title="DNS Creation Failed",
					indicator="orange"
				)

	def on_trash(self):
		"""Delete DNS record when site is deleted"""
		if self.root_domain and self.subdomain:
			success, message = delete_subdomain(
				self.root_domain,
				self.subdomain
			)
			if success:
				frappe.msgprint(f"DNS record deleted: {message}")
			else:
				frappe.msgprint(
					f"Failed to delete DNS record: {message}. You may need to delete it manually.",
					title="DNS Deletion Failed",
					indicator="orange"
				)

