# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: nhomar@openerp.com.ve,
#    Planified by: Nhomar Hernandez
#    Finance by: Helados Gilda, C.A. http://heladosgilda.com.ve
#    Audited by: Humberto Arocha humberto@openerp.com.ve
#############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
##############################################################################
from osv import osv
from osv import fields
from tools.translate import _
import netsvc

class account_invoice(osv.osv):
    _inherit = 'account.invoice'

    def split_invoice(self, cr, uid, ids):
        '''
        Split the invoice when the lines exceed the maximum set for the company
        '''
        for inv in self.browse(cr, uid, ids):
            inv_id =False
            if inv.company_id.lines_invoice < 1:
                raise osv.except_osv(_('Error !'), _('Please set an invoice lines value in:\nAdministration->Company->Configuration->Invoice lines'))
            if inv.type in ["out_invoice","out_refund"]:
                if len(inv.invoice_line)> inv.company_id.lines_invoice:
                    lst = []
                    invoice = self.read(cr, uid, inv.id, ['name', 'type', 'number', 'reference', 'comment', 'date_due', 'partner_id', 'address_contact_id', 'address_invoice_id', 'partner_contact', 'partner_insite', 'partner_ref', 'payment_term', 'account_id', 'currency_id', 'invoice_line', 'tax_line', 'journal_id', 'period_id','user_id'])
                    invoice.update({
                        'state': 'draft',
                        'number': False,
                        'invoice_line': [],
                        'tax_line': [],
                    })
                    # take the id part of the tuple returned for many2one fields
                    for field in ('address_contact_id', 'address_invoice_id', 'partner_id',
                            'account_id', 'currency_id', 'payment_term', 'journal_id', 'period_id','user_id'):
                        invoice[field] = invoice[field] and invoice[field][0]
                    
                    if hasattr(inv,'sale_ids'):
                        if self.browse(cr,uid,inv.id,context={}).sale_ids:
                            invoice.update({
                                'sale_ids':[(6,0,[i.id for i in self.browse(cr,uid,inv.id,context={}).sale_ids])]
                            })
                        
                    inv_id = self.create(cr, uid, invoice)
                    cont = 0
                    lst = inv.invoice_line
                    while cont < inv.company_id.lines_invoice:
                        lst.pop(0)
                        cont += 1
                    for il in lst:
                        self.pool.get('account.invoice.line').write(cr,uid,il.id,{'invoice_id':inv_id})
                    self.button_compute(cr, uid, [inv.id], set_total=True)
            if inv_id:
                wf_service = netsvc.LocalService("workflow")
                self.button_compute(cr, uid, [inv_id], set_total=True)
#                wf_service.trg_validate(uid, 'account.invoice', inv_id, 'invoice_open', cr)
        return True

    def action_date_assign(self, cr, uid, ids, *args):
        data = super(account_invoice, self).action_date_assign(cr, uid, ids, *args)
        self.split_invoice(cr,uid,ids)
        return True

account_invoice()
