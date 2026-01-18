
import frappe
from frappe.model.document import Document
from htbencher.custom.godaddy_client import create_subdomain, update_subdomain, delete_subdomain

class HTSite(Document):
	def validate(self):
		"""Validate the site document before saving"""
		self.apply_domain_logic()
		self.validate_duplicate_apps()
		self.compute_full_domain()
	
	def apply_domain_logic(self):
		"""
		Apply critical domain logic:
		- Root domains (e.g. valid root) -> app.root
		- Subdomains -> kept as is
		"""
		if not self.subdomain or self.subdomain.strip() in ['@', '', '.']:
			self.subdomain = "app"
			
		# Clean subdomain
		self.subdomain = self.subdomain.strip().lower()
	
	def validate_duplicate_apps(self):
		"""Prevent duplicate apps in installed_apps table"""
		if not self.installed_apps:
			return
		
		seen_apps = set()
		for app_row in self.installed_apps:
			if app_row.app in seen_apps:
				frappe.throw(f"Duplicate app found: {app_row.app}")
			seen_apps.add(app_row.app)
	
	def compute_full_domain(self):
		"""Compute the full domain name from root domain and subdomain"""
		if self.root_domain:
			root_domain_doc = frappe.get_doc("HT Root Domain", self.root_domain)
			# Ensure we don't have double dots
			if self.subdomain:
				self.full_domain = f"{self.subdomain}.{root_domain_doc.domain_name}"
			else:
				# Should not happen due to apply_domain_logic
				self.full_domain = f"app.{root_domain_doc.domain_name}"
		else:
			# Fallback if no root domain selected (manual entry?)
			# For now, require root_domain as per schema
			pass
	
	def after_insert(self):
		"""Create DNS record and Trigger Site Creation"""
		# DNS Handling
		if self.root_domain and self.subdomain and self.server_ip:
			create_subdomain(self.root_domain, self.subdomain, self.server_ip)
			
		# Trigger Background Site Creation
		frappe.enqueue(
			"htbencher.htbencher.doctype.ht_site.ht_site.create_site_background",
			queue="long",
			timeout=4000,
			site_name=self.name
		)
		frappe.msgprint(f"Site creation started for {self.full_domain}. Check background jobs.")

	def on_trash(self):
		"""Drop site and DNS"""
		if self.root_domain and self.subdomain:
			delete_subdomain(self.root_domain, self.subdomain)
			
		# Trigger drop-site
		frappe.enqueue(
			"htbencher.htbencher.doctype.ht_site.ht_site.drop_site_background",
			queue="long",
			site_name=self.name, # Passing name to fetch, oh wait, doc is gone.
			# We must pass params directly
			bench_name=self.bench,
			full_domain=self.full_domain
		)

	@frappe.whitelist()
	def install_app_on_site(self, app_name):
		"""Install an app on this site"""
		frappe.enqueue(
			"htbencher.htbencher.doctype.ht_site.ht_site.install_app_site_background",
			queue="long",
			site_name=self.name,
			app_name=app_name
		)
		frappe.msgprint(f"Installing {app_name} on {self.full_domain}...")

	@frappe.whitelist()
	def migrate_site(self):
		frappe.enqueue(
			"htbencher.htbencher.doctype.ht_site.ht_site.migrate_site_background",
			queue="long",
			site_name=self.name
		)
		frappe.msgprint(f"Migrating {self.full_domain}...")

	@frappe.whitelist()
	def backup_site(self):
		frappe.enqueue(
			"htbencher.htbencher.doctype.ht_site.ht_site.backup_site_background",
			queue="long",
			site_name=self.name
		)
		frappe.msgprint(f"Backing up {self.full_domain}...")

# --------------------------------------------------------------------------------
# Background Jobs
# --------------------------------------------------------------------------------

