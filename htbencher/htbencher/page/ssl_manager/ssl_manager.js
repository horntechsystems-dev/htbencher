frappe.provide("htbencher");

frappe.pages['ssl-manager'].on_page_load = function (wrapper) {
    new htbencher.SSLManager(wrapper);
}

htbencher.SSLManager = class SSLManager {
    constructor(wrapper) {
        this.wrapper = $(wrapper);
        this.make();
    }

    make() {
        this.page = frappe.ui.make_app_page({
            parent: this.wrapper,
            title: 'SSL Manager',
            single_column: true
        });

        this.page.main.html(frappe.render_template('ssl_manager', {}));
    }
}
