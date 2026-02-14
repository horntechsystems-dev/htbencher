import api from "./api"
import { API_BASE } from "./server"

// Helper to construct full URL
const url = (endpoint) => `${API_BASE}.${endpoint}`

export const auth = {
    login: (email, password) => api.post("htbencher.api.login", { usr: email, pwd: password }),
}

export const resource = {
    getCount: (doctype, filters = {}) => api.get("/api/method/frappe.client.get_count", { doctype, filters }),
    getList: (doctype, fields = ["name"], filters = {}) => api.get("/api/method/frappe.client.get_list", { doctype, fields, filters }),
    getValue: (doctype, fieldname, filters = {}) => api.get("/api/method/frappe.client.get_value", { doctype, fieldname, filters }),
}

export const system = {
    status: () => api.get(url("api.get_system_status")),
    servers: () => api.get("frappe.client.get_list", { doctype: "HT Server", fields: ["name"] }),
}

export const benches = {
    getAll: () => api.get(url("api.v1.bench.get_benches")),
    list: () => api.get(url("api.v1.bench.get_benches")), // Alias for backward compatibility
    getInstalledApps: (bench_name) => api.get(url("api.v1.bench.get_installed_apps"), { bench_name }),
    create: (data) => api.post(url("api.v1.bench.create_bench"), data),
    update: (bench_name) => api.post(url("api.v1.bench.update_bench"), { bench_name }),
    restart: (bench_name) => api.post(url("api.v1.bench.build_bench"), { bench_name }),
    installApp: (bench, app) => api.post(url("api.v1.bench.get_app"), { bench_name: bench, app_doc_name: app }),
    getPythons: (server) => api.get(url("api.v1.bench.get_available_pythons"), { server }),
}

export const sites = {
    getAll: (bench_name) => api.get(url("api.v1.site.get_sites"), { bench_name }),
    list: (bench_name) => api.get(url("api.v1.site.get_sites"), { bench_name }), // Alias
    getInstalledApps: (site_name) => api.get(url("api.v1.site.get_installed_apps"), { site_name }),
    create: (data) => api.post(url("api.v1.site.create_site"), data),
    backup: (bench) => api.post(url("api.v1.site.backup_sites"), { bench_name: bench }),
    migrate: (bench) => api.post(url("api.v1.site.migrate_sites"), { bench_name: bench }),
    delete: (site) => api.delete(url("api.v1.site.delete_site"), { site_name: site }),
    installApp: (site_name, app_name) => api.post(url("api.v1.site.install_app"), { site_name, app_name }),
    uninstallApp: (site_name, app_name) => api.post(url("api.v1.site.uninstall_app"), { site_name, app_name }),
}

export const apps = {
    list: () => api.get(url("api.get_apps")),
    available: () => api.get(url("api.get_available_apps")),
    installToBench: (bench_name, app_name) => api.post(url("api.v1.bench.get_app"), { bench_name, app_doc_name: app_name }),
    uninstallFromBench: (bench_name, app_name) => api.post(url("api.v1.bench.uninstall_app"), { bench_name, app_name }),
    installToSite: (site_name, app_name) => api.post(url("api.v1.site.install_app"), { site_name, app_name }),
    uninstallFromSite: (site_name, app_name) => api.post(url("api.v1.site.uninstall_app"), { site_name, app_name }),
}

export const github = {
    getAccounts: () => api.get(url("api.v1.github.get_github_accounts")),
    addAccount: (data) => api.post(url("api.v1.github.add_github_account"), data),
    getRepos: (account_name) => api.get(url("api.v1.github.get_github_repositories"), { account_name }),
    getBranches: (account_name, repo_full_name, repo_ssh_url) => api.get(url("api.v1.github.get_github_branches"), { account_name, repo_full_name, repo_ssh_url }),
    installApp: (data) => api.post(url("api.v1.github.install_app"), data),
}

export const tasks = {
    getStatus: (task_id) => api.get(url("api.v1.site.get_task_status"), { task_id }),
}

export default {
    auth,
    resource,
    system,
    benches,
    sites,
    apps,
    tasks,
    github,
}
