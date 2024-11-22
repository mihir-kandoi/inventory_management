// Copyright (c) 2024, Mihir Kandoi and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Item", {
// 	refresh(frm) {

// 	},
// });

frappe.ui.form.on('Item', {
    setup(frm) {
        frm.set_query('warehouse', 'opening_warehouses', () => {
            return {
                filters: [
                    ['parent_warehouse', '!=', ""],
                ]
            }
        });
    },
});