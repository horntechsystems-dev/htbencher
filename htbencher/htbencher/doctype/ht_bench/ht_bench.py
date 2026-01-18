import frappe
from frappe.model.document import Document

import os
import stat

class HTBench(Document):
	def before_save(self):
		if self.server:
			self.fetch_server_details()
		
		if self.is_remote and self.ssh_private_key:
			self.save_ssh_key()

	def fetch_server_details(self):
		# We don't need to copy everything, just ensure we have the link
		# The execution logic handles the rest via ssh_utils
		pass

	def save_ssh_key(self):
		# Create a directory for SSH keys if it doesn't exist
		keys_dir = frappe.get_site_path('private', 'files', 'ssh_keys')
		if not os.path.exists(keys_dir):
			os.makedirs(keys_dir, mode=0o700)

		# Generate a filename based on the bench name
		key_filename = f"id_rsa_{self.name.lower().replace(' ', '_')}"
		key_path = os.path.join(keys_dir, key_filename)

		# Write the key to the file
		with open(key_path, 'w') as f:
			f.write(self.ssh_private_key.strip() + '\n')

		# Set file permissions to 600 (read/write for owner only)
		os.chmod(key_path, stat.S_IRUSR | stat.S_IWUSR)

		# Update the path in the document
		self.ssh_key_path = key_path


	def after_insert(self):
		"""Trigger bench creation after document is created"""
		frappe.enqueue(
			"htbencher.htbencher.doctype.ht_bench.ht_bench.create_bench_background",
			queue="long",
			timeout=3600,
			bench_name=self.name
		)
		frappe.msgprint(f"Bench creation started for {self.bench_name}. Check background jobs or logs for progress.")

	@frappe.whitelist()
	def install_app(self, app_name):
		"""
		Install (Get) an app on this bench
		"""
		frappe.enqueue(
			"htbencher.htbencher.doctype.ht_bench.ht_bench.get_app_background",
			queue="long",
			timeout=3600,
			bench_name=self.name,
			app_name=app_name
		)
		frappe.msgprint(f"App installation started for {app_name} on {self.bench_name}.")

def create_bench_background(bench_name):
	"""
	Background job to create the bench
	"""
	try:
		doc = frappe.get_doc("HT Bench", bench_name)
		from htbencher.custom.ssh_utils import execute_command
		
		# Construct the command
		# bench init [path] --frappe-branch [branch] --python [version]
		cmd = [
			"bench", "init", doc.path,
			"--frappe-branch", doc.frappe_branch,
			"--python", doc.python_version or "python3.10"
		]
		
		success, output = execute_command(
			cmd, 
			bench_doc=doc, 
			task_id=f"create_bench_{doc.name}",
			env={"FRAPPE_DOCKER_BUILD": "1"}
		)
		
		if success:
			frappe.log_error(f"Bench {doc.name} created successfully", "Bench Creation Success")
		else:
			frappe.log_error(f"Failed to create bench {doc.name}: {output}", "Bench Creation Failed")
			
	except Exception as e:
		frappe.log_error(f"Error in create_bench_background: {str(e)}", "Bench Creation Error")


def get_app_background(bench_name, app_name):
	"""
	Background job to run bench get-app
	"""
	try:
		bench_doc = frappe.get_doc("HT Bench", bench_name)
		app_doc = frappe.get_doc("HT App", app_name)
		from htbencher.custom.ssh_utils import execute_command, write_file
		
		# Define Paths
		# We need a robust way to determine where to put the key
		# Using /tmp is generally safe for temporary keys
		key_filename = f"deploy_key_{app_doc.name}.key"
		key_path = f"/tmp/{key_filename}"
		
		env = {}
		cmd = ["bench", "get-app", app_doc.repo_url]
		
		if app_doc.branch:
			cmd.extend(["--branch", app_doc.branch])
		
		key_created = False
		
		# Handle Private Repo
		if app_doc.is_private and app_doc.ssh_private_key:
			# 1. Write Key File
			key_content = app_doc.ssh_private_key.strip() + "\n"
			success, msg = write_file(key_content, key_path, bench_doc)
			if not success:
				frappe.log_error(f"Failed to write SSH key: {msg}", "Bench Get-App Error")
				return

			key_created = True
			
			# 2. Set Permissions (chmod 600)
			success, msg = execute_command(f"chmod 600 {key_path}", bench_doc=bench_doc)
			if not success:
				frappe.log_error(f"Failed to chmod SSH key: {msg}", "Bench Get-App Error")
				return 
				
			# 3. Configure GIT_SSH_COMMAND
			ssh_cmd = f"ssh -i {key_path} -o StrictHostKeyChecking=no"
			env["GIT_SSH_COMMAND"] = f"'{ssh_cmd}'"
			
			# Note: We must quote the value so the export command is valid shell syntax
			# export GIT_SSH_COMMAND='ssh ...'
		
		success, output = execute_command(
			cmd,
			bench_doc=bench_doc,
			cwd=bench_doc.path,
			task_id=f"get_app_{app_name}",
			env=env
		)
		
		if success:
			frappe.log_error(f"App {app_name} installed on bench {bench_name}", "Bench Get-App Success")
		else:
			frappe.log_error(f"Failed to install app {app_name}: {output}", "Bench Get-App Failed")
			
	except Exception as e:
		frappe.log_error(f"Error in get_app_background: {str(e)}", "Bench Get-App Error")
	finally:
		# Cleanup Key File
		if key_created:
			try:
				execute_command(f"rm {key_path}", bench_doc=bench_doc)
			except Exception:
				pass
