#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Humberto Arocha           <humberto@openerp.com.ve>
#              Angelica Barrios          <angelicaisabelb@gmail.com>
#              María Gabriela Quilarque  <gabrielaquilarque97@gmail.com>
#              Javier Duran              <javier.duran@netquatro.com>             
#    Planified by: Nhomar Hernandez
#    Finance by: Helados Gilda, C.A. http://heladosgilda.com.ve
#    Audited by: Humberto Arocha humberto@openerp.com.ve
#############################################################################
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
##############################################################################
from osv import osv
from osv import fields
from tools.translate import _
from tools import config
import time
import datetime

class adjustment_book(osv.osv):

    def _get_amount_total(self,cr,uid,ids,name,args,context=None):
        res = {}
        for adj in self.browse(cr,uid,ids,context):
            res[adj.id] = {
                'amount_total': 0.0,
                'amount_untaxed_n_total' : 0.0,
                'amount_with_vat_n_total': 0.0,
                'amount_untaxed_i_total' : 0.0,
                'amount_with_vat_i_total': 0.0,
                'uncredit_fiscal_total'  : 0.0,
                'amount_with_vat_total'  : 0.0,
            }
            for line in adj.adjustment_ids:
                res[adj.id]['amount_total'] += line.amount
                res[adj.id]['amount_untaxed_n_total'] += line.amount_untaxed_n
                res[adj.id]['amount_with_vat_n_total'] += line.amount_with_vat_n
                res[adj.id]['amount_untaxed_i_total'] += line.amount_untaxed_i
                res[adj.id]['amount_with_vat_i_total'] += line.amount_with_vat_i
                res[adj.id]['uncredit_fiscal_total'] += line.uncredit_fiscal
                res[adj.id]['amount_with_vat_total'] += line.amount_with_vat
        return res

    _name='adjustment.book'
    _columns={
        'name':fields.char('Description', size=256,required=True,help="Description of adjustment book"),
        'period_id':fields.many2one('account.period','Period',required=True,help="Period of adjustment book"),
        'adjustment_ids': fields.one2many('adjustment.book.line','adjustment_id','Adjustment Book Line'),
        'note': fields.text('Note',required=True),
        'type': fields.selection([
            ('sale','Sale'),
            ('purchase', 'Purchase'),
            ],'Type', select=True, required=True, help="Type of adjustment book: Sale or Purchase"),
        'amount_total':fields.function(_get_amount_total,multi='all',method=True,digits=(16, int(config['price_accuracy'])),string='Amount Total Withholding VAT',readonly=True,help="Amount Total for adjustment book of invoice"),
        'amount_untaxed_n_total':fields.function(_get_amount_total,multi='all',method=True,digits=(16, int(config['price_accuracy'])),string='Amount Untaxed National',readonly=True,help="Amount Total Untaxed for adjustment book of nacional operations"),
        'amount_with_vat_n_total':fields.function(_get_amount_total,multi='all',method=True,digits=(16, int(config['price_accuracy'])),string='Amount Withheld National',readonly=True,help="Amount Total Withheld for adjustment book of national operations"),
        'amount_untaxed_i_total':fields.function(_get_amount_total,multi='all',method=True,digits=(16, int(config['price_accuracy'])),string='Amount Untaxed International',readonly=True,help="Amount Total Untaxed for adjustment book of internacional operations"),
        'amount_with_vat_i_total':fields.function(_get_amount_total,multi='all',method=True,digits=(16, int(config['price_accuracy'])),string='Amount Withheld International',readonly=True,help="Amount Total Withheld for adjustment book of international operations"),
        'uncredit_fiscal_total':fields.function(_get_amount_total,multi='all',method=True,digits=(16, int(config['price_accuracy'])),string='Sin derecho a credito fiscal',readonly=True,help="Sin derecho a credito fiscal"),
        'amount_with_vat_total':fields.function(_get_amount_total,multi='all',method=True,digits=(16, int(config['price_accuracy'])),string='Amount Withholding VAT Total',readonly=True,help="Amount Total Withholding VAT for adjustment book"),
    }

    _sql_constraints = [
        ('period_id_type_uniq', 'unique (period_id,type)', 'The period and type combination must be unique!')
    ]

adjustment_book()


class adjustment_book_line(osv.osv):
    
    _name='adjustment.book.line'
    _columns={
        'date_accounting': fields.date('Date Accounting', required=True,help="Date accounting for adjustment book"),
        'date_admin': fields.date('Date Administrative',required=True, help="Date administrative for adjustment book"),
        'vat':fields.char('Vat', size=10,required=True,help="Vat of partner for adjustment book"),
        'partner':fields.char('Partner', size=256,required=True,help="Partner for adjustment book"),
        'invoice_number':fields.char('Invoice Number', size=256,required=True,help="Invoice number for adjustment book"),
        'control_number':fields.char('Invoice Control', size=256,required=True,help="Invoice control for adjustment book"),        
        'amount':fields.float('Amount Document at Withholding VAT',digits=(16, int(config['price_accuracy'])),required=True,help="Amount document for adjustment book"),
        'type_doc': fields.selection([
            ('F','Invoice'),
            ('ND', 'Debit Note'),
            ('NC', 'Credit Note'),
            ],'Document Type', select=True, required=True, help="Type of Document for adjustment book: -Invoice(F),-Debit Note(dn),-Credit Note(cn)"),
        'doc_affected':fields.char('Affected Document', size=256,required=True,help="Affected Document for adjustment book"),
        'uncredit_fiscal':fields.float('Sin derecho a Credito Fiscal',digits=(16, int(config['price_accuracy'])),required=True,help="Sin derechoa credito fiscal"),
        'amount_untaxed_n': fields.float('Amount Untaxed',digits=(16, int(config['price_accuracy'])),required=True,help="Amount untaxed for national operations"),
        'percent_with_vat_n': fields.float('% Withholding VAT',digits=(16, int(config['price_accuracy'])),required=True,help="Percent(%) VAT for national operations"),
        'amount_with_vat_n': fields.float('Amount Withholding VAT',digits=(16, int(config['price_accuracy'])),required=True,help="Percent(%) VAT for national operations"),
        'amount_untaxed_i': fields.float('Amount Untaxed',digits=(16, int(config['price_accuracy'])),required=True,help="Amount untaxed for international operations"),
        'percent_with_vat_i': fields.float('% Withholding VAT',digits=(16, int(config['price_accuracy'])),required=True,help="Percent(%) VAT for international operations"),
        'amount_with_vat_i': fields.float('Amount Withholding VAT',digits=(16, int(config['price_accuracy'])),required=True,help="Amount withholding VAT for international operations"),
        'amount_with_vat': fields.float('Amount Withholding VAT Total',digits=(16, int(config['price_accuracy'])),required=True,help="Amount withheld VAT total"),
        'voucher': fields.char('Voucher Withholding VAT', size=256,required=True,help="Voucher Withholding VAT"),
        'adjustment_id':fields.many2one('adjustment.book','Adjustment Book')
    }
    _rec_rame = 'partner'
    
adjustment_book_line()



