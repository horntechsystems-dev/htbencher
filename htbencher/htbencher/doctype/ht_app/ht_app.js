frappe.ui.form.on('HT App', {
    refresh: function (frm) {
        // Add Test SSH Connection button for private repos
        if (!frm.is_new() && frm.doc.is_private && frm.doc.repo_url) {
            frm.add_custom_button(__('Test SSH Connection'), function () {
                frappe.call({
                    method: 'htbencher.api.v1.app.test_ssh_connection',
                    args: {
                        app_name: frm.doc.name
                    },
                    freeze: true,
                    freeze_message: __('Testing SSH connection...'),
                    callback: function (r) {
                        if (r.message) {
                            if (r.message.success) {
                                frappe.msgprint({
                                    title: __('SSH Connection Successful'),
                                    message: r.message.message,
                                    indicator: 'green'
                                });
                            } else {
                                frappe.msgprint({
                                    title: __('SSH Connection Failed'),
                                    message: r.message.message,
                                    indicator: 'red'
                                });
                            }
                        }
                    }
                });
            }, __('Actions'));
        }

        // Add button to convert HTTPS URL to SSH
        if (!frm.is_new() && frm.doc.repo_url && frm.doc.repo_url.startsWith('https://github.com')) {
            frm.add_custom_button(__('Convert to SSH URL'), function () {
                let ssh_url = convert_https_to_ssh(frm.doc.repo_url);
                frappe.msgprint({
                    title: __('SSH URL'),
                    message: `<p>For private repositories, use this SSH URL instead:</p>
						<pre style="background: #f5f5f5; padding: 10px; border-radius: 5px;">${ssh_url}</pre>
						<p><button class="btn btn-primary btn-sm" onclick="
							navigator.clipboard.writeText('${ssh_url}');
							frappe.show_alert({message: 'Copied to clipboard!', indicator: 'green'});
						">Copy to Clipboard</button></p>`,
                    indicator: 'blue'
                });
            }, __('Actions'));
        }

        // Add Install on Bench button
        if (!frm.is_new()) {
            frm.add_custom_button(__('Install on Bench'), function () {
                let d = new frappe.ui.Dialog({
                    title: __('Install App on Bench'),
                    fields: [
                        {
                            label: 'Bench',
                            fieldname: 'bench',
                            fieldtype: 'Link',
                            options: 'HT Bench',
                            get_query: function () {
                                return {
                                    filters: {
                                        status: 'Active'
                                    }
                                };
                            },
                            reqd: 1
                        }
                    ],
                    primary_action_label: __('Install'),
                    primary_action: function (values) {
                        d.hide();
                        frappe.call({
                            method: 'htbencher.api.v1.app.install_app',
                            args: {
                                app_name: frm.doc.name,
                                bench_name: values.bench
                            },
                            callback: function (r) {
                                if (r.message && r.message.task_id) {
                                    frappe.msgprint({
                                        message: __('Installation started. Task ID: {0}', [r.message.task_id]),
                                        indicator: 'green'
                                    });
                                }
                            }
                        });
                    }
                });
                d.show();
            }, __('Actions'));
        }
    },

    is_private: function (frm) {
        if (frm.doc.is_private && frm.doc.repo_url) {
            // Check if URL is HTTPS
            if (frm.doc.repo_url.startsWith('https://')) {
                frappe.msgprint({
                    title: __('Private Repository Detected'),
                    message: `<p>For private repositories, you should use SSH URL format instead of HTTPS.</p>
						<p><strong>Current URL:</strong> ${frm.doc.repo_url}</p>
						<p><strong>Recommended SSH URL:</strong></p>
						<pre style="background: #f5f5f5; padding: 10px; border-radius: 5px;">${convert_https_to_ssh(frm.doc.repo_url)}</pre>
						<p>Click the "Convert to SSH URL" button to get the correct format.</p>`,
                    indicator: 'orange'
                });
            }
        }
    },

    repo_url: function (frm) {
        // Auto-detect if it's a private repo based on URL format
        if (frm.doc.repo_url) {
            // Validate URL format
            if (frm.doc.repo_url.startsWith('git@')) {
                // SSH URL detected
                frm.set_value('is_private', 1);
                frappe.show_alert({
                    message: __('SSH URL detected - marked as private repository'),
                    indicator: 'blue'
                });
            } else if (frm.doc.repo_url.includes('@')) {
                // Token in URL
                frappe.msgprint({
                    title: __('Security Warning'),
                    message: `<p>Your URL contains credentials (token). This is not recommended for security reasons.</p>
						<p>Consider using SSH URL format instead.</p>`,
                    indicator: 'orange'
                });
            }
        }
    }
});

function convert_https_to_ssh(https_url) {
    // Convert https://github.com/username/repo.git to git@github.com:username/repo.git
    let ssh_url = https_url
        .replace('https://github.com/', 'git@github.com:')
        .replace('http://github.com/', 'git@github.com:');

    // Ensure .git extension
    if (!ssh_url.endsWith('.git')) {
        ssh_url += '.git';
    }

    return ssh_url;
}
