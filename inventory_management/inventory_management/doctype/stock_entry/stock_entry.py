# Copyright (c) 2024, Mihir Kandoi and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import add_to_date
from frappe.model.document import Document

class StockEntry(Document):
	def on_submit(self):
		for row in self.data:
			doc = {
				"doctype": "Stock Ledger Entry",
				"reference_entry": self.name,
				"date": self.date,
				"item": row.item,
				"quantity": row.quantity,
				"price": row.price,
			}
			if self.type == "Receipt":
				receipt(doc, row.to)
			elif self.type == "Consume":
				consume(doc, row)
			else:
				doc["price"] = 0
				consume(doc, row)

				doc["price"] = 0
				doc["date"] = add_to_date(
					date=self.date, as_string=True, as_datetime=True, seconds=1
				) # this is a possibly unacceptable workaround
				receipt(doc, row.to)

	def on_cancel(self):
		frappe.db.delete("Stock Ledger Entry", filters={"reference_entry": self.name})

def receipt(doc, to):
	doc["action"] = "In"
	doc["warehouse"] = to
	frappe.get_doc(doc).insert()

def consume(doc, row):
	if is_negative_stock(row.item, row.from_field, doc["date"], row.quantity):
		frappe.throw("Quantity consumed cannot be higher than balance.")
	else:
		doc["action"] = "Out"
		doc["warehouse"] = row.from_field
		frappe.get_doc(doc).insert()

def is_negative_stock(item, warehouse, date, quantity):
	balance = frappe.db.sql(
		f'''
			SELECT
				item,
				warehouse,
				action,
				date,
				SUM(
					CASE 
						WHEN action = 'In' THEN quantity
						WHEN action = 'Out' THEN -quantity
						ELSE 0
					END
				) AS balance
			FROM
				`tabStock Ledger Entry`
			WHERE
				item=%s AND warehouse=%s and date<%s
			GROUP BY
				item, warehouse
		'''
	, (item, warehouse, date), as_dict=True)
	if balance:
		return quantity > balance[-1]["balance"]
	return True