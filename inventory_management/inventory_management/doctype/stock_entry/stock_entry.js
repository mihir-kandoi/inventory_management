// Copyright (c) 2024, Mihir Kandoi and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Stock Entry", {
// 	refresh(frm) {

// 	},
// });

frappe.ui.form.on("Stock Entry Data", {
    to(frm, cdt, cdn) {
        frm.set_query('from_field', 'data', () => {
            return {
                filters: [
                    ['parent_warehouse', '!=', ""],
                    ['name1', '!=', locals[cdt][cdn].to]
                ]
            }
        });
    },
    from_field(frm, cdt, cdn) {
        frm.set_query('to', 'data', () => {
            console.log("bye");
            return {
                filters: [
                    ['parent_warehouse', '!=', ""],
                    ['name1', '!=', locals[cdt][cdn].from_field]
                ]
            }
        });
    },
});

frappe.ui.form.on("Stock Entry", {
    setup(frm) {
        frm.set_query('from_field', 'data', () => {
            return {
                filters: [
                    ['parent_warehouse', '!=', ""],
                ]
            }
        });
        frm.set_query('to', 'data', () => {
            return {
                filters: [
                    ['parent_warehouse', '!=', ""],
                ]
            }
        });
    },
    refresh(frm) {
        const value = frm.doc.type;
        frm.get_field('data').grid.toggle_reqd("from_field", value === "Consume" || value === "Transfer");
        frm.get_field('data').grid.toggle_reqd("to", value === "Receipt" || value === "Transfer");
        frm.get_field('data').grid.toggle_enable("from_field", value === "Consume" || value === "Transfer");
        frm.get_field('data').grid.toggle_enable("to", value === "Receipt" || value === "Transfer");
        frm.get_field('data').grid.toggle_reqd("price", value != "Transfer");
        frm.get_field('data').grid.toggle_enable("price", value != "Transfer");
    },
    type(frm) {
        frm.trigger('refresh');
    }
});