def create_site_background(site_name):
	try:
		doc = frappe.get_doc("HT Site", site_name)
		bench_doc = frappe.get_doc("HT Bench", doc.bench)
		from htbencher.custom.ssh_utils import execute_command
		
		# 1. Bench New Site
		cmd = ["bench", "new-site", doc.full_domain]
		if doc.db_password:
			cmd.extend(["--admin-password", doc.db_password])
			# We assume system is configured so we don't need --mariadb-root-password
			# If needed, it should be in bench config
		
		cmd.extend(["--no-mariadb-socket"]) # often helps
		
		success, output = execute_command(cmd, bench_doc=bench_doc, cwd=bench_doc.path, task_id=f"create_site_{site_name}")
		if not success:
			frappe.log_error(f"Failed to create site {doc.full_domain}: {output}", "Site Creation Failed")
			doc.status = "Inactive"
			doc.save()
			return


		# 2. Setup Nginx
		execute_command("bench setup nginx", bench_doc=bench_doc, cwd=bench_doc.path)
		
		# 3. Reload Nginx
		# We attempt reload. If user is not sudoer, this might fail, but necessary for automation.
		success_reload, output_reload = execute_command("sudo service nginx reload", bench_doc=bench_doc, cwd=bench_doc.path)
		if not success_reload:
			frappe.log_error(f"Nginx reload failed: {output_reload}", "Site Creation Warning")
			# We don't fail the site creation for this, but warn.

		# 4. Lets Encrypt
		# Automatically issue SSL
		# bench setup lets-encrypt [site] --custom-domain [full_domain]
		# This requires the DNS to be propagated!
		# Since we just created DNS in after_insert, it might not be ready.
		# But 'bench setup lets-encrypt' uses certbot which verifies usage.
		# We might need to retry or warn?
		# For now, we try it.
		
		ssl_cmd = ["bench", "setup", "lets-encrypt", doc.full_domain]
		
		# Custom domain argument if needed, but doc.full_domain IS the site name usually if created as such.
		# If user created site as 'app', we definitely need --custom-domain if accessing via app.domain
		# But our logic sets site name = full_domain.
		# So 'bench setup lets-encrypt full_domain' is correct.
		
		success_ssl, output_ssl = execute_command(ssl_cmd, bench_doc=bench_doc, cwd=bench_doc.path)
		if not success_ssl:
			frappe.log_error(f"SSL Setup failed: {output_ssl}", "SSL Warning")
		
		doc.status = "Active"
		doc.save()
		frappe.publish_realtime("htops_site_created", {"site": doc.name})
		
	except Exception as e:
		frappe.log_error(str(e), "Site Creation Error")

def drop_site_background(bench_name, full_domain):
	try:
		bench_doc = frappe.get_doc("HT Bench", bench_name)
		from htbencher.custom.ssh_utils import execute_command
		
		# Force drop
		cmd = f"bench drop-site {full_domain} --force --no-backup"
		execute_command(cmd, bench_doc=bench_doc, cwd=bench_doc.path, task_id=f"drop_site_{full_domain}")
		
	except Exception as e:
		frappe.log_error(str(e), "Site Drop Error")

def install_app_site_background(site_name, app_name):
	try:
		doc = frappe.get_doc("HT Site", site_name)
		bench_doc = frappe.get_doc("HT Bench", doc.bench)
		from htbencher.custom.ssh_utils import execute_command
		
		cmd = ["bench", "--site", doc.full_domain, "install-app", app_name]
		success, output = execute_command(cmd, bench_doc=bench_doc, cwd=bench_doc.path, task_id=f"install_app_{site_name}")
		
		if success:
			# Auto Migrate and Restart
			execute_command(["bench", "--site", doc.full_domain, "migrate"], bench_doc=bench_doc, cwd=bench_doc.path)
			# Restart Bench? 'bench restart'
			execute_command("bench restart", bench_doc=bench_doc, cwd=bench_doc.path)
			
	except Exception as e:
		frappe.log_error(str(e), "App Install Error")

def migrate_site_background(site_name):
	try:
		doc = frappe.get_doc("HT Site", site_name)
		bench_doc = frappe.get_doc("HT Bench", doc.bench)
		from htbencher.custom.ssh_utils import execute_command
		
		execute_command(["bench", "--site", doc.full_domain, "migrate"], bench_doc=bench_doc, cwd=bench_doc.path, task_id=f"migrate_{site_name}")
	except Exception as e:
		frappe.log_error(str(e), "Site Migrate Error")
		
def backup_site_background(site_name):
	try:
		doc = frappe.get_doc("HT Site", site_name)
		bench_doc = frappe.get_doc("HT Bench", doc.bench)
		from htbencher.custom.ssh_utils import execute_command
		
		execute_command(["bench", "--site", doc.full_domain, "backup"], bench_doc=bench_doc, cwd=bench_doc.path, task_id=f"backup_{site_name}")
	except Exception as e:
		frappe.log_error(str(e), "Site Backup Error")


