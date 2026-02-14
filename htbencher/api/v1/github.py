import frappe
import requests
import os
import subprocess
import tempfile
from frappe import _

@frappe.whitelist()
def get_github_accounts():
    """Fetch all GitHub accounts."""
    return frappe.get_all("HT Github Account", fields=["name", "account_name", "status"])

@frappe.whitelist()
def add_github_account(account_name, ssh_private_key, ssh_public_key, github_token=None):
    """Bridge for frontend API call."""
    return add_github_account_ssh(
        name=account_name, 
        private_key=ssh_private_key, 
        public_key=ssh_public_key, 
        token=github_token
    )

@frappe.whitelist()
def add_github_account_ssh(name, private_key, public_key, token=None):
    """Add a new GitHub account with SSH keys."""
    if frappe.db.exists("HT Github Account", name):
        doc = frappe.get_doc("HT Github Account", name)
        doc.ssh_private_key = private_key
        doc.ssh_public_key = public_key
        if token:
            doc.github_token = token
        doc.save()
    else:
        doc = frappe.get_doc({
            "doctype": "HT Github Account",
            "account_name": name,
            "ssh_private_key": private_key,
            "ssh_public_key": public_key,
            "github_token": token,
            "status": "Active"
        })
        doc.insert()
    
    frappe.db.commit()
    return doc.name

@frappe.whitelist()
def get_github_repositories(account_name):
    """Fetch repositories from GitHub for a specific account."""
    doc = frappe.get_doc("HT Github Account", account_name)
    token = doc.get_password("github_token")
    if not token:
        frappe.throw(_("GitHub Token is required to fetch repositories. Please update the account settings."))
    
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "HTBencher"
    }
    
    # We fetch both user repos and org repos
    try:
        repos = []
        # Get user repos
        response = requests.get("https://api.github.com/user/repos?per_page=100", headers=headers)
        if response.status_code != 200:
            frappe.log_error(f"GitHub API Error (Repos): {response.status_code} - {response.text}", "GitHub Integration")
            response.raise_for_status()
            
        repos.extend(response.json())
        
        return [{
            "name": r["name"],
            "full_name": r["full_name"],
            "ssh_url": r["ssh_url"],
            "description": r.get("description", "")
        } for r in repos]
    except Exception as e:
        frappe.throw(_("Failed to fetch repositories. Please check if your token has 'repo' scope. Error: {0}").format(str(e)))

@frappe.whitelist()
def get_github_branches(account_name, repo_full_name, repo_ssh_url=None):
    """Fetch branches for a repository using multiple fallback strategies."""
    # Handle frontend sending "undefined" string
    if repo_ssh_url == "undefined":
        repo_ssh_url = None
        
    doc = frappe.get_doc("HT Github Account", account_name)
    
    # Strategy 1: Git ls-remote via SSH (Best for private repos if key is added)
    if repo_ssh_url and doc.ssh_private_key:
        temp_key_path = None
        try:
            temp_key_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='_ssh_branch')
            temp_key_path = temp_key_file.name
            temp_key_file.write(doc.ssh_private_key)
            temp_key_file.close()
            os.chmod(temp_key_path, 0o600)
            
            env = os.environ.copy()
            env['GIT_SSH_COMMAND'] = f'ssh -i {temp_key_path} -o StrictHostKeyChecking=no -o BatchMode=yes'
            
            result = subprocess.run(
                ['git', 'ls-remote', '--heads', repo_ssh_url],
                env=env,
                capture_output=True,
                text=True,
                timeout=15
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                branches = [line.split('\t')[1].replace('refs/heads/', '') for line in lines if '\t' in line]
                if branches:
                    return branches
        except Exception as e:
            frappe.log_error(f"Git ls-remote SSH failed for {repo_full_name}: {str(e)}", "GitHub Integration")
        finally:
            if temp_key_path and os.path.exists(temp_key_path):
                os.remove(temp_key_path)

    # Strategy 2: Git ls-remote via HTTPS (Best for public repos, no auth needed)
    try:
        https_url = f"https://github.com/{repo_full_name}.git"
        result = subprocess.run(
            ['git', 'ls-remote', '--heads', https_url],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            branches = [line.split('\t')[1].replace('refs/heads/', '') for line in lines if '\t' in line]
            if branches:
                return branches
    except Exception as e:
        pass

    # Strategy 3: REST API (Requires token with appropriate scope)
    token = doc.get_password("github_token")
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "HTBencher"
    }
    if token:
        headers["Authorization"] = f"token {token}"
    
    try:
        api_url = f"https://api.github.com/repos/{repo_full_name}/branches"
        response = requests.get(api_url, headers=headers)
        
        # If forbidden and we had a token, try without the token (one last time for public repos)
        if response.status_code in [403, 404] and token:
            response = requests.get(api_url, headers={
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "HTBencher"
            })
        
        if response.status_code == 200:
            branches = response.json()
            return [b["name"] for b in branches]
        
        # If all else fails, throw a meaningful error from the REST API
        error_data = response.json() if response.text else {}
        error_msg = error_data.get("message", response.text)
        
        frappe.log_error(f"All strategies failed for {repo_full_name}. Final error: {response.status_code} - {error_msg}", "GitHub Integration")
        
        if response.status_code in [403, 404] and "token" in error_msg.lower():
            frappe.throw(_("GitHub returned {0}: '{1}'. This usually means your Token needs the 'repo' scope (for Classic tokens) or 'Contents: Read' permission (for Fine-grained tokens), or the repository is private.").format(response.status_code, error_msg))
        
        response.raise_for_status()
            
    except Exception as e:
        if isinstance(e, frappe.ValidationError):
            raise e
        frappe.throw(_("Failed to fetch branches. Please ensure your SSH key is added to GitHub OR your Token has 'repo' scope. Error: {0}").format(str(e)))

@frappe.whitelist()
def install_app(bench_name, account_name, repo_full_name, repo_ssh_url, branch):
    """Install app from GitHub into a bench."""
    account_doc = frappe.get_doc("HT Github Account", account_name)
    
    # Extract app name from repo (usually the last part)
    app_name = repo_full_name.split('/')[-1]
    
    # Create or Update HT App
    if frappe.db.exists("HT App", app_name):
        app_doc = frappe.get_doc("HT App", app_name)
    else:
        app_doc = frappe.new_doc("HT App")
        app_doc.app_name = app_name
    
    app_doc.repo_url = repo_ssh_url
    app_doc.branch = branch
    app_doc.is_private = 1
    app_doc.ssh_private_key = account_doc.ssh_private_key
    app_doc.save()
    frappe.db.commit()
    
    # Now call the existing install_app logic
    from htbencher.api.v1.app import install_app
    return install_app(app_name, bench_name)
