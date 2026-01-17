frappe.ui.form.on('HT Server', {
    refresh: function (frm) {
        frm.add_custom_button(__('Ping Server'), function () {
            frm.call({
                doc: frm.doc,
                method: 'ping',
                freeze: true,
                callback: function (r) {
                    if (r.message && r.message.status === 'success') {
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
            });
        }, __('Actions'));
    }
});
