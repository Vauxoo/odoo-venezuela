#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############################################################################
#    Credits:
#    Coded by: Vauxoo C.A.
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
###############################################################################

import time

from openerp.addons import decimal_precision as dp
from openerp.osv import fields, osv
from openerp.tools.translate import _


class account_invoice(osv.osv):

    _inherit = 'account.invoice'

    def _get_inv_from_awil(self, cr, uid, ids, context=None):
        '''
        Returns a list of invoices which are recorded in VAT Withholding Docs
        '''
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        awil_obj = self.pool.get('account.wh.iva.line')
        awil_brws = awil_obj.browse(cr, uid, ids, context=context)
        return [i.invoice_id.id for i in awil_brws if i.invoice_id]

    def _get_inv_from_awi(self, cr, uid, ids, context=None):
        '''
        Returns a list of invoices which are recorded in VAT Withholding Docs
        '''
        res = []
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        awi_obj = self.pool.get('account.wh.iva')
        awi_brws = awi_obj.browse(cr, uid, ids, context=context)
        for awi_brw in awi_brws:
            for awil_brw in awi_brw.wh_lines:
                if awil_brw.invoice_id:
                    res.append(awil_brw.invoice_id.id)
        return res

    def _fnct_get_wh_iva_id(self, cr, uid, ids, name, args, context=None):
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        awil_obj = self.pool.get('account.wh.iva.line')
        awil_ids = awil_obj.search(cr, uid, [('invoice_id', 'in', ids)],
                                   context=context)

        awil_brws = awil_obj.browse(cr, uid, awil_ids, context=context)
        res = {}.fromkeys(ids, False)
        for i in awil_brws:
            if i.invoice_id:
                res[i.invoice_id.id] = i.retention_id.id or False
        return res

    def _retenida(self, cr, uid, ids, name, args, context=None):
        """ Verify whether withholding was applied to the invoice
        """
        res = {}
        if context is None:
            context = {}
        for inv_id in ids:
            res[inv_id] = self.test_retenida(cr, uid, [inv_id])
        return res

    def _get_inv_from_line(self, cr, uid, ids, context=None):
        """ Returns invoice from journal items
        """
        context = context or {}
        move = {}
        for line in self.pool.get('account.move.line').browse(cr, uid, ids):
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

    def _get_inv_from_reconcile(self, cr, uid, ids, context=None):
        """ Return invoice from reconciled lines
        """
        context = context or {}
        move = {}
        for amr_brw in self.pool.get('account.move.reconcile').browse(cr, uid,
                                                                      ids):
            for line in amr_brw.line_partial_ids:
                move[line.move_id.id] = True
            for line in amr_brw.line_id:
                move[line.move_id.id] = True

        invoice_ids = []
        if move:
            invoice_ids = self.pool.get('account.invoice').search(
                cr, uid, [('move_id', 'in', move.keys())], context=context)
        return invoice_ids

    def check_document_date(self, cr, uid, ids, context=None):
        """
        check that the invoice in open state have the document date defined.
        @return True or raise an osv exception.
        """
        context = context or context
        ids = isinstance(ids, (int, long)) and ids or ids[0]
        inv_brw = self.browse(cr, uid, ids, context=context)
        if (inv_brw.type in ('in_invoice', 'in_refund') and
                inv_brw.state == 'open' and not inv_brw.date_document):
            raise osv.except_osv(
                _('Warning'),
                _('The document date can not be empty when the invoice is in'
                  ' open state.'))
        return True

    def check_invoice_dates(self, cr, uid, ids, context=None):
        """
        check that the date document is less or equal than the date invoice.
        @return True or raise and osv exception.
        """
        context = context or context
        ids = isinstance(ids, (int, long)) and ids or ids[0]
        inv_brw = self.browse(cr, uid, ids, context=context)
        if (inv_brw.type in ('in_invoice', 'in_refund') and
                inv_brw.date_document and
                not inv_brw.date_document <= inv_brw.date_invoice):
            raise osv.except_osv(
                _('Warning'),
                _('The document date must be less or equal than the invoice'
                  ' date.'))
        return True

    _columns = {
        'wh_iva': fields.function(
            _retenida, method=True, string='Withhold', type='boolean',
            store={
                'account.invoice': (
                    lambda self, cr, uid, ids, c={}: ids, None, 50),
                'account.move.line': (_get_inv_from_line, None, 50),
                'account.move.reconcile': (_get_inv_from_reconcile, None, 50),
            }, help="The account moves of the invoice have been retention with"
                    " account moves of the payment(s)."),
        'wh_iva_id': fields.function(
            _fnct_get_wh_iva_id, method=True,
            type='many2one', relation='account.wh.iva',
            string='VAT Wh. Document',
            store={
                'account.wh.iva': (_get_inv_from_awi, ['wh_lines'], 50),
                'account.wh.iva.line': (
                    _get_inv_from_awil, ['invoice_id'], 50)},
            help="This is the VAT Withholding Document where this invoice"
                 " is being withheld"),
        'vat_apply': fields.boolean(
            'Exclude this document from VAT Withholding',
            states={'draft': [('readonly', False)]},
            help="This selection indicates whether generate the invoice"
                 " withholding document"),
        'consolidate_vat_wh': fields.boolean(
            'Group wh doc', readonly=True,
            states={'draft': [('readonly', False)]},
            help="This selection indicates to group this invoice in existing"
                 " withholding document"),
    }

    _defaults = {'consolidate_vat_wh': False}

    def copy(self, cr, uid, ids, default=None, context=None):
        """ Initialized fields to the copy a register
        """
        # NOTE: use ids argument instead of id for fix the pylint error W0622.
        # Redefining built-in 'id'
        context = context or {}
        if default is None:
            default = {}
        default = default.copy()
        # TODO: PROPERLY CALL THE WH_IVA_RATE
        default.update({'wh_iva': False, 'wh_iva_id': False,
                        'vat_apply': False})
        return super(account_invoice, self).copy(cr, uid, ids, default,
                                                 context)

    def wh_iva_line_create(self, cr, uid, ids, context=None):
        """ Creates line with iva withholding
        """
        context = context or {}
        wil_obj = self.pool.get('account.wh.iva.line')
        rp_obj = self.pool.get('res.partner')
        inv_brw = self.browse(cr, uid, ids, context=context)
        wh_iva_rate = (
            inv_brw.type in ('in_invoice', 'in_refund') and
            rp_obj._find_accounting_partner(inv_brw.partner_id).wh_iva_rate or
            rp_obj._find_accounting_partner(
                inv_brw.company_id.partner_id).wh_iva_rate)
        values = {'name': inv_brw.name or inv_brw.number,
                  'invoice_id': inv_brw.id,
                  'wh_iva_rate': wh_iva_rate}
        return wil_obj.create(cr, uid, values, context=context)

    def action_wh_iva_supervisor(self, cr, uid, ids, context=None):
        """ Validate the currencys are equal
        """
        context = context or {}
        for inv in self.browse(cr, uid, ids):
            if inv.amount_total == 0.0:
                raise osv.except_osv(
                    _('Invalid Action !'),
                    _('This invoice has total amount %s %s check the'
                        ' products price') % (inv.amount_total,
                                              inv.currency_id.symbol))
        return True

    def action_wh_iva_create(self, cr, uid, ids, context=None):
        """ Create withholding objects """
        context = context or {}
        wh_iva_obj = self.pool.get('account.wh.iva')
        for inv_brw in self.browse(cr, uid, ids, context=context):
            if inv_brw.wh_iva_id:
                if inv_brw.wh_iva_id.state == 'draft':
                    wh_iva_obj.compute_amount_wh(cr, uid,
                                                 [inv_brw.wh_iva_id.id],
                                                 context=context)
                else:
                    raise osv.except_osv(
                        _('Warning !'),
                        _('You have already a withholding doc associate to'
                          ' your invoice, but this withholding doc is not in'
                          ' cancel state.'))
                return True
            else:
                # Create Lines Data
                ret_line_id = self.wh_iva_line_create(cr, uid, inv_brw.id,
                                                      context=context)
                fortnight_wh_id = self.get_fortnight_wh_id(cr, uid, inv_brw.id,
                                                           context=context)
                # Add line to a WH DOC
                if inv_brw.company_id.consolidate_vat_wh and fortnight_wh_id:
                    # Add to an exist WH Doc
                    ret_id = isinstance(fortnight_wh_id, (int, long)) \
                        and fortnight_wh_id or fortnight_wh_id[0]
                    if not ret_id:
                        raise osv.except_osv(_('Error!'),
                                             _('Can\'t find withholding doc'))
                    wh_iva_obj.write(cr, uid, ret_id,
                                     {'wh_lines': [(4, ret_line_id)]},
                                     context=context)
                else:
                    # Create a New WH Doc and add line
                    ret_id = self.create_new_wh_iva(cr, uid, inv_brw.id,
                                                    ret_line_id,
                                                    context=context)
                self.write(cr, uid, [inv_brw.id], {'wh_iva_id': ret_id})
                wh_iva_obj.compute_amount_wh(cr, uid, [ret_id],
                                             context=context)
        return True

    def get_fortnight_wh_id(self, cr, uid, ids, context=None):
        """ Returns the id of the acc.wh.iva in draft state that correspond to
        the invoice fortnight. If not exist return False.
        """
        context = context or {}
        res = []
        ids = isinstance(ids, (int, long)) and [ids] or ids
        wh_iva_obj = self.pool.get('account.wh.iva')
        per_obj = self.pool.get('account.period')
        rp_obj = self.pool.get('res.partner')
        for inv_brw in self.browse(cr, uid, ids, context=context):
            acc_part_id = rp_obj._find_accounting_partner(inv_brw.partner_id)
            inv_period, inv_fortnight = per_obj.find_fortnight(
                cr, uid, inv_brw.date_invoice, context=context)
            ttype = inv_brw.type in ["out_invoice", "out_refund"] \
                and "out_invoice" or "in_invoice"
            acc_wh_ids = wh_iva_obj.search(
                cr, uid, [
                    ('state', '=', 'draft'), ('type', '=', ttype), '|',
                    ('partner_id', '=', acc_part_id.id),
                    ('partner_id', 'child_of', acc_part_id.id),
                    ('period_id', '=', inv_period),
                    ('fortnight', '=', inv_fortnight)], context=context)
            res.append(acc_wh_ids)
        return len(res) == 1 and res[0] or res

    def create_new_wh_iva(self, cr, uid, ids, ret_line_id, context=None):
        """ Create a Withholding VAT document.
        @param ids: only one id.
        @param ret_line_id: account.wh.iva.line id.
        @return id of the new wh vat document created.
        """
        context = context or {}
        wh_iva_obj = self.pool.get('account.wh.iva')
        per_obj = self.pool.get('account.period')
        rp_obj = self.pool.get('res.partner')
        ids = isinstance(ids, (int, long)) and ids or ids[0]
        inv_brw = self.browse(cr, uid, ids, context=context)
        acc_part_id = rp_obj._find_accounting_partner(inv_brw.partner_id)
        if inv_brw.type in ('out_invoice', 'out_refund'):
            acc_id = acc_part_id.property_account_receivable.id
            wh_type = 'out_invoice'
        else:
            acc_id = acc_part_id.property_account_payable.id
            wh_type = 'in_invoice'
            if not acc_id:
                raise osv.except_osv(
                    _('Invalid Action !'),
                    _('You need to configure the partner with'
                      ' withholding accounts!'))
        ret_iva = {
            'name': _('IVA WH - ORIGIN %s' % (inv_brw.number)),
            'type': wh_type,
            'account_id': acc_id,
            'partner_id': acc_part_id.id,
            'period_id': inv_brw.period_id.id,
            'wh_lines': [(4, ret_line_id)],
            'fortnight': per_obj.find_fortnight(
                cr, uid, inv_brw.date_invoice, context=context)[1],
        }
        if inv_brw.company_id.propagate_invoice_date_to_vat_withholding:
            ret_iva['date'] = inv_brw.date_invoice
        return wh_iva_obj.create(cr, uid, ret_iva, context=context)

    def button_reset_taxes_ret(self, cr, uid, ids, context=None):
        """ Recalculate taxes in invoice
        """
        if not context:
            context = {}

        ait_obj = self.pool.get('account.invoice.tax')
        for inv_id in ids:
            amount_tax_ret = {}
            amount_tax_ret = ait_obj.compute_amount_ret(cr, uid, inv_id,
                                                        context)
            for ait_id in amount_tax_ret.keys():
                ait_obj.write(cr, uid, ait_id, amount_tax_ret[ait_id])

        return True

    def button_reset_taxes(self, cr, uid, ids, context=None):
        """ It makes two function calls related taxes reset
        """
        context = context or {}
        super(account_invoice, self).button_reset_taxes(cr, uid, ids, context)
        self.button_reset_taxes_ret(cr, uid, ids, context)

        return True

    def _withholding_partner(self, cr, uid, ids, context=None):
        """ I verify that the provider retains or not
        """
        if context is None:
            context = {}
        obj = self.browse(cr, uid, ids[0], context=context)
        # No VAT withholding Documents are created for customer invoice &
        # refunds
        if obj.type in ('in_invoice', 'in_refund') and \
                self.pool.get('res.partner')._find_accounting_partner(
                    obj.company_id.partner_id).wh_iva_agent:
            return True
        return False

    def _withholdable_tax(self, cr, uid, ids, context=None):
        """ Verify that existing withholding in invoice
        """
        if context is None:
            context = {}
        return any([
            line.tax_id.ret
            for line in self.browse(cr, uid, ids[0],
                                    context=context).tax_line])

    def check_withholdable(self, cr, uid, ids, context=None):
        """ This will test for Refund invoice trying to find out
        if its regarding parent is in the same fortnight.

        return True if invoice is type 'in_invoice'
        return True if invoice is type 'in_refund' and parent_id invoice
                are both in the same fortnight.
        return False otherwise
        """
        per_obj = self.pool.get('account.period')
        if context is None:
            context = {}
        inv_brw = self.browse(cr, uid, ids[0], context=context)
        if inv_brw.type == 'in_invoice':
            return True
        if inv_brw.type == 'in_refund' and inv_brw.parent_id:
            dt_refund = inv_brw.date_invoice or time.strftime('%Y-%m-%d')
            dt_invoice = inv_brw.parent_id.date_invoice
            find_fortnight = per_obj.find_fortnight
            return find_fortnight(cr, uid, date=dt_refund, context=context) \
                == find_fortnight(cr, uid, date=dt_invoice, context=context)
        return False

    def check_wh_apply(self, cr, uid, ids, context=None):
        """ Apply withholding to the invoice
        """
        if context is None:
            context = {}
        invo_brw = self.browse(cr, uid, ids[0], context=context)
        if invo_brw.vat_apply or invo_brw.sin_cred:
            return False
        wh_apply = []
        wh_apply.append(self._withholdable_tax(cr, uid, ids, context=context))
        wh_apply.append(self._withholding_partner(cr, uid, ids,
                                                  context=context))
        return all(wh_apply)

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
        if context is None:
            context = {}
        res = super(account_invoice, self)._get_move_lines(
            cr, uid, ids, to_wh, period_id, pay_journal_id, writeoff_acc_id,
            writeoff_period_id, writeoff_journal_id, date, name,
            context=context)
        if context.get('vat_wh', False):
            invoice = self.browse(cr, uid, ids[0])
            acc_part_id = \
                self.pool.get('res.partner')._find_accounting_partner(
                    invoice.partner_id)

            types = {'out_invoice': -1, 'in_invoice': 1,
                     'out_refund': 1, 'in_refund': -1}
            direction = types[invoice.type]

            for tax_brw in to_wh:
                if 'invoice' in invoice.type:
                    acc = (tax_brw.tax_id.wh_vat_collected_account_id and
                           tax_brw.tax_id.wh_vat_collected_account_id.id or
                           False)
                elif 'refund' in invoice.type:
                    acc = (tax_brw.tax_id.wh_vat_paid_account_id and
                           tax_brw.tax_id.wh_vat_paid_account_id.id or False)
                if not acc:
                    raise osv.except_osv(
                        _('Missing Account in Tax!'),
                        _("Tax [%s] has missing account. Please, fill the"
                          " missing fields") % (tax_brw.tax_id.name,))
                res.append((0, 0, {
                    'debit':
                    direction * tax_brw.amount_ret < 0 and
                    - direction * tax_brw.amount_ret,
                    'credit':
                    direction * tax_brw.amount_ret > 0 and
                    direction * tax_brw.amount_ret,
                    'account_id': acc,
                    'partner_id': acc_part_id.id,
                    'ref': invoice.number,
                    'date': date,
                    'currency_id': False,
                    'name': name
                }))

        return res

    def validate_wh_iva_done(self, cr, uid, ids, context=None):
        """ Method that check if wh vat is validated in invoice refund.
        @params: ids: list of invoices.
        return: True: the wh vat is validated.
                False: the wh vat is not validated.
        """
        context = context or {}
        for inv in self.browse(cr, uid, ids, context=context):
            if inv.type in ('out_invoice', 'out_refund') and not inv.wh_iva_id:
                riva = True
            else:
                riva = (not inv.wh_iva_id and True or
                        inv.wh_iva_id.state in ('done') and True or False)
                if not riva:
                    raise osv.except_osv(
                        _('Error !'),
                        _('The withholding VAT "%s" is not validated!' %
                          inv.wh_iva_id.code))
        return True

    def button_generate_wh_doc(self, cr, uid, ids, context=None):
        ids = isinstance(ids, (int, long)) and [ids] or ids
        rp_obj = self.pool.get('res.partner')
        inv_brw = self.browse(cr, uid, ids, context={})[0]
        view_id = self.pool.get('ir.ui.view').\
            search(cr, uid, [('name', '=', 'account.invoice.wh.iva.customer')])
        context.update({
            'invoice_id': inv_brw.id,
            'type': inv_brw.type,
            'default_partner_id': rp_obj._find_accounting_partner(
                inv_brw.partner_id).id,
            'default_name': inv_brw.name or inv_brw.number,
            'view_id': view_id,
        })
        return {'name': _('Withholding vat customer'),
                'type': 'ir.actions.act_window',
                'res_model': 'account.wh.iva',
                'view_type': 'form',
                'view_id': False,
                'view_mode': 'form',
                'nodestroy': True,
                'target': 'current',
                'domain': "[('type','=',inv_brw.type)]",
                'context': context}

    def action_cancel(self, cr, uid, ids, context=None):
        """ Verify first if the invoice have a non cancel withholding iva doc.
        If it has then raise a error message. """
        context = context or {}
        for inv_brw in self.browse(cr, uid, ids, context=context):
            # print '\n'*3, 'inv_brw.wh_iva_id', inv_brw.wh_iva_id,
            #       'inv_brw.wh_iva_id.state', inv_brw.wh_iva_id.state, '\n'*3
            if ((not inv_brw.wh_iva_id) or (
                    inv_brw.wh_iva_id and
                    inv_brw.wh_iva_id.state == 'cancel')):
                super(account_invoice, self).action_cancel(cr, uid, ids,
                                                           context=context)
            else:
                raise osv.except_osv(
                    _("Error!"),
                    _("You can't cancel an invoice that have non cancel"
                      " withholding document. Needs first cancel the invoice"
                      " withholding document and then you can cancel this"
                      " invoice."))
        return True


