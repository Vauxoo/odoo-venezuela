##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    nhomar@vauxoo.com
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


{
    "name" : "Opening balance Of Products",
    "version" : "0.1",
    "depends" : ["product","product",],
    "author" : "Vauxoo",
    "description" : """This is an informational model tu push on openerp, you imported data on products:
        All this fields will be usables:
default_code	categ_id	standard_price	list_price	cost_method	uom_id	uos_id	mes_type	name	procure_method	type	uom_po_id	supply_method	sale_ok	purchase_ok	property_account_income	property_account_expense	property_stock_account_output	property_stock_account_input	taxes_id	supplier_taxes_id	product_qty
                    """,
    "website" : "http://openerp.com.ve",
    "category" : "Generic Modules/Accounting",
    "init_xml" : [
    ],
    "demo_xml" : [
    ],
    "update_xml" : [
        "costo_inicial_view.xml",
    ],
    "active": False,
    "installable": True,
}
