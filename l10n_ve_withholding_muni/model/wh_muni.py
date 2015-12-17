# coding: utf-8
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
# Credits######################################################
#    Coded by: Javier Duran <javier@vauxoo.com>
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
##########################################################################

import time

from openerp.addons import decimal_precision as dp
from openerp.osv import fields, osv
from openerp.tools.translate import _


class AccountWhMunici(osv.osv):

    def _get_type(self, cr, uid, context=None):
        """ Return invoice type
        """
        if context is None:
            context = {}
        inv_type = context.get('type', 'in_invoice')
        return inv_type

    def _get_journal(self, cr, uid, context=None):
        """ Return the journal to the journal items that coresspond to local
        retention depending on the invoice
        """
        if context is None:
            context = {}
        type_inv = context.get('type', 'in_invoice')
        type2journal = {'out_invoice': 'mun_sale', 'in_invoice':
                        'mun_purchase'}
        journal_obj = self.pool.get('account.journal')
        res = journal_obj.search(cr, uid, [('type', '=', type2journal.get(
            type_inv, 'mun_purchase'))], limit=1)
        if res:
            return res[0]
        else:
            return False

    def _get_currency(self, cr, uid, context=None):
        """ Return company currency
        """
        if context is None:
            context = {}
        user = self.pool.get('res.users').browse(cr, uid, [uid])[0]
        if user.company_id:
            return user.company_id.currency_id.id
        else:
            return self.pool.get('res.currency').search(
                cr, uid, [('rate', '=', 1.0)])[0]

    def _get_company(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid)
        return user.company_id.id

    _name = "account.wh.munici"
    _description = "Local Withholding"
    _columns = {
        'name': fields.char('Description', size=64, readonly=True,
                            states={'draft': [('readonly', False)]},
                            required=True, help="Description of withholding"),
        'code': fields.char(
            'Code', size=32, readonly=True,
            states={'draft': [('readonly', False)]},
            help="Withholding reference"),
        'number': fields.char(
            'Number', size=32, readonly=True,
            states={'draft': [('readonly', False)]},
            help="Withholding number"),
        'type': fields.selection([
            ('out_invoice', 'Customer Invoice'),
            ('in_invoice', 'Supplier Invoice'),
            ], string='Type', readonly=True,
            default=lambda s: s._get_type(),
            help="Withholding type"),
        'state': fields.selection([
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'),
            ('done', 'Done'),
            ('cancel', 'Cancelled')
            ], string='State', readonly=True, default='draft',
            help="Estado del Comprobante"),
        'date_ret': fields.date('Withholding date', readonly=True,
                                states={'draft': [('readonly', False)]},
                                help="Keep empty to use the current date"),
        'date': fields.date(
            'Date', readonly=True, states={'draft': [('readonly', False)]},
            help="Date"),
        'account_id': fields.many2one(
            'account.account', 'Account', required=True, readonly=True,
            states={'draft': [('readonly', False)]},
            help="The pay account used for this withholding."),
        'period_id': fields.many2one(
            'account.period', 'Force Period', domain=[('state', '<>', 'done')],
            readonly=True, states={'draft': [('readonly', False)]},
            help="Keep empty to use the period of the validation(Withholding"
                 " date) date."),
        'currency_id': fields.many2one(
            'res.currency', 'Currency', required=True, readonly=True,
            states={'draft': [('readonly', False)]},
            default=lambda s: s._get_currency(),
            help="Currency"),
        'partner_id': fields.many2one(
            'res.partner', 'Partner', readonly=True, required=True,
            states={'draft': [('readonly', False)]},
            help="Withholding customer/supplier"),
        'company_id': fields.many2one(
            'res.company', 'Company', required=True,
            default=lambda s: s._get_company(),
            help="Company"),
        'journal_id': fields.many2one(
            'account.journal', 'Journal', required=True, readonly=True,
            states={'draft': [('readonly', False)]},
            default=lambda s: s._get_journal(),
            help="Journal entry"),
        'munici_line_ids': fields.one2many(
            'account.wh.munici.line', 'retention_id',
            'Local withholding lines', readonly=True,
            states={'draft': [('readonly', False)]},
            help="Invoices to will be made local withholdings"),
        'amount': fields.float(
            'Amount', required=False,
            digits_compute=dp.get_precision('Withhold'),
            help="Amount withheld"),
        'move_id': fields.many2one(
            'account.move', 'Account Entry',
            help='account entry for the invoice'),
    }

    _sql_constraints = [
        ('ret_num_uniq', 'unique (number)', 'number must be unique !')
    ]

    def action_cancel(self, cr, uid, ids, context=None):
        """ Call cancel_move and return True
        """
        context = context or {}
        self.cancel_move(cr, uid, ids)
        self.clear_munici_line_ids(cr, uid, ids, context=context)
        return True

    def cancel_move(self, cr, uid, ids, *args):
        """ Delete move lines related with withholding vat and cancel
        """
        ret_brw = self.browse(cr, uid, ids)
        account_move_obj = self.pool.get('account.move')
        for ret in ret_brw:
            if ret.state == 'done':
                for ret_line in ret.munici_line_ids:
                    if ret_line.move_id:
                        account_move_obj.button_cancel(cr, uid,
                                                       [ret_line.move_id.id])
                        account_move_obj.unlink(cr, uid, [ret_line.move_id.id])
            self.write(cr, uid, ret.id, {'state': 'cancel'})
        return True

    def clear_munici_line_ids(self, cr, uid, ids, context=None):
        """ Clear lines of current withholding document and delete wh document
        information from the invoice.
        """
        context = context or {}
        wml_obj = self.pool.get('account.wh.munici.line')
        ai_obj = self.pool.get('account.invoice')
        if ids:
            wml_ids = wml_obj.search(cr, uid, [('retention_id', 'in', ids)],
                                     context=context)
            ai_ids = wml_ids and [wml.invoice_id.id for wml in wml_obj.browse(
                cr, uid, wml_ids, context=context)]
            if ai_ids:
                ai_obj.write(cr, uid, ai_ids, {'wh_muni_id': False},
                             context=context)
            if wml_ids:
                wml_obj.unlink(cr, uid, wml_ids, context=context)
        return True

    def action_confirm(self, cr, uid, ids, context=None):
        """ Verifies the amount withheld and the document is confirmed
        """
        if context is None:
            context = {}
        obj = self.pool.get('account.wh.munici').browse(cr, uid, ids)
        total = 0
        for i in obj[0].munici_line_ids:
            if i.amount >= i.invoice_id.check_total * 0.15:
                raise osv.except_osv(_('Invalid action !'), _(
                    "The line containing the document '%s' looks as if the"
                    " amount withheld was wrong please check.!") % (
                        i.invoice_id.supplier_invoice_number))
            total += i.amount
        self.write(cr, uid, ids, {'amount': total})
        return True

    def action_number(self, cr, uid, ids, *args):
        """ Generate sequence for empty number fields in account_wh_munici records
        """
        obj_ret = self.browse(cr, uid, ids)[0]
        if obj_ret.type == 'in_invoice':
            cr.execute('SELECT id, number '
                       'FROM account_wh_munici '
                       'WHERE id IN (' + ','.join(
                           [str(item) for item in ids]) + ')')

            for (awm_id, number) in cr.fetchall():
                if not number:
                    number = self.pool.get('ir.sequence').get(
                        cr, uid, 'account.wh.muni.%s' % obj_ret.type)
                cr.execute('UPDATE account_wh_munici SET number=%s '
                           'WHERE id=%s', (number, awm_id))
        return True

    def action_done(self, cr, uid, ids, context=None):
        """ The document is done
        """
        if context is None:
            context = {}
        self.action_number(cr, uid, ids)
        self.action_move_create(cr, uid, ids)
        return True

    def action_move_create(self, cr, uid, ids, context=None):
        """ Create movements associated with retention and reconcile
        """
        inv_obj = self.pool.get('account.invoice')
        context = dict(context or {})
        context.update({'muni_wh': True})
        for ret in self.browse(cr, uid, ids):
            for line in ret.munici_line_ids:
                if line.move_id or line.invoice_id.wh_local:
                    raise osv.except_osv(_('Invoice already withhold !'), _(
                        "You must omit the follow invoice '%s' !") % (
                            line.invoice_id.name,))

            acc_id = ret.account_id.id
            if not ret.date_ret:
                self.write(cr, uid, [ret.id], {'date_ret':
                           time.strftime('%Y-%m-%d')})
                ret = self.browse(cr, uid, ret.id, context=context)

            period_id = ret.period_id and ret.period_id.id or False
            journal_id = ret.journal_id.id
            if not period_id:
                period_ids = self.pool.get('account.period').search(cr, uid, [
                    ('date_start', '<=', ret.date_ret or
                     time.strftime('%Y-%m-%d')),
                    ('date_stop', '>=', ret.date_ret or
                     time.strftime('%Y-%m-%d'))])
                if len(period_ids):
                    period_id = period_ids[0]
                else:
                    raise osv.except_osv(
                        _('Warning !'),
                        _("There was not found a fiscal period for this date:"
                          " '%s' please check.!") % (
                            ret.date_ret or time.strftime('%Y-%m-%d')))
            if ret.munici_line_ids:
                for line in ret.munici_line_ids:
                    writeoff_account_id = False
                    writeoff_journal_id = False
                    amount = line.amount
                    name = 'COMP. RET. MUN ' + ret.number
                    ret_move = inv_obj.ret_and_reconcile(
                        cr, uid, [line.invoice_id.id],
                        amount, acc_id, period_id, journal_id,
                        writeoff_account_id, period_id, writeoff_journal_id,
                        ret.date_ret, name, line, context)

                    # make the retencion line point to that move
                    rl = {
                        'move_id': ret_move['move_id'],
                    }
                    lines = [(1, line.id, rl)]
                    self.write(cr, uid, [ret.id], {
                        'munici_line_ids': lines, 'period_id': period_id})
                    inv_obj.write(
                        cr, uid, [line.invoice_id.id], {'wh_muni_id': ret.id})
        return True

    def onchange_partner_id(self, cr, uid, ids, inv_type, partner_id,
                            context=None):
        """ Changing the partner is again determinated accounts and lines retain
        for document
        @param type: invoice type
        @param partner_id: vendor or buyer
        """
        context = context or {}
        acc_id = False
        rp_obj = self.pool.get('res.partner')
        if partner_id:
            acc_part_brw = rp_obj._find_accounting_partner(rp_obj.browse(
                cr, uid, partner_id))
            if inv_type in ('out_invoice', 'out_refund'):
                acc_id = (acc_part_brw.property_account_receivable and
                          acc_part_brw.property_account_receivable.id or False)
            else:
                acc_id = (acc_part_brw.property_account_payable and
                          acc_part_brw.property_account_payable.id or False)
        result = {'value': {
            'account_id': acc_id}
        }
        return result

    def _update_check(self, cr, uid, ids, context=None):
        """ Check if the invoices are selected partner
        """
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        rp_obj = self.pool.get('res.partner')
        for awm_id in ids:
            inv_str = ''
            awm_brw = self.browse(cr, uid, awm_id, context=context)
            for line in awm_brw.munici_line_ids:
                acc_part_brw = rp_obj._find_accounting_partner(
                    line.invoice_id.partner_id)
                if acc_part_brw.id != awm_brw.partner_id.id:
                    inv_str += '%s' % '\n' + (
                        line.invoice_id.name or line.invoice_id.number or '')
            if inv_str:
                raise osv.except_osv(
                    _('Incorrect Invoices !'),
                    _("The following invoices are not from the selected"
                      " partner: %s " % (inv_str,)))

        return True

    def write(self, cr, uid, ids, vals, context=None):
        """ Validate invoices before update records
        """
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        res = super(AccountWhMunici, self).write(cr, uid, ids, vals,
                                                 context=context)
        self._update_check(cr, uid, ids, context=context)
        return res

    def create(self, cr, uid, vals, context=None):
        """ Validate before create record
        """
        context = context or {}
        new_id = super(AccountWhMunici, self).create(cr, uid, vals,
                                                     context=context)
        self._update_check(cr, uid, new_id, context=context)
        return new_id

    def unlink(self, cr, uid, ids, context=None):
        """ Overwrite the unlink method to throw an exception if the
        withholding is not in cancel state."""
        context = context or {}
        for muni_brw in self.browse(cr, uid, ids, context=context):
            if muni_brw.state != 'cancel':
                raise osv.except_osv(
                    _("Invalid Procedure!!"),
                    _("The withholding document needs to be in cancel state"
                      " to be deleted."))
            else:
                super(AccountWhMunici, self).unlink(cr, uid, ids,
                                                    context=context)
        return True

    def confirm_check(self, cr, uid, ids, context=None):
        '''
        Unique method to check if we can confirm the Withholding Document
        '''
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids

        if not self.check_wh_lines(cr, uid, ids, context=context):
            return False
        return True

    def check_wh_lines(self, cr, uid, ids, context=None):
        """ Check that wh muni has withholding lines"""
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        awm_brw = self.browse(cr, uid, ids[0], context=context)
        if not awm_brw.munici_line_ids:
            raise osv.except_osv(
                _("Missing Values !"),
                _("Missing Withholding Lines!"))
        return True