class account_invoice_tax(osv.osv):
    _inherit = 'account.invoice.tax'
    _columns = {
        'amount_ret': fields.float(
            'Withholding amount',
            digits_compute=dp.get_precision('Withhold'),
            help="Vat Withholding amount"),
        'base_ret': fields.float(
            'Amount', digits_compute=dp.get_precision('Withhold'),
            help="Amount without tax"),
    }

    def compute_amount_ret(self, cr, uid, invoice_id, context=None):
        """ Calculate withholding amount
        """
        context = context or {}
        res = {}
        inv = self.pool.get('account.invoice').browse(cr, uid, invoice_id,
                                                      context)
        rp_obj = self.pool.get('res.partner')
        acc_part_id = inv.type in ['out_invoice', "out_refund"] and \
            rp_obj._find_accounting_partner(inv.company_id.partner_id) or \
            rp_obj._find_accounting_partner(inv.partner_id)
        wh_iva_rate = acc_part_id.wh_iva_rate

        for ait in inv.tax_line:
            amount_ret = 0.0
            if ait.tax_id.ret:
                amount_ret = (wh_iva_rate and
                              ait.tax_amount * wh_iva_rate / 100.0 or 0.00)
            res[ait.id] = {'amount_ret': amount_ret,
                           'base_ret': ait.base_amount}
        return res
