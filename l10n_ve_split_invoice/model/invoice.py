# coding: utf-8
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############################################################################
#    Credits:
#    Coded by: nhomar@openerp.com.ve,
#    Planified by: Nhomar Hernandez
#    Finance by: Helados Gilda, C.A. http://heladosgilda.com.ve
#    Audited by: Humberto Arocha humberto@openerp.com.ve
#############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
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

from openerp import models, api, exceptions, _


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def split_invoice(self):
        """
        Split the invoice when the lines exceed the maximum set for the company
        """
        for inv in self:
            if inv.company_id.lines_invoice < 1:
                raise exceptions.except_orm(
                    _('Error !'),
                    _('Please set an invoice lines value in:\n'
                      'Administration->Company->Configuration->Invoice lines'))
            if inv.type in ["out_invoice", "out_refund"]:
                if len(inv.invoice_line) > inv.company_id.lines_invoice:
                    invoice = {}
                    for field in [
                            'name', 'type', 'comment', 'account_id',
                            'supplier_invoice_number', 'date_due',
                            'period_id', 'partner_id', 'payment_term',
                            'currency_id', 'journal_id', 'user_id']:
                        if inv._fields[field].type == 'many2one':
                            invoice[field] = inv[field].id
                        else:
                            invoice[field] = inv[field] or False
                    invoice.update({
                        'state': 'draft',
                        'number': False,
                        'invoice_line': [],
                        'tax_line': [],
                    })
                    new_inv = self.create(invoice)
                    cont = 0
                    lst = inv.invoice_line
                    while cont < inv.company_id.lines_invoice:
                        lst -= inv.invoice_line[cont]
                        cont += 1
                    for il in lst:
                        il.write({'invoice_id': new_inv.id})
                    inv.button_compute(set_total=True)
                    new_inv.button_compute(set_total=True)
#                wf_service.trg_validate(uid, 'account.invoice', inv_id,
#                                        'invoice_open', cr)
        return True

    @api.multi
    def action_date_assign(self):
        """ Return assigned dat
        """
        super(AccountInvoice, self).action_date_assign()
        self.split_invoice()
        return True
