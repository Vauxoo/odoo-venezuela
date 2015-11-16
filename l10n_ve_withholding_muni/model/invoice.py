# coding: utf-8
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############################################################################
#    Credits:
#    Coded by: Javier Duran <jduran@corvus.com.ve>
#    Planified by: Nhomar Hernandez
#    Audited by: Vauxoo C.A.
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
#############################################################################

from openerp import api
from openerp.osv import fields, osv
from openerp.tools.translate import _


class AccountInvoice(osv.osv):
    _inherit = 'account.invoice'

    @api.multi
    def copy(self, default=None):
        """ Initialized fields to the copy a register
        """
        # NOTE: use ids argument instead of id for fix the pylint error W0622.
        # Redefining built-in 'id'
        default = default or {}
        default = default.copy()
        default.update({'wh_local': False, 'wh_muni_id': False})
        return super(AccountInvoice, self).copy(default)

    def _get_move_lines(self, cr, uid, ids, to_wh, period_id,
                        pay_journal_id, writeoff_acc_id,
                        writeoff_period_id, writeoff_journal_id, date,
                        name, context=None):
        """ Generate move lines in corresponding account
        @param to_wh: whether or not withheld
        @param period_id: Period
        @param pay_journal_id: pay journal of the invoice
        @param writeoff_acc_id: account where canceled
        @param writeoff_period_id: period where canceled
        @param writeoff_journal_id: journal where canceled
        @param date: current date
        @param name: description
        """

        context = context or {}
        res = super(AccountInvoice, self)._get_move_lines(
            cr, uid, ids, to_wh, period_id, pay_journal_id, writeoff_acc_id,
            writeoff_period_id, writeoff_journal_id, date, name,
            context=context)
        rp_obj = self.pool.get('res.partner')
        if context.get('muni_wh', False):
            invoice = self.browse(cr, uid, ids[0])
            acc_part_brw = rp_obj._find_accounting_partner(
                to_wh.invoice_id.partner_id)
            types = {
                'out_invoice': -1,
                'in_invoice': 1,
                'out_refund': 1,
                'in_refund': -1
            }
            direction = types[invoice.type]
            if to_wh.retention_id.type == 'in_invoice':
                acc = acc_part_brw.property_wh_munici_payable and \
                    acc_part_brw.property_wh_munici_payable.id or False
            else:
                acc = acc_part_brw.property_wh_munici_receivable and \
                    acc_part_brw.property_wh_munici_receivable.id or False
            if not acc:
                raise osv.except_osv(
                    _('Missing Local Account in Partner!'),
                    _("Partner [%s] has missing Local account. Please, fill"
                      " the missing field") % (acc_part_brw.name,))
            res.append((0, 0, {
                'debit': direction * to_wh.amount < 0 and
                (-direction * to_wh.amount),
                'credit': direction * to_wh.amount > 0 and
                direction * to_wh.amount,
                'partner_id': acc_part_brw.id,
                'ref': invoice.number,
                'date': date,
                'currency_id': False,
                'name': name,
                'account_id': acc,
            }))
        return res

    def _retenida_munici(self, cr, uid, ids, name, args, context=None):
        """ Check that all is well in the log lines
        """
        context = context or {}
        res = {}
        for inv_id in ids:
            res[inv_id] = self.test_retenida_muni(cr, uid, [inv_id], 'retmun')
        return res

    def test_retenida_muni(self, cr, uid, ids, *args):
        """ Check that all lines having their share account
        """
        type2journal = {'out_invoice': 'mun_sale',
                        'out_refund': 'mun_sale',
                        'in_invoice': 'mun_purchase',
                        'in_refund': 'mun_purchase'}
        type_inv = self.browse(cr, uid, ids[0]).type
        type_journal = type2journal.get(type_inv, 'mun_purchase')
        res = self.ret_payment_get(cr, uid, ids)
        if not res:
            return False
        ok = True

        cr.execute('select l.id'
                   ' from account_move_line l'
                   ' inner join account_journal j on (j.id=l.journal_id)'
                   ' where l.id in (' + ','.join(
                       [str(item) for item in res]) + ') and j.type=' +
                   '\'' + type_journal + '\'')
        ok = ok and bool(cr.fetchone())
        return ok

    def _get_inv_munici_from_line(self, cr, uid, ids, context=None):
        """ Return invoice from journal items
        """
        context = context or {}
        move = {}
        aml_brw = self.pool.get('account.move.line').browse(cr, uid, ids)
        for line in aml_brw:
            if line.reconcile_partial_id:
                for line2 in line.reconcile_partial_id.line_partial_ids:
                    move[line2.move_id.id] = True
            if line.reconcile_id:
                for line2 in line.reconcile_id.line_id:
                    move[line2.move_id.id] = True
        invoice_ids = []
        if move:
            invoice_ids = self.pool.get('account.invoice').search(
                cr, uid, [('move_id', 'in', move.keys())], context=context)
        return invoice_ids

    def _get_inv_munici_from_reconcile(self, cr, uid, ids, context=None):
        """ Return invoice from reconciled lines
        """
        context = context or {}
        move = {}
        amr_brws = self.pool.get('account.move.reconcile').browse(cr, uid, ids)
        for amr_brw in amr_brws:
            for line in amr_brw.line_partial_ids:
                move[line.move_id.id] = True
            for line in amr_brw.line_id:
                move[line.move_id.id] = True

        invoice_ids = []
        if move:
            invoice_ids = self.pool.get('account.invoice').search(
                cr, uid, [('move_id', 'in', move.keys())], context=context)
        return invoice_ids

    def action_cancel(self, cr, uid, ids, context=None):
        """ Verify first if the invoice have a non cancel local withholding doc.
        If it has then raise a error message. """
        context = context or {}
        for inv_brw in self.browse(cr, uid, ids, context=context):
            if not inv_brw.wh_muni_id:
                super(AccountInvoice, self).action_cancel(cr, uid, ids,
                                                          context=context)
            else:
                raise osv.except_osv(
                    _("Error!"),
                    _("You can't cancel an invoice that have non cancel"
                      " Local Withholding Document. Needs first cancel the"
                      " invoice Local Withholding Document and then you can"
                      " cancel this invoice."))
        return True

    _columns = {
        'wh_local': fields.function(
            _retenida_munici, method=True,
            string='Local Withholding', type='boolean',
            store={
                'account.invoice':
                (lambda self, cr, uid, ids, c={}: ids, None, 50),
                'account.move.line': (_get_inv_munici_from_line, None, 50),
                'account.move.reconcile':
                (_get_inv_munici_from_reconcile, None, 50),
            },
            help="The account moves of the invoice have been withheld with \
            account moves of the payment(s)."),
        'wh_muni_id': fields.many2one(
            'account.wh.munici', 'Wh. Municipality',
            readonly=True, help="Withholding muni."),

    }
