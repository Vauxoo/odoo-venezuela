# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010 Vauxoo C.A. (http://openerp.com.ve/) All Rights Reserved.
#                    Javier Duran <javier@vauxoo.com> Nhomar Hernandez <nhomar@vauxoo.com>
# 
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from osv import osv
from osv import fields
from tools.translate import _
import time

class report_purchase_byproduct(osv.osv):
    """
    OpenERP Model : report_purchase_byproduct
    """
    
    _name = 'report.purchase.byproduct'
    _description = 'report_purchase_byproduct'
    _auto = False
    _columns = {
        'name':fields.char('Reference', size=64, required=False, readonly=False),
        'date': fields.date('Date'),
        'product_id':fields.many2one('product.product', 'Product', readonly=True, select=True),
        'partner_id': fields.many2one('res.partner', 'Partner', readonly=True, select=True),
        'type': fields.selection([
            ('out_invoice','Customer Invoice'),
            ('in_invoice','Supplier Invoice'),
            ('out_refund','Customer Refund'),
            ('in_refund','Supplier Refund'),
            ],'Type', readonly=True, select=True),
        'invoice_line_price_unit': fields.float('Unit Price', readonly=True),
        'uos_id':fields.many2one('product.uom', 'UOM    ', readonly=True, select=True),
        'invoice_line_quantity': fields.float('Quantity', readonly=True),
        'line_discount': fields.float('Discount', readonly=True),
        'invoice_line_price_sub': fields.float('Sub Total', readonly=True),       
    }

    def init(self, cr):
            cr.execute('''
                create or replace view report_purchase_byproduct as ( SELECT
                    account_invoice_line.id as id,
                    account_invoice.date_invoice as date,
                    account_invoice."reference" AS name,
                    account_invoice."partner_id" AS partner_id,
                    account_invoice_line."product_id" AS product_id,
                    account_invoice."type" AS type,
                    case when account_invoice."type"='in_refund'
                    then
                        account_invoice_line."price_unit"*(-1)
                    else
                        account_invoice_line."price_unit" 
		    end AS invoice_line_price_unit,
		    case when account_invoice."type"='in_refund'
                    then
                        account_invoice_line."price_subtotal"*(-1)
                    else
                        account_invoice_line."price_subtotal" 
		    end AS invoice_line_price_sub,
		    case when account_invoice."type"='in_refund'
                    then
                        account_invoice_line."discount"*(-1)
                    else
                        account_invoice_line."discount" 
		    end AS line_discount,
		    		    case when account_invoice."type"='in_refund'
                    then
                        account_invoice_line."quantity"*(-1)
                    else
                        account_invoice_line."quantity" 
		    end AS invoice_line_quantity,
                    account_invoice_line."uos_id" AS uos_id
                FROM
                    "account_invoice" account_invoice INNER JOIN "account_invoice_line" account_invoice_line ON account_invoice."id" = account_invoice_line."invoice_id"
                INNER JOIN "product_uom" product_uom ON account_invoice_line."uos_id" = product_uom."id"
                INNER JOIN "product_template" product_template ON account_invoice_line."product_id" = product_template."id"
                WHERE
                (account_invoice."type" = 'in_invoice' OR account_invoice."type" = 'in_refund')
                AND
                product_template."type" = 'product'
                AND
                (account_invoice."state" = 'open' OR account_invoice."state" = 'paid')
                order by
                account_invoice_line."product_id",
                account_invoice."number")
            ''')
report_purchase_byproduct()
