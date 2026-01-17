
import frappe
from frappe.model.document import Document
import os
import stat

class HTServer(Document):
	def before_save(self):
		if self.ssh_private_key:
			self.save_ssh_key()

	def save_ssh_key(self):
		# Reuse logic from HT Bench if needed, but localize to Server
		keys_dir = frappe.get_site_path('private', 'files', 'ssh_keys')
		if not os.path.exists(keys_dir):
			os.makedirs(keys_dir, mode=0o700)

		key_filename = f"id_rsa_server_{self.name.lower().replace(' ', '_')}"
		key_path = os.path.join(keys_dir, key_filename)

		with open(key_path, 'w') as f:
			f.write(self.ssh_private_key.strip() + '\n')

		os.chmod(key_path, stat.S_IRUSR | stat.S_IWUSR)
		self.ssh_key_path = key_path

	@frappe.whitelist()
	def ping(self):
		"""
		Test SSH connection to the server
		"""
		from htbencher.custom.ssh_utils import execute_remote_command
		
		# Create a dummy bench-like object for the executor
		class MockBench:
			def __init__(self, server_doc):
				self.server = server_doc.name
				self.hostname = server_doc.hostname
				self.username = server_doc.username
				self.ssh_key_path = server_doc.ssh_key_path
				self.port = 22
			def get_password(self, field):
				return server_doc.get_password(field)

		mock_bench = MockBench(self)
		
		success, output = execute_remote_command("echo 'Ping Success'", mock_bench)
		
		if success:
			return {"status": "success", "message": "Connection Successful!"}
		else:
			return {"status": "failed", "message": f"Connection Failed: {output}"}
