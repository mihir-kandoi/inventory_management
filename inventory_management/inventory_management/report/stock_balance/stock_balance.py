# Copyright (c) 2024, Mihir Kandoi and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters: dict | None = None):
	"""Return columns and data for the report.

	This is the main entry point for the report. It accepts the filters as a
	dictionary and should return columns and data. It is called by the framework
	every time the report is refreshed or a filter is updated.
	"""
	columns = get_columns(filters["display"])
	data = get_data(filters["display"])

	return columns, data

def get_columns(display) -> list[dict]:
	"""Return columns for the report.

	One field definition per column, just like a DocType field definition.
	"""

	warehouse = {
		"label": _("Warehouse"),
		"fieldname": "warehouse",
		"fieldtype": "Link",
		"options": "Warehouse"
	}
	item = {
		"label": _("Item"),
		"fieldname": "item",
		"fieldtype": "Link",
		"options": "Item"
	}
	columns = [
		{
			"label": _("Balance"),
			"fieldname": "balance",
			"fieldtype": "Int",
		}
	]
	
	if display == "Item":
		columns.insert(0, item)
	elif display == "Warehouse":
		columns.insert(0, warehouse)
	else:
		columns.insert(0, warehouse)
		columns.insert(0, item)

	return columns

def get_data(display) -> list[list]:
	"""Return data for the report.

	The report data is a list of rows, with each row being a list of cell values.
	"""
	return frappe.db.sql(
		f'''
			SELECT
				item,
				warehouse,
				action,
				SUM(
					CASE 
						WHEN action = 'In' THEN quantity
						WHEN action = 'Out' THEN -quantity
						ELSE 0
					END
				) AS balance
			FROM
				`tabStock Ledger Entry`
			GROUP BY
				{display if display != "Both" else "item, warehouse"}
		'''
	, as_dict=True)