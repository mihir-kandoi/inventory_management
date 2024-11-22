# Copyright (c) 2024, Mihir Kandoi and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import now
from frappe.model.document import Document

class Item(Document):
	def after_insert(self):
		for row in self.opening_warehouses:
			frappe.get_doc({
				"doctype": "Stock Ledger Entry",
				"reference_entry": None,
				"date": now(),
				"warehouse": row.warehouse,
				"item": self.name,
				"quantity": row.quantity,
				"action": "In",
				"price": row.price
			}).insert()