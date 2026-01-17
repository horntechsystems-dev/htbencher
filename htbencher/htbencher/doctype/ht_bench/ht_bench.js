frappe.ui.form.on('HT Bench', {
    refresh: function (frm) {

    },
    server: function (frm) {
        if (frm.doc.server) {
            frappe.db.get_doc('HT Server', frm.doc.server).then(server_doc => {
                // Logic to detect if local
                let is_local = false;
                if (["localhost", "127.0.0.1"].includes(server_doc.hostname) || server_doc.server_name.toLowerCase() === "local") {
                    is_local = true;
                }

                frm.set_value('is_remote', is_local ? 0 : 1);
                frm.set_value('hostname', server_doc.hostname);
                frm.set_value('username', server_doc.username);

                // Optional: Set port if available in server_doc (not currently in standard fields but good practice)
                if (server_doc.port) {
                    frm.set_value('port', server_doc.port);
                }
            });
        } else {
            // Reset if cleared?
            frm.set_value('is_remote', 0);
            frm.set_value('hostname', '');
            frm.set_value('username', '');
        }
    }
});
