# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt
from __future__ import unicode_literals

from frappe import _
from erpnext.accounts.report.item_wise_sales_register.item_wise_sales_register import (
    _execute,
)

from finbyz_einvoice.gst_india.report.gst_sales_register.gst_sales_register import (
    get_additional_table_columns,
    get_column_names,
)


from finbyzerp.finbyzerp.report.item_wise_sales_register import _execute

def execute(filters=None):
	return _execute(filters, additional_table_columns=[
		dict(fieldtype='Data', label='Customer GSTIN', fieldname="customer_gstin", width=120),
		dict(fieldtype='Data', label='Billing Address GSTIN', fieldname="billing_address_gstin", width=140),
		dict(fieldtype='Data', label='Company GSTIN', fieldname="company_gstin", width=120),
		dict(fieldtype='Data', label='Place of Supply', fieldname="place_of_supply", width=120),
		dict(fieldtype='Data', label='Is Reverse Charge', fieldname="is_reverse_charge", width=120),
		dict(fieldtype='Data', label='GST Category', fieldname="gst_category", width=120),
		dict(fieldtype='Data', label='Is Export With GST', fieldname="is_export_with_gst", width=120),
		dict(fieldtype='Data', label='E-Commerce GSTIN', fieldname="ecommerce_gstin", width=130),
		dict(fieldtype='Data', label='HSN Code', fieldname="gst_hsn_code", width=120)
	], additional_query_columns=[
		'customer_gstin',
		'billing_address_gstin',
		'company_gstin',
		'place_of_supply',
		'is_reverse_charge',
		'gst_category',
		'is_export_with_gst',
		'ecommerce_gstin',
		'gst_hsn_code'
	])

def get_conditions(filters, additional_query_columns):
    conditions = ""

    for opts in additional_query_columns:
        if filters.get(opts):
            conditions += f" and {opts}=%({opts})s"

    return conditions
