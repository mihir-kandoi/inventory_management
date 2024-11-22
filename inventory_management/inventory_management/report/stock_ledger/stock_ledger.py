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
	columns = get_columns()
	data = get_data()

	return columns, data


def get_columns() -> list[dict]:
	"""Return columns for the report.

	One field definition per column, just like a DocType field definition.
	"""
	return [
		{
			"label": _("Date"),
			"fieldname": "date",
			"fieldtype": "Datetime",
		},
		{
			"label": _("Action"),
			"fieldname": "action",
			"fieldtype": "Select",
		},
		{
			"label": _("Item"),
			"fieldname": "item",
			"fieldtype": "Link",
			"options": "Item"
		},
		{
			"label": _("Warehouse"),
			"fieldname": "warehouse",
			"fieldtype": "Link",
			"options": "Warehouse"
		},
		{
			"label": _("Quantity"),
			"fieldname": "quantity",
			"fieldtype": "Int",
		},
		{
			"label": _("Price"),
			"fieldname": "price",
			"fieldtype": "Float",
		},
		{
			"label": _("Balance"),
			"fieldname": "balance",
			"fieldtype": "Int",
		},
		{
			"label": _("Moving Average Valuation"),
			"fieldname": "mav",
			"fieldtype": "Float",
		}
	]


def get_data() -> list[list]:
	"""
 	Return data for the report.

	The report data is a list of rows, with each row being a list of cell values.
	"""

	result = frappe.db.sql(
		'''
			SELECT
				date,
				action,
				item,
				warehouse,
				quantity,
				price,
				SUM(
					CASE 
						WHEN action = 'In' THEN quantity
						WHEN action = 'Out' THEN -quantity
						ELSE 0
					END
				) OVER (
					PARTITION BY item, warehouse
					ORDER BY date
					ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
				) AS balance
			FROM
				`tabStock Ledger Entry`
			ORDER BY
				date;
		'''
	, as_dict=True)

	return add_mav(result)

def add_mav(data):
	for index, row in enumerate(data):
		if row["balance"] == 0:
			row["mav"] = 0
		else:
			last_entry = get_last_entry(data, index, row["item"], row["warehouse"])
			if not last_entry: # No matching row means first entry for item and warehouse combination in which case MAV will be same as price of item.
				row["mav"] = row["price"] if row["price"] != 0 else data[index - 1]["mav"] # if price is 0 and last entry is None that means item is transferred to warehouse without existing stock of item
			elif row["price"] == 0: # Transfer entry
				row["mav"] = last_entry["mav"] if row["action"] == "Out" else calculate_mav(row, last_entry, data[index - 1]["mav"])
			else: # Receipt or consume entry
				row["mav"] = calculate_mav(row, last_entry, row["price"])
	return data

def calculate_mav(row, last_entry, mav_to_consider):
	prev = last_entry["mav"] * last_entry["balance"] # Value of existing inventory
	curr = mav_to_consider * row["quantity"] # Value of new entry
	return ((prev + curr) if row["action"] == "In" else (prev - curr)) / row["balance"]

def get_last_entry(data, index, item, warehouse):
	"""
	Gets the last entry (entry before current row) with the same warehouse and item.

	Args:
		data (list(dict)): Data returned by frappe.db.sql command using as_dict=True
		index (int): Index of the current row in data
		item (str): Item to be queried
		warehouse (str): Warehouse to be queried

	Returns:
		row (dict or None): The last entry before the given index, item and warehouse or None if not found.
	"""	
	for i in range(index - 1, -1, -1):
		row = data[i]
		if row["item"] == item and row["warehouse"] == warehouse:
			return row
	return None