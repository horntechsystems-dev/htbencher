frappe.ui.form.on('HT Root Domain', {
    refresh: function (frm) {
        // Add "Test Connection" button
        if (!frm.is_new()) {
            frm.add_custom_button(__('Test Connection'), function () {
                frappe.call({
                    method: 'htbencher.api.v1.domain.test_godaddy_connection',
                    args: {
                        root_domain_name: frm.doc.name
                    },
                    freeze: true,
                    freeze_message: __('Testing GoDaddy API connection...'),
                    callback: function (r) {
                        if (r.message) {
                            if (r.message.success) {
                                frappe.msgprint({
                                    title: __('Connection Successful'),
                                    indicator: 'green',
                                    message: r.message.message
                                });
                            } else {
                                frappe.msgprint({
                                    title: __('Connection Failed'),
                                    indicator: 'red',
                                    message: r.message.message
                                });
                            }
                        }
                    }
                });
            }, __('Actions'));

            // Run Diagnostics button
            frm.add_custom_button(__('Run Diagnostics'), function () {
                frappe.call({
                    method: 'htbencher.api.v1.domain.run_diagnostics',
                    args: {
                        root_domain_name: frm.doc.name
                    },
                    freeze: true,
                    freeze_message: __('Running diagnostics...'),
                    callback: function (r) {
                        if (r.message) {
                            // Create a formatted HTML message
                            let html = `<div style="font-family: monospace;">`;
                            html += `<h4>${r.message.summary}</h4><br>`;

                            r.message.checks.forEach(check => {
                                let color = 'black';
                                if (check.status.startsWith('✓')) color = 'green';
                                else if (check.status.startsWith('✗')) color = 'red';
                                else if (check.status.startsWith('⚠')) color = 'orange';

                                html += `<div style="margin-bottom: 10px;">`;
                                html += `<strong style="color: ${color};">${check.status}</strong> ${check.name}<br>`;
                                html += `<span style="color: #666; margin-left: 20px;">${check.details}</span>`;
                                html += `</div>`;
                            });

                            if (r.message.available_domains && r.message.available_domains.length > 0) {
                                html += `<br><div style="background: #f0f0f0; padding: 10px; border-radius: 5px;">`;
                                html += `<strong>💡 Tip:</strong> The following domains are available in your GoDaddy account:<br>`;
                                html += `<span style="color: #0066cc;">${r.message.available_domains.join(', ')}</span>`;
                                html += `</div>`;
                            }

                            html += `</div>`;

                            frappe.msgprint({
                                title: __('Diagnostic Results'),
                                message: html,
                                indicator: r.message.success ? 'green' : 'red',
                                wide: true
                            });
                        }
                    }
                });
            }, __('Actions'));

            // List Available Domains button
            frm.add_custom_button(__('List Available Domains'), function () {
                frappe.call({
                    method: 'htbencher.api.v1.domain.list_available_domains',
                    args: {
                        root_domain_name: frm.doc.name
                    },
                    freeze: true,
                    freeze_message: __('Fetching domains...'),
                    callback: function (r) {
                        if (r.message && r.message.success) {
                            let html = `<div style="font-family: monospace;">`;
                            html += `<h4>Found ${r.message.count} domain(s) in your GoDaddy account:</h4><br>`;

                            if (r.message.domains.length > 0) {
                                html += `<table class="table table-bordered" style="width: 100%;">`;
                                html += `<thead><tr><th>Domain</th><th>Status</th><th>Expires</th><th>Renewable</th></tr></thead>`;
                                html += `<tbody>`;

                                r.message.domains.forEach(domain => {
                                    html += `<tr>`;
                                    html += `<td><strong>${domain.domain}</strong></td>`;
                                    html += `<td><span class="indicator ${domain.status === 'ACTIVE' ? 'green' : 'orange'}">${domain.status}</span></td>`;
                                    html += `<td>${domain.expires || 'N/A'}</td>`;
                                    html += `<td>${domain.renewable ? '✓' : '✗'}</td>`;
                                    html += `</tr>`;
                                });

                                html += `</tbody></table>`;

                                // Check if current domain is in the list
                                const currentDomain = frm.doc.domain_name;
                                const found = r.message.domains.find(d => d.domain === currentDomain);

                                if (!found) {
                                    html += `<br><div style="background: #fff3cd; padding: 10px; border-radius: 5px; border-left: 4px solid #ffc107;">`;
                                    html += `<strong>⚠ Warning:</strong> Your configured domain "<strong>${currentDomain}</strong>" was NOT found in this account.<br>`;
                                    html += `This is why you're getting "Access Denied" errors. Please verify the domain name or use a different API key.`;
                                    html += `</div>`;
                                } else {
                                    html += `<br><div style="background: #d4edda; padding: 10px; border-radius: 5px; border-left: 4px solid #28a745;">`;
                                    html += `<strong>✓ Success:</strong> Your configured domain "<strong>${currentDomain}</strong>" was found in this account!`;
                                    html += `</div>`;
                                }
                            } else {
                                html += `<p>No domains found in this account.</p>`;
                            }

                            html += `</div>`;

                            frappe.msgprint({
                                title: __('Available Domains'),
                                message: html,
                                indicator: 'blue',
                                wide: true
                            });
                        } else {
                            frappe.msgprint({
                                title: __('Failed to List Domains'),
                                message: r.message ? r.message.message : 'Unknown error',
                                indicator: 'red'
                            });
                        }
                    }
                });
            }, __('Actions'));
        }
    },

    domain_name: function (frm) {
        // Auto-fill domain name as title
        if (frm.doc.domain_name) {
            frm.set_value('domain_name', frm.doc.domain_name.toLowerCase().trim());
        }
    }
});
