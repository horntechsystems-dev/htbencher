frappe.provide("htbencher");

frappe.pages['ht-dashboard'].on_page_load = function (wrapper) {
    new htbencher.HTDashboard(wrapper);
}

htbencher.HTDashboard = class HTDashboard {
    constructor(wrapper) {
        this.wrapper = $(wrapper);
        this.selected_bench = null;
        this.current_task_id = null;
        this.make();
    }

    make() {
        this.page = frappe.ui.make_app_page({
            parent: this.wrapper,
            title: 'HT Dashboard',
            single_column: true
        });

        this.page.main.html(frappe.render_template('ht_dashboard', {}));
        this.refresh();
        this.load_benches();
        this.bind_events();
    }

    refresh() {
        // Fetch bench statistics
        frappe.call({
            method: 'frappe.client.get_count',
            args: {
                doctype: 'HT Bench',
                filters: { status: 'Active' }
            },
            callback: (r) => {
                if (r.message !== undefined) {
                    this.wrapper.find('.active-benches-count').text(r.message);
                }
            }
        });

        // Fetch site count
        frappe.call({
            method: 'frappe.client.get_count',
            args: {
                doctype: 'HT Site'
            },
            callback: (r) => {
                if (r.message !== undefined) {
                    this.wrapper.find('.total-sites-count').text(r.message);
                }
            }
        });

        // Fetch app count
        frappe.call({
            method: 'frappe.client.get_count',
            args: {
                doctype: 'HT App'
            },
            callback: (r) => {
                if (r.message !== undefined) {
                    this.wrapper.find('.total-apps-count').text(r.message);
                }
            }
        });
    }

    load_benches() {
        frappe.call({
            method: 'frappe.client.get_list',
            args: {
                doctype: 'HT Bench',
                filters: { status: 'Active' },
                fields: ['name', 'bench_name']
            },
            callback: (r) => {
                if (r.message) {
                    let select = this.wrapper.find('.bench-selector');
                    select.empty();
                    select.append('<option value="">Select a bench...</option>');
                    r.message.forEach(bench => {
                        select.append(`<option value="${bench.name}">${bench.bench_name}</option>`);
                    });
                }
            }
        });
    }

    bind_events() {
        // Bench selection
        this.wrapper.find('.bench-selector').on('change', (e) => {
            this.selected_bench = $(e.target).val();
            if (this.selected_bench) {
                this.wrapper.find('.bench-actions').show();
            } else {
                this.wrapper.find('.bench-actions').hide();
            }
        });

        // Update bench
        this.wrapper.find('.btn-update-bench').on('click', () => {
            this.run_operation('update', 'htbencher.api.v1.bench.update_bench');
        });

        // Build bench
        this.wrapper.find('.btn-build-bench').on('click', () => {
            this.run_operation('build', 'htbencher.api.v1.bench.build_bench');
        });

        // Migrate
        this.wrapper.find('.btn-migrate-bench').on('click', () => {
            this.show_migrate_dialog();
        });

        // Backup
        this.wrapper.find('.btn-backup-bench').on('click', () => {
            this.show_backup_dialog();
        });

        // Install app
        this.wrapper.find('.btn-install-app').on('click', () => {
            this.show_install_app_dialog();
        });

        // Create site
        this.wrapper.find('.btn-create-site').on('click', () => {
            this.show_create_site_dialog();
        });
    }

    run_operation(operation_name, api_method, args = {}) {
        if (!this.selected_bench) {
            frappe.msgprint('Please select a bench first');
            return;
        }

        this.wrapper.find('.operation-log').show();
        this.wrapper.find('#operation-logs').html(`<p>Starting ${operation_name}...</p>`);

        frappe.call({
            method: api_method,
            args: {
                bench_name: this.selected_bench,
                ...args
            },
            callback: (r) => {
                if (r.message && r.message.task_id) {
                    this.current_task_id = r.message.task_id;
                    this.listen_to_logs(r.message.task_id);
                }
            }
        });
    }

    listen_to_logs(task_id) {
        frappe.realtime.on('htbench_task_log', (data) => {
            if (data.task_id === task_id) {
                let log_div = this.wrapper.find('#operation-logs');
                let color = data.error ? '#f00' : '#0f0';
                log_div.append(`<p style="color: ${color}; margin: 2px 0;">${data.log}</p>`);
                log_div.parent().scrollTop(log_div.parent()[0].scrollHeight);
            }
        });

        frappe.realtime.on('htbench_task_complete', (data) => {
            if (data.task_id === task_id) {
                let log_div = this.wrapper.find('#operation-logs');
                if (data.status === 'success') {
                    log_div.append('<p style="color: #0f0; font-weight: bold;">✓ Operation completed successfully!</p>');
                    this.refresh();
                } else {
                    log_div.append('<p style="color: #f00; font-weight: bold;">✗ Operation failed!</p>');
                }
            }
        });
    }

    show_migrate_dialog() {
        frappe.prompt([
            {
                label: 'Skip Failing Patches',
                fieldname: 'skip_failing',
                fieldtype: 'Check'
            }
        ], (values) => {
            this.run_operation('migrate', 'htbencher.api.v1.site.migrate_sites', {
                skip_failing: values.skip_failing ? 1 : 0
            });
        }, 'Migrate Database', 'Run Migration');
    }

    show_backup_dialog() {
        frappe.prompt([
            {
                label: 'Include Files',
                fieldname: 'with_files',
                fieldtype: 'Check',
                default: 1
            }
        ], (values) => {
            this.run_operation('backup', 'htbencher.api.v1.site.backup_sites', {
                with_files: values.with_files ? 1 : 0
            });
        }, 'Backup Sites', 'Create Backup');
    }

    show_install_app_dialog() {
        frappe.call({
            method: 'frappe.client.get_list',
            args: {
                doctype: 'HT App',
                fields: ['name']
            },
            callback: (r) => {
                if (r.message) {
                    let apps = r.message.map(a => a.name);
                    frappe.prompt([
                        {
                            label: 'App',
                            fieldname: 'app_name',
                            fieldtype: 'Select',
                            options: apps,
                            reqd: 1
                        }
                    ], (values) => {
                        this.run_operation('install-app', 'htbencher.api.v1.bench.get_app', {
                            app_name: values.app_name
                        });
                    }, 'Install App', 'Install');
                }
            }
        });
    }

    show_create_site_dialog() {
        // First, fetch available root domains
        frappe.call({
            method: 'frappe.client.get_list',
            args: {
                doctype: 'HT Root Domain',
                filters: { is_active: 1 },
                fields: ['name', 'domain_name']
            },
            callback: (r) => {
                let root_domains = r.message || [];
                let domain_options = root_domains.map(d => d.name);

                // Get bench server IP if available
                let server_ip = '';
                if (this.selected_bench) {
                    frappe.call({
                        method: 'frappe.client.get_value',
                        args: {
                            doctype: 'HT Bench',
                            filters: { name: this.selected_bench },
                            fieldname: ['hostname']
                        },
                        async: false,
                        callback: (bench_r) => {
                            if (bench_r.message && bench_r.message.hostname) {
                                server_ip = bench_r.message.hostname;
                            }
                        }
                    });
                }

                frappe.prompt([
                    {
                        label: 'Site Name',
                        fieldname: 'site_name',
                        fieldtype: 'Data',
                        reqd: 1,
                        description: 'Enter the site name (e.g., mysite.local)'
                    },
                    {
                        label: 'Admin Password',
                        fieldname: 'admin_password',
                        fieldtype: 'Password',
                        reqd: 1,
                        description: 'Password for the Administrator user'
                    },
                    {
                        label: 'MariaDB Root Password',
                        fieldname: 'db_password',
                        fieldtype: 'Password',
                        reqd: 1,
                        description: 'MariaDB root password for database creation'
                    },
                    {
                        fieldname: 'section_break_1',
                        fieldtype: 'Section Break',
                        label: 'Domain Configuration (Optional)'
                    },
                    {
                        label: 'Root Domain',
                        fieldname: 'root_domain',
                        fieldtype: 'Select',
                        options: domain_options,
                        description: 'Select root domain for automatic DNS creation'
                    },
                    {
                        label: 'Subdomain',
                        fieldname: 'subdomain',
                        fieldtype: 'Data',
                        description: 'Subdomain name (e.g., mysite for mysite.horntech.cloud)'
                    },
                    {
                        label: 'Server IP Address',
                        fieldname: 'server_ip',
                        fieldtype: 'Data',
                        default: server_ip,
                        description: 'IP address for DNS A record'
                    }
                ], (values) => {
                    this.run_operation('create-site', 'htbencher.api.v1.site.create_site', {
                        site_name: values.site_name,
                        admin_password: values.admin_password,
                        db_password: values.db_password,
                        root_domain: values.root_domain || '',
                        subdomain: values.subdomain || '',
                        server_ip: values.server_ip || ''
                    });
                }, 'Create New Site', 'Create');
            }
        });
    }
}