class AccountWhMuniciLine(osv.osv):

    def default_get(self, cr, uid, field_list, context=None):
        """ Default for munici_context field
        """
        # NOTE: use field_list argument instead of fields for fix the pylint
        # error W0621 Redefining name 'fields' from outer scope
        if context is None:
            context = {}
        data = super(AccountWhMuniciLine, self).default_get(cr, uid,
                                                            field_list,
                                                            context)
        self.munici_context = context
        return data

# TODO
# necesito crear el campo y tener la forma de calcular el monto del impuesto
# munici retenido en la factura

    _name = "account.wh.munici.line"
    _description = "Local Withholding Line"
    _columns = {
        'name': fields.char(
            'Description', size=64, required=True,
            help="Local Withholding line Description"),
        'retention_id': fields.many2one(
            'account.wh.munici', 'Local withholding', ondelete='cascade',
            help="Local withholding"),
        'invoice_id': fields.many2one(
            'account.invoice', 'Invoice', required=True, ondelete='set null',
            help="Withholding invoice"),
        'amount': fields.float(
            'Amount', digits_compute=dp.get_precision('Withhold'),
            help='amout to be withhold'),
        'move_id': fields.many2one(
            'account.move', 'Account Entry', readonly=True,
            help="Account Entry"),
        'wh_loc_rate': fields.float(
            'Rate', help="Local withholding rate"),
        'concepto_id': fields.integer(
            'Concept', size=3, default=1,
            help="Local withholding concept"),
    }

    _sql_constraints = [
        ('munici_fact_uniq', 'unique (invoice_id)',
         'The invoice has already assigned in local withholding, you'
         ' cannot assigned it twice!')
    ]

    def onchange_invoice_id(self, cr, uid, ids, invoice_id, wh_loc_rate=3.0,
                            context=None):
        """ Validate that the bill is no longer assigned to retention
        @param invoice_id: invoice id
        """
        if context is None:
            context = {}

        if not invoice_id:
            return {'value': {'amount': 0.0,
                              'wh_loc_rate': 0.0}}
        else:
            res = self.pool.get(
                'account.invoice').browse(cr, uid, invoice_id, context)
            cr.execute('select retention_id '
                       'from account_wh_munici_line '
                       'where invoice_id=%s',
                       (invoice_id,))
            ret_ids = cr.fetchone()
            if bool(ret_ids):
                ret = self.pool.get(
                    'account.wh.munici').browse(cr, uid, ret_ids[0], context)
                raise osv.except_osv(
                    _('Assigned Invoice !'),
                    "The invoice has already assigned in local withholding"
                    " code: '%s' !" % (ret.code,))

            total = res.amount_total * wh_loc_rate / 100.0
            return {'value': {'amount': total,
                              'wh_loc_rate': wh_loc_rate}}
