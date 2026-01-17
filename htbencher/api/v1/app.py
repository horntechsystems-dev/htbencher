import frappe
import tempfile
import os
import subprocess

@frappe.whitelist()
def install_app(app_name, bench_name):
	"""
	Install this app on the specified bench
	"""
	from htbencher.custom.bench_operations import get_app
	
	task_id = frappe.generate_hash(length=10)
	
	frappe.enqueue(
		get_app,
		queue='long',
		timeout=3600,
		bench_name=bench_name,
		app_doc_name=app_name,
		task_id=task_id
	)
	
	return {"task_id": task_id}

@frappe.whitelist()
def test_ssh_connection(app_name):
	"""
	Test SSH connection for a private repository
	
	Args:
		app_name: Name of the HT App document
	
	Returns:
		dict: {success: bool, message: str}
	"""
	temp_key_path = None
	try:
		app_doc = frappe.get_doc("HT App", app_name)
		
		if not app_doc.is_private:
			return {
				"success": False,
				"message": "This app is not marked as private. SSH test is only for private repositories."
			}
		
		if not app_doc.repo_url:
			return {
				"success": False,
				"message": "Repository URL is not set."
			}
		
		# Check if URL is SSH format
		if not app_doc.repo_url.startswith('git@'):
			return {
				"success": False,
				"message": f"Repository URL must be in SSH format (git@github.com:user/repo.git), not HTTPS.\n\nCurrent URL: {app_doc.repo_url}"
			}
		
		# Extract host from git@github.com:user/repo.git
		try:
			host = app_doc.repo_url.split('@')[1].split(':')[0]
		except:
			return {
				"success": False,
				"message": "Invalid SSH URL format. Expected: git@github.com:user/repo.git"
			}
		
		# If SSH key is provided, test with it
		if app_doc.ssh_private_key:
			# Create temporary SSH key file
			temp_key_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='_ssh_test')
			temp_key_path = temp_key_file.name
			temp_key_file.write(app_doc.ssh_private_key)
			temp_key_file.close()
			
			# Set permissions to 600 (required by SSH)
			os.chmod(temp_key_path, 0o600)
			
			# Test SSH connection
			cmd = f'ssh -i {temp_key_path} -o StrictHostKeyChecking=no -o BatchMode=yes -T git@{host}'
			
			try:
				result = subprocess.run(
					cmd,
					shell=True,
					capture_output=True,
					text=True,
					timeout=10
				)
				
				# GitHub returns exit code 1 even on successful auth (because no command was run)
				# But the output will contain success message
				output = result.stdout + result.stderr
				
				if 'successfully authenticated' in output.lower() or 'hi ' in output.lower():
					return {
						"success": True,
						"message": f"✓ SSH authentication successful!\n\nConnected to {host}\n\nYou can now install this app."
					}
				elif 'permission denied' in output.lower():
					return {
						"success": False,
						"message": f"✗ SSH authentication failed: Permission denied\n\nPossible issues:\n1. SSH key is not added to your GitHub account\n2. SSH key is incorrect or corrupted\n3. Repository access denied\n\nOutput: {output[:200]}"
					}
				else:
					return {
						"success": False,
						"message": f"✗ SSH connection failed\n\nOutput: {output[:300]}"
					}
			except subprocess.TimeoutExpired:
				return {
					"success": False,
					"message": "✗ SSH connection timeout. Check your network connection."
				}
			except Exception as e:
				return {
					"success": False,
					"message": f"✗ Error testing SSH: {str(e)}"
				}
		else:
			# No SSH key provided - check if system SSH works
			return {
				"success": False,
				"message": "No SSH private key provided. Please paste your SSH private key in the 'SSH Private Key' field."
			}
			
	except Exception as e:
		frappe.log_error(str(e), "SSH Connection Test Failed")
		return {
			"success": False,
			"message": f"✗ Error: {str(e)}"
		}
	finally:
		# Clean up temporary SSH key file
		if temp_key_path and os.path.exists(temp_key_path):
			try:
				os.remove(temp_key_path)
			except Exception as e:
				frappe.log_error(f"Failed to remove temp SSH key: {e}", "SSH Test Cleanup")
