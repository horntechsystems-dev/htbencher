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
		
		# We assume the parent directory of 'path' exists or bench init creates it?
		# bench init creates the directory 'path'. But the parent of 'path' must exist and be writable.
		# For remote, typically we might need to be in a home dir or similar.
		# If doc.path is absolute, bench init handles it? Yes.
		
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
