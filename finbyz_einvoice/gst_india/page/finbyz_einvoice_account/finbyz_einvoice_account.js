frappe.pages["india-compliance-account"].on_page_load = async function (wrapper) {
    await frappe.require([
        "finbyz_einvoice.bundle.js",
        "finbyz_einvoice.bundle.css",
    ]);

    new finbyz_einvoice.pages.IndiaComplianceAccountPage(wrapper);
};
