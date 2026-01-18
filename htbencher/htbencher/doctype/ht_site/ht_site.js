
frappe.ui.form.on('HT Site', {
    refresh: function (frm) {
        if (!frm.doc.__islocal) {
            frm.add_custom_button(__('Install App'), function () {
                frappe.prompt({
                    label: 'App to Install',
                    fieldname: 'app_name',
                    fieldtype: 'Link',
                    options: 'HT App',
                    reqd: 1
                }, (values) => {
                    frm.call('install_app_on_site', {
                        app_name: values.app_name
                    });
                });
            }, __('Actions'));

            frm.add_custom_button(__('Migrate Site'), function () {
                frappe.confirm('Are you sure you want to migrate this site?', () => {
                    frm.call('migrate_site');
                });
            }, __('Actions'));

            frm.add_custom_button(__('Backup Site'), function () {
                frm.call('backup_site');
            }, __('Actions'));

            // Drop Site Button (Dangerous)
            frm.add_custom_button(__('Drop Site'), function () {
                frappe.warn('Are you sure you want to PERMANENTLY delete this site and its data? This cannot be undone.', () => {
                    // We trust the backend on_trash handler, so we can just delete the doc?
                    // Or call a specific method?
                    // User manual says: "All actions must call official bench commands: bench drop-site"
                    // Our backend 'on_trash' calls 'drop_site_background'. 
                    // So deleting the doc via standard UI is the correct way.
                    // But users prefer a button.
                    frappe.confirm('Please confirm deletion.', () => {
                        frm.delete_doc();
                    });
                });
            }, __('Actions'));
        }
    }
});
