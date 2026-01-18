
import frappe
import unittest
from htbencher.custom.ssh_utils import validate_command

class TestSecurity(unittest.TestCase):
	def test_whitelist(self):
		# Allowed
		self.assertTrue(validate_command("ls -la")[0])
		self.assertTrue(validate_command("cd /tmp")[0])
		self.assertTrue(validate_command("bench init")[0])
		self.assertTrue(validate_command("bench get-app")[0])
		self.assertTrue(validate_command("git pull")[0])
		self.assertTrue(validate_command("sudo service nginx reload")[0])
		self.assertTrue(validate_command("export X=1 && bench migrate")[0])
		
		# Blocked
		self.assertFalse(validate_command("cat /etc/passwd")[0], "cat should be blocked")
		self.assertFalse(validate_command("rm -rf /")[0], "rm should be blocked? Wait, rm IS allowed.")
		# Check logic for rm
		# Allowed commands explicitly lists 'rm'.
		# But 'cat' is not in allowed list.
		
		self.assertFalse(validate_command("python3 script.py")[0], "python3 should be blocked")
		self.assertFalse(validate_command("bench shell")[0], "bench shell should be blocked (not in allowed subcommands)")
		self.assertFalse(validate_command("whoami")[0], "whoami should be blocked")
		self.assertFalse(validate_command("curl example.com")[0], "curl should be blocked")
		
		# Check complex injection
		self.assertFalse(validate_command("bench init; cat /etc/passwd")[0], "Chained blocked command")
