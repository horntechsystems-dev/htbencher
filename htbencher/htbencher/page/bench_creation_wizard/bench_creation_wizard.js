frappe.provide("htbencher");

frappe.pages['bench-creation-wizard'].on_page_load = function (wrapper) {
    new htbencher.BenchCreationWizard(wrapper);
}

htbencher.BenchCreationWizard = class BenchCreationWizard {
    constructor(wrapper) {
        this.wrapper = $(wrapper);
        this.make();
    }

    make() {
        this.page = frappe.ui.make_app_page({
            parent: this.wrapper,
            title: 'Create New Bench',
            single_column: true
        });

        this.page.main.html(frappe.render_template('bench_creation_wizard', {}));

        this.fetch_python_versions();
        this.fetch_servers();
        this.bind_events();
    }

    fetch_python_versions(server) {
        frappe.call({
            method: "htbencher.api.v1.bench.get_available_pythons",
            args: {
                server: server
            },
            callback: (r) => {
                if (r.message) {
                    let select = this.wrapper.find('select[name="python_version"]');
                    select.empty();
                    r.message.forEach(v => {
                        select.append(`<option value="${v}">${v}</option>`);
                    });

                    // Select python3.11 if available, else first
                    if (r.message.includes('python3.11')) {
                        select.val('python3.11');
                    }
                }
            }
        });
    }

    fetch_servers() {
        frappe.call({
            method: "frappe.client.get_list",
            args: {
                doctype: "HT Server",
                fields: ["name"]
            },
            callback: (r) => {
                if (r.message) {
                    let select = this.wrapper.find('select[name="server_name"]');
                    select.empty();
                    select.append('<option value="" selected disabled>Select Server...</option>');
                    r.message.forEach(s => {
                        select.append(`<option value="${s.name}">${s.name}</option>`);
                    });
                }
            }
        });
    }

    bind_events() {
        // Refresh python versions when server changes
        this.wrapper.find('select[name="server_name"]').on('change', (e) => {
            let server = $(e.currentTarget).val();
            if (server) {
                this.fetch_python_versions(server);
            }
        });

        this.wrapper.find('.btn-create-bench').on('click', () => {
            let bench_name = this.wrapper.find('input[name="bench_name"]').val();
            let server_name = this.wrapper.find('select[name="server_name"]').val();
            let python_version = this.wrapper.find('select[name="python_version"]').val();
            let frappe_branch = this.wrapper.find('input[name="frappe_branch"]').val();

            if (!bench_name) {
                frappe.msgprint("Please enter a bench name");
                return;
            }

            if (!server_name) {
                frappe.msgprint("Please select a server");
                return;
            }

            this.wrapper.find('.progress-container').show();
            this.wrapper.find('.terminal-container').show();
            this.wrapper.find('#terminal-logs').html('<p>Starting bench creation...</p>');
            this.update_progress(0, "Starting...");
            this.wrapper.find('.btn-create-bench').prop('disabled', true);

            frappe.call({
                method: "htbencher.api.v1.bench.create_bench",
                args: {
                    bench_name: bench_name,
                    server: server_name,
                    python_version: python_version,
                    frappe_branch: frappe_branch
                },
                callback: (r) => {
                    if (r.message && r.message.task_id) {
                        this.listen_to_logs(r.message.task_id);
                        frappe.msgprint("Bench creation task queued. Monitor logs below.");
                    } else {
                        this.wrapper.find('.btn-create-bench').prop('disabled', false);
                    }
                },
                error: () => {
                    this.wrapper.find('.btn-create-bench').prop('disabled', false);
                }
            });
        });
    }

    listen_to_logs(task_id) {
        frappe.realtime.on('htbench_task_progress', (data) => {
            if (data.task_id === task_id) {
                this.update_progress(data.percentage, data.status);
            }
        });

        frappe.realtime.on('htbench_task_log', (data) => {
            if (data.task_id === task_id) {
                let color = data.error ? '#ff5858' : '#0f0';
                let html = `<div style="color: ${color};"><span style="color: #888;">[${new Date().toLocaleTimeString()}]</span> ${data.log}</div>`;
                let terminal = this.wrapper.find('#terminal-logs');
                terminal.append(html);

                // Auto scroll
                let container = this.wrapper.find('.terminal-container');
                container.scrollTop(container[0].scrollHeight);
            }
        });

        frappe.realtime.on('htbench_task_complete', (data) => {
            if (data.task_id === task_id) {
                let msg = data.status === 'success' ? 'Task Completed Successfully' : 'Task Failed';
                let color = data.status === 'success' ? '#0f0' : '#ff5858';
                this.wrapper.find('#terminal-logs').append(`<div style="color: ${color}; font-weight: bold; margin-top: 10px;">=== ${msg} ===</div>`);
                this.wrapper.find('.btn-create-bench').prop('disabled', false);

                if (data.status === 'success') {
                    this.update_progress(100, "Completed");
                }
            }
        });
    }

    update_progress(percentage, status) {
        let bar = this.wrapper.find('#creation-progress-bar');
        bar.css('width', percentage + '%');
        bar.attr('aria-valuenow', percentage);
        this.wrapper.find('#progress-percentage').text(percentage + '%');
        if (status) {
            this.wrapper.find('#progress-status').text(status);
        }
    }
}
