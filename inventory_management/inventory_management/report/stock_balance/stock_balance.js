// Copyright (c) 2024, Mihir Kandoi and contributors
// For license information, please see license.txt

frappe.query_reports["Stock Balance"] = {
	filters: [
		{
			"fieldname": "display",
			"label": __("Display by"),
			"fieldtype": "Select",
			"options": ["Item", "Warehouse", "Both"],
			"reqd": 1,
		},
	],
};
