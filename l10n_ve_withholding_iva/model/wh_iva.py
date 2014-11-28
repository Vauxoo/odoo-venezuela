# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Vauxoo C.A.
#    Planified by: Nhomar Hernandez
#    Audited by: Vauxoo C.A.
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
################################################################################

from openerp.osv import osv, fields
import time
from openerp.tools.translate import _
from openerp.addons import decimal_precision as dp


class account_wh_iva_line_tax(osv.osv):
    _name = 'account.wh.iva.line.tax'


class account_wh_iva_line(osv.osv):
    _name = "account.wh.iva.line"


class account_wh_iva(osv.osv):
    _name = "account.wh.iva"


class account_wh_iva_line_tax(osv.osv):

    def _set_amount_ret(self, cr, uid, id, name, value, arg, ctx=None):
        """ Change withholding amount into iva line
        @param value: new value for retention amount
        """
        if ctx is None:
            ctx = {}
        if not self.browse(cr, uid, id, context=ctx).wh_vat_line_id.retention_id.type == 'out_invoice':
            return False
        sql_str = """UPDATE account_wh_iva_line_tax set
                    amount_ret='%s'
                    WHERE id=%d """ % (value, id)
        cr.execute(sql_str)
        return True

    def _get_amount_ret(self, cr, uid, ids, fieldname, args, context=None):
        """ Return withholding amount
        """
        if context is None:
            context = None
        res = {}

        awilt_brw = self.browse(cr, uid, ids, context=context)

        for each in awilt_brw:
            #~ TODO: THIS NEEDS REFACTORY IN ORDER TO COMPLY WITH THE SALE WITHHOLDING
            res[each.id] = round((each.amount * each.wh_vat_line_id.wh_iva_rate / 100.0) + 0.00000001, 2)
        return res

    _name = 'account.wh.iva.line.tax'
    _columns = {
        'inv_tax_id': fields.many2one('account.invoice.tax', 'Invoice Tax', ondelete='set null', help="Tax Line"),
        'wh_vat_line_id': fields.many2one('account.wh.iva.line', 'VAT Withholding Line', required=True, ondelete='cascade', help="Line withholding VAT"),
        'tax_id': fields.related('inv_tax_id', 'tax_id', type='many2one', relation='account.tax', string='Tax', store=True, select=True, readonly=True, ondelete='set null', help="Tax"),
        'name': fields.related('inv_tax_id', 'name', type='char', string='Tax Name', size=256, store=True, select=True, readonly=True, ondelete='set null', help=" Tax Name"),
        'base': fields.related('inv_tax_id', 'base', type='float', string='Tax Base', store=True, select=True, readonly=True, ondelete='set null', help="Tax Base"),
        'amount': fields.related('inv_tax_id', 'amount', type='float', string='Taxed Amount', store=True, select=True, readonly=True, ondelete='set null', help="Withholding tax amount"),
        'company_id': fields.related('inv_tax_id', 'company_id', type='many2one', relation='res.company', string='Company', store=True, select=True, readonly=True, ondelete='set null', help="Company"),
        'amount_ret': fields.function(
            _get_amount_ret,
            method=True,
            type='float',
            string='Withheld Taxed Amount',
            digits_compute=dp.get_precision('Withhold'),
            store={
                'account.wh.iva.line.tax': (lambda self, cr, uid, ids, c={}: ids, ['amount'], 15)
            },
            fnct_inv=_set_amount_ret,
            help="Vat Withholding amount"),
    }


class account_wh_iva_line(osv.osv):

    def _get_tax_lines(self, cr, uid, tax_id_brw, context=None):
        """ Return dictionary with tax line data
        @param tax_id_brw: tax object
        """
        if context is None:
            context = {}
        rp_obj = self.pool.get('res.partner')
        acc_part_id = rp_obj._find_accounting_partner(tax_id_brw.invoice_id.partner_id)
        return {
            'inv_tax_id': tax_id_brw.id,
            'tax_id': tax_id_brw.tax_id.id,
            'name': tax_id_brw.tax_id.name,
            'base': tax_id_brw.base,
            'amount': tax_id_brw.amount,
            'company_id': tax_id_brw.company_id.id,
            'wh_iva_rate': acc_part_id.wh_iva_rate
        }

    def load_taxes(self, cr, uid, ids, context=None):
        """ Clean and load again tax lines of the withholding voucher
        """
        if context is None:
            context = {}
        awilt_obj = self.pool.get('account.wh.iva.line.tax')
        rp_obj = self.pool.get('res.partner')

        for ret_line in self.browse(cr, uid, ids, context):
            lines = []
            if ret_line.invoice_id:
                rate = ret_line.retention_id.type == 'out_invoice' \
                    and rp_obj._find_accounting_partner(ret_line.invoice_id.company_id.partner_id).wh_iva_rate \
                    or rp_obj._find_accounting_partner(ret_line.invoice_id.partner_id).wh_iva_rate
                self.write(cr, uid, ret_line.id, {'wh_iva_rate': rate})
                tax_lines = awilt_obj.search(cr, uid, [('wh_vat_line_id', '=', ret_line.id)])
                if tax_lines:
                    awilt_obj.unlink(cr, uid, tax_lines)

                tax_ids = [i for i in ret_line.invoice_id.tax_line if i.tax_id and i.tax_id.ret]
                for i in tax_ids:
                    values = self._get_tax_lines(cr, uid, i, context=context)
                    values.update({'wh_vat_line_id': ret_line.id, })
                    del values['wh_iva_rate']
                    lines.append(awilt_obj.create(cr, uid, values, context=context))
        return True

    def _amount_all(self, cr, uid, ids, fieldname, args, context=None):
        """ Return amount total each line
        """
        res = {}
        for ret_line in self.browse(cr, uid, ids, context):
            res[ret_line.id] = {
                'amount_tax_ret': 0.0,
                'base_ret': 0.0
            }
            for line in ret_line.tax_line:
                if ret_line.invoice_id.type not in ('in_refund'):
                    res[ret_line.id]['amount_tax_ret'] += line.amount_ret
                    res[ret_line.id]['base_ret'] += line.base
                else:
                    res[ret_line.id]['amount_tax_ret'] -= line.amount_ret
                    res[ret_line.id]['base_ret'] -= line.base

        return res

    _name = "account.wh.iva.line"
    _description = "Vat Withholding line"
    _columns = {
        'name': fields.char('Description', size=64, required=True, help="Withholding line Description"),
        'retention_id': fields.many2one('account.wh.iva', 'Vat Withholding', ondelete='cascade', help="Vat Withholding"),
        'invoice_id': fields.many2one('account.invoice', 'Invoice', required=True, ondelete='restrict', help="Withholding invoice"),
        'supplier_invoice_number': fields.related('invoice_id', 'supplier_invoice_number', type='char', string='Supplier Invoice Number', size=64, store=True, readonly=True),
        'tax_line': fields.one2many('account.wh.iva.line.tax', 'wh_vat_line_id', string='Taxes', help="Invoice taxes"),
        'amount_tax_ret': fields.function(_amount_all, method=True, digits=(16, 4), string='Wh. tax amount', multi='all', help="Withholding tax amount"),
        'base_ret': fields.function(_amount_all, method=True, digits=(16, 4), string='Wh. amount', multi='all', help="Withholding without tax amount"),
        'move_id': fields.many2one('account.move', 'Account Entry', readonly=True, help="Account entry", ondelete='restrict'),
        'wh_iva_rate': fields.float(string='Withholding Vat Rate', digits_compute= dp.get_precision('Withhold'), help="Vat Withholding rate"),
        'date': fields.related('retention_id', 'date', type='date', relation='account.wh.iva', string='Voucher Date', help='Emission/Voucher/Document date'),
        'date_ret': fields.related('retention_id', 'date_ret', type='date', relation='account.wh.iva', string='Accounting Date', help='Accouting date. Date Withholding')
    }

    _sql_constraints = [
        ('ret_fact_uniq', 'unique (invoice_id)', 'The invoice has already assigned in withholding vat, you cannot assigned it twice!')
    ]

    def invoice_id_change(self, cr, uid, ids, invoice, context=None):
        """ Return invoice data to assign to withholding vat
        @param invoice: invoice for assign a withholding vat
        """
        if context is None:
            context = {}
        if not invoice:
            return {}
        result = {}
        domain = {}
        ok = True
        res = self.pool.get('account.invoice').browse(cr, uid, invoice, context=context)
        cr.execute('select retention_id from account_wh_iva_line where invoice_id=%s', (invoice,))
        ret_ids = cr.fetchone()
        ok = ok and bool(ret_ids)
        if ok:
            ret = self.pool.get('account.wh.iva').browse(cr, uid, ret_ids[0], context)
            raise osv.except_osv('Assigned Invoice !', "The invoice has already assigned in withholding vat code: '%s' !" % (ret.code,))

        result.update({'name': res.name, 'supplier_invoice_number': res.supplier_invoice_number})

        return {'value': result, 'domain': domain}


class account_wh_iva(osv.osv):

    def name_get(self, cr, uid, ids, context):
        if not len(ids):
            return []
        res = []
        for item in self.browse(cr, uid, ids, context):
            if item.number and item.state == 'done':
                res.append((item.id, '%s (%s)' % (item.number, item.name)))
            else:
                res.append((item.id, '%s' % (item.name)))
        return res

    def _amount_ret_all(self, cr, uid, ids, name, args, context=None):
        """ Return withholding amount total each line
        """
        res = {}
        for retention in self.browse(cr, uid, ids, context):
            res[retention.id] = {
                'amount_base_ret': 0.0,
                'total_tax_ret': 0.0
            }
            for line in retention.wh_lines:
                res[retention.id]['total_tax_ret'] += line.amount_tax_ret
                res[retention.id]['amount_base_ret'] += line.base_ret

        return res

    def _get_type(self, cr, uid, context=None):
        """ Return invoice type
        """
        if context is None:
            context = {}
        type = context.get('type', 'in_invoice')
        return type

    def _get_journal(self, cr, uid, context):
        """ Return a iva journal depending of invoice type
        """
        if context is None:
            context = {}
        type_inv = context.get('type', 'in_invoice')
        type2journal = {'out_invoice': 'iva_sale', 'in_invoice': 'iva_purchase'}
        journal_obj = self.pool.get('account.journal')
        res = journal_obj.search(cr, uid, [('type', '=', type2journal.get(type_inv, 'iva_purchase'))], limit=1)
        if res:
            return res[0]
        else:
            return False

    def _get_fortnight(self, cr, uid, context=None):
        """ Return currency to use
        """
        context = context or {}
        dt = time.strftime('%Y-%m-%d')
        return time.strptime(dt, '%Y-%m-%d').tm_mday <= 15 and 'False' or 'True'

    def _get_currency(self, cr, uid, context):
        """ Return currency to use
        """
        user = self.pool.get('res.users').browse(cr, uid, [uid])[0]
        if user.company_id:
            return user.company_id.currency_id.id
        else:
            return self.pool.get('res.currency').search(cr, uid, [('rate', '=', 1.0)])[0]

    _name = "account.wh.iva"
    _description = "Withholding Vat"
    _columns = {
        'name': fields.char('Description', size=64, readonly=True, states={'draft': [('readonly', False)]}, required=True, help="Description of withholding"),
        'code': fields.char('Internal Code', size=32, readonly=True, states={'draft': [('readonly', False)]}, help="Internal withholding reference"),
        'number': fields.char('Number', size=32, readonly=True, states={'draft': [('readonly', False)]}, help="Withholding number"),
        'type': fields.selection([
            ('out_invoice', 'Customer Invoice'),
            ('in_invoice', 'Supplier Invoice'),
        ], 'Type', readonly=True, help="Withholding type"),
        'state': fields.selection([
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'),
            ('done', 'Done'),
            ('cancel', 'Cancelled')
        ], 'State', readonly=True, help="Withholding State"),
        'date_ret': fields.date('Accounting date', readonly=True, states={'draft': [('readonly', False)]}, help="Keep empty to use the current date"),
        'date': fields.date('Voucher Date', readonly=True, states={'draft': [('readonly', False)]}, help="Emission/Voucher/Document Date"),
        'period_id': fields.many2one('account.period', 'Force Period', domain=[('state', '<>', 'done')], readonly=True, states={'draft': [('readonly', False)]}, help="Keep empty to use the period of the validation(Withholding date) date."),
        'account_id': fields.many2one('account.account', 'Account', required=True, readonly=True, states={'draft': [('readonly', False)]}, help="The pay account used for this withholding."),
        'partner_id': fields.many2one('res.partner', 'Partner', readonly=True, required=True, states={'draft': [('readonly', False)]}, help="Withholding customer/supplier"),
        'currency_id': fields.many2one('res.currency', 'Currency', required=True, readonly=True, states={'draft': [('readonly', False)]}, help="Currency"),
        'journal_id': fields.many2one('account.journal', 'Journal', required=True, readonly=True, states={'draft': [('readonly', False)]}, help="Journal entry"),
        'company_id': fields.many2one('res.company', 'Company', required=True, readonly=True, help="Company"),
        'wh_lines': fields.one2many('account.wh.iva.line', 'retention_id', 'Vat Withholding lines', readonly=True, states={'draft': [('readonly', False)]}, help="Vat Withholding lines"),
        'amount_base_ret': fields.function(_amount_ret_all, method=True, digits_compute=dp.get_precision('Withhold'), string='Compute amount', multi='all', help="Compute amount without tax"),
        'total_tax_ret': fields.function(_amount_ret_all, method=True, digits_compute=dp.get_precision('Withhold'), string='Compute amount wh. tax vat', multi='all', help="compute amount withholding tax vat"),
        'fortnight': fields.selection(
            [('False', "First Fortnight"), ('True', "Second Fortnight")],
            string="Fortnight",
            readonly=True, states={"draft": [("readonly", False)]},
            help="Withholding type"),
        'consolidate_vat_wh': fields.boolean('Fortnight Consolidate Wh. VAT',
            help='If set then the withholdings vat generate in a same'
            ' fornight will be grouped in one withholding receipt.'),
        'third_party_id': fields.many2one(
            'res.partner',
            'Third Party Partner',
            help='Third Party Partner'),
    }

    _defaults = {
        'code': lambda self, cr, uid, c: self.wh_iva_seq_get(cr, uid),
        'type': _get_type,
        'state': lambda *a: 'draft',
        'journal_id': _get_journal,
        'currency_id': _get_currency,
        'company_id': lambda self, cr, uid, context:
        self.pool.get('res.users').browse(cr, uid, uid,
                    context=context).company_id.id,
        "fortnight": _get_fortnight,
    }

    def action_cancel(self, cr, uid, ids, context=None):
        """ Call cancel_move and return True
        """
        context = context or {}
        self.cancel_move(cr, uid, ids)
        self.clear_wh_lines(cr, uid, ids, context=context)
        return True

    def cancel_move(self, cr, uid, ids, *args):
        """ Delete move lines related with withholding vat and cancel
        """
        ret_brw = self.browse(cr, uid, ids)
        account_move_obj = self.pool.get('account.move')
        for ret in ret_brw:
            delete = False
            if ret.state == 'done':
                for ret_line in ret.wh_lines:
                    account_move_obj.button_cancel(cr, uid, [ret_line.move_id.id])
                    ret_line.write({'move_id': False})
                    delete = account_move_obj.unlink(cr, uid, [ret_line.move_id.id])
                if delete:
                    ret.write({'state': 'cancel'})
            else:
                ret.write({'state': 'cancel'})
        return True

    def _get_valid_wh(self, cr, uid, amount_ret, amount, wh_iva_rate, offset=0.5, context=None):
        """ This method can be override in a way that
        you can afford your own value for the offset
        @param amount_ret: withholding amount
        @param amount: invoice amount
        @param wh_iva_rate: iva rate
        @param offset: compensation
        """
        if context is None:
            context = {}
        return amount_ret >= amount * (wh_iva_rate - offset) / 100.0 and amount_ret <= amount * (wh_iva_rate + offset) / 100.0

    def check_wh_taxes(self, cr, uid, ids, context=None):
        """ Check that are valid and that amount retention is not greater than amount
        """
        if context is None:
            context = {}
        res = {}
        note = _('Taxes in the following invoices have been miscalculated\n\n')
        error_msg = ''
        for wh_line in self.browse(cr, uid, ids[0]).wh_lines:
            for tax in wh_line.tax_line:
                if not self._get_valid_wh(cr, uid, tax.amount_ret, tax.amount, tax.wh_vat_line_id.wh_iva_rate, context=context):
                    if not res.get(wh_line.id, False):
                        note += _('\tInvoice: %s, %s, %s\n') % (wh_line.invoice_id.name, wh_line.invoice_id.number, wh_line.invoice_id.supplier_invoice_number or '/')
                        res[wh_line.id] = True
                    note += '\t\t%s\n' % tax.name
                if tax.amount_ret > tax.amount:
                    porcent = '%'
                    error_msg += _("The withheld amount: %s(%s%s), must be less than tax amount %s(%s%s).") % (tax.amount_ret, wh_line.wh_iva_rate, porcent, tax.amount, tax.amount * 100, porcent)
        if res and self.browse(cr, uid, ids[0]).type == 'in_invoice':
            raise osv.except_osv(_('Miscalculated Withheld Taxes'), note)
        elif error_msg:
            raise osv.except_osv(_('Invalid action !'), error_msg)
        return True

    def check_vat_wh(self, cr, uid, ids, context=None):
        """ Check whether the invoice will need to be withheld taxes
        """
        obj = self.browse(cr, uid, ids[0])
        if obj.type == 'out_invoice' and (not obj.date or not obj.date_ret):
            raise osv.except_osv(_('Error!'), _('Must indicate: Accounting date and (or) Voucher Date'))
        res = {}
        for wh_line in obj.wh_lines:
            if not wh_line.tax_line:
                res[wh_line.id] = (wh_line.invoice_id.name, wh_line.invoice_id.number, wh_line.invoice_id.supplier_invoice_number)
        if res:
            note = _('The Following Invoices Have not already been withheld:\n\n')
            for i in res:
                note += '* %s, %s, %s\n' % res[i]
            note += _('\nPlease, Load the Taxes to be withheld and Try Again')

            raise osv.except_osv(_('Invoices with Missing Withheld Taxes!'), note)
        return True

    def check_invoice_nro_ctrl(self, cr, uid, ids, context=None):
        """ Method that check if the control number of the invoice is set
        Return: True if the control number is set, and raise an exception
        when is not.
        """
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        obj = self.browse(cr, uid, ids[0])
        res = {}
        for wh_line in obj.wh_lines:
            if not wh_line.invoice_id.nro_ctrl:
                res[wh_line.id] = (wh_line.invoice_id.name, wh_line.invoice_id.number, wh_line.invoice_id.supplier_invoice_number)
        if res:
            note = _('The Following Invoices will not be withheld:\n\n')
            for i in res:
                note += '* %s, %s, %s\n' % res[i]
            note += _('\nPlease, Write the control number and Try Again')

            raise osv.except_osv(_('Invoices with Missing Control Number!'), note)
        return True

    def write_wh_invoices(self, cr, uid, ids, context=None):
        """ Method that writes the wh vat id in sale invoices.
        Return: True: write successfully.
                False: write unsuccessfully.
        """
        inv_obj = self.pool.get('account.invoice')
        obj = self.browse(cr, uid, ids[0])
        if obj.type in ('out_invoice', 'out_refund'):
            for wh_line in obj.wh_lines:
                if not inv_obj.write(cr, uid, [wh_line.invoice_id.id], {'wh_iva_id': obj.id}):
                    return False
        return True

    def _check_partner(self, cr, uid, ids, context=None):
        """ Determine if a given partner is a VAT Withholding Agent
        """
        obj = self.browse(cr, uid, ids[0])
        rp_obj = self.pool.get('res.partner')
        if obj.type in ('out_invoice', 'out_refund'):
            return rp_obj._find_accounting_partner(obj.partner_id).wh_iva_agent
        else:
            return rp_obj._find_accounting_partner(obj.company_id.partner_id).wh_iva_agent

    _constraints = [
        (_check_partner, 'Error ! The partner must be withholding vat agent .', ['partner_id']),
    ]

    _sql_constraints = [
        ('ret_num_uniq', 'unique (number,type,partner_id,company_id)', 'number must be unique by partner and document type!')
    ]

    def write(self, cr, uid, ids, values, context=None):
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        res = super(account_wh_iva, self).write(cr, uid, ids, values, context=context)
        self._partner_invoice_check(cr, uid, ids, context=context)
        return res

    def create(self, cr, uid, values, context=None):
        context = context or {}
        new_id = super(account_wh_iva, self).create(cr, uid, values, context=context)
        self._partner_invoice_check(cr, uid, new_id, context=context)
        return new_id

    def wh_iva_seq_get(self, cr, uid, context=None):
        """ Generate sequences for records of withholding iva
        """
        pool_seq = self.pool.get('ir.sequence')
        cr.execute("select id,number_next,number_increment,prefix,suffix,padding from ir_sequence where code='account.wh.iva' and active=True")
        res = cr.dictfetchone()
        if res:
            if res['number_next']:
                return pool_seq._next(cr, uid, [res['id']])
            else:
                return pool_seq._process(res['prefix']) + pool_seq._process(res['suffix'])
        return False

    def action_number(self, cr, uid, ids, *args):
        """ Update records numbers
        """
        obj_ret = self.browse(cr, uid, ids)[0]
        if obj_ret.type == 'in_invoice':
            cr.execute('SELECT id, number '
                    'FROM account_wh_iva '
                    'WHERE id IN (' + ','.join(map(str, ids)) + ')')

            for (id, number) in cr.fetchall():
                if not number:
                    number = self.pool.get('ir.sequence').get(cr, uid, 'account.wh.iva.%s' % obj_ret.type)
                if not number:
                    raise osv.except_osv(_("Missing Configuration !"),
                        _('No Sequence configured for Supplier VAT Withholding'))

                cr.execute('UPDATE account_wh_iva SET number=%s '
                        'WHERE id=%s', (number, id))
        return True

    def action_date_ret(self, cr, uid, ids, context=None):
        """ Undated records will be assigned the current date
        """
        context = context or {}
        values = {}
        per_obj = self.pool.get('account.period')
        for wh in self.browse(cr, uid, ids, context=context):
            if wh.type in ['in_invoice']:
                values['date_ret'] = wh.company_id.allow_vat_wh_outdated \
                    and wh.date or time.strftime('%Y-%m-%d')
                values['date'] = values['date_ret']
                if not ((wh.period_id.id, wh.fortnight) ==
                        per_obj.find_fortnight(cr, uid,
                                               values['date_ret'],
                                               context=context)):
                    raise osv.except_osv(
                        _("Invalid action !"),
                        _("You have introduced non-valid accounting date. The"
                          "date needs to be in the same withholding period and"
                          " fortnigh."))
            elif wh.type in ['out_invoice']:
                values['date_ret'] = wh.date_ret or time.strftime('%Y-%m-%d')

            if not wh.company_id.allow_vat_wh_outdated and \
                    values['date_ret'] > time.strftime('%Y-%m-%d'):
                error_msg = _(
                    'You have introduced a non valid withholding date (a date \
                    in the future). The withholding date needs to be at least \
                    today or a previous date.')
                raise osv.except_osv(_("Invalid action !"), _(error_msg))

            self.write(cr, uid, [wh.id], values, context=context)
        return True

    def action_move_create(self, cr, uid, ids, context=None):
        """ Create movements associated with retention and reconcile
        """
        inv_obj = self.pool.get('account.invoice')
        user_obj = self.pool.get('res.users')
        per_obj = self.pool.get('account.period')
        if context is None:
            context = {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        context.update({'vat_wh': True,
                        'company_id': user_obj.browse(cr, uid, uid, context=context).company_id.id})
        ret = self.browse(cr, uid, ids[0], context)
        for line in ret.wh_lines:
            if line.move_id or line.invoice_id.wh_iva:
                raise osv.except_osv(_('Invoice already withhold !'),
                _("You must omit the follow invoice '%s' !") %
                    (line.invoice_id.name,))

        acc_id = ret.account_id.id

        period_id = ret.period_id and ret.period_id.id or False
        journal_id = ret.journal_id.id
        if not period_id:
            period_id = per_obj.find(cr, uid, ret.date_ret or time.strftime('%Y-%m-%d'), context=context)
            if not period_id:
                message = _("There are not Periods availables for the pointed day, two options you must verify, 1.- The period is closed, 2.- The period is not created yet for your company")
                raise osv.except_osv(_('Missing Periods!'), message)
            period_id = period_id[0]
        if period_id:
            if ret.wh_lines:
                for line in ret.wh_lines:
                    writeoff_account_id, writeoff_journal_id = False, False
                    amount = line.amount_tax_ret
                    if line.invoice_id.type in ['in_invoice', 'in_refund']:
                        name = 'COMP. RET. IVA ' + ret.number + ' Doc. ' + (line.invoice_id.supplier_invoice_number or '')
                    else:
                        name = 'COMP. RET. IVA ' + ret.number + ' Doc. ' + (line.invoice_id.number or '')
                    ret_move = inv_obj.ret_and_reconcile(cr, uid, [line.invoice_id.id],
                            abs(amount), acc_id, period_id, journal_id, writeoff_account_id,
                        period_id, writeoff_journal_id, ret.date_ret, name, line.tax_line, context)
                    # make the withholding line point to that move
                    rl = {
                        'move_id': ret_move['move_id'],
                    }
                    lines = [(1, line.id, rl)]
                    self.write(cr, uid, [ret.id], {'wh_lines': lines, 'period_id': period_id})

                    if rl and line.invoice_id.type in ['out_invoice', 'out_refund']:
                        inv_obj.write(cr, uid, [line.invoice_id.id], {'wh_iva_id': ret.id})
        return True

    def _withholdable_tax_(self, cr, uid, ids, context=None):
        """ Return lines with withholdable taxes
        """
        if context is None:
            context = {}
        account_invo_obj = self.pool.get('account.invoice')
        acc_id = [line.id for line in account_invo_obj.browse(cr, uid, ids, context=context) if line.tax_line for tax in line.tax_line if tax.tax_id.ret]
        return acc_id

    def on_change_date_ret(self, cr, uid, ids, date_ret, date):
        res = {}
        if date_ret:
            if not date:
                res.update({'date': date_ret})
            obj_per = self.pool.get('account.period')
            per_id = obj_per.find(cr, uid, date_ret)
            res.update({'period_id': per_id and per_id[0]})
        return {'value': res}

    def clear_wh_lines(self, cr, uid, ids, context=None):
        """ Clear lines of current withholding document and delete wh document
        information from the invoice.
        """
        context = context or {}
        wil_obj = self.pool.get('account.wh.iva.line')
        ai_obj = self.pool.get('account.invoice')
        if ids:
            wil_ids = wil_obj.search(cr, uid, [
                ('retention_id', 'in', ids)], context=context)
            ai_ids = wil_ids and [wil.invoice_id.id
                for wil in wil_obj.browse(cr, uid, wil_ids, context=context)]
            ai_ids and ai_obj.write(cr, uid, ai_ids,
                                    {'wh_iva_id': False}, context=context)
            wil_ids and wil_obj.unlink(cr, uid, wil_ids, context=context)

        return True

    def onchange_partner_id(self, cr, uid, ids, type, partner_id,
                            period_id=False, fortnight=False, context=None):
        """ Update the withholding document accounts and the withholding lines
        depending on the partner and another parameters that depend of the type
        of withholdong. If the type is sale will only take into account the
        partner, but if the type is purchase would take into account the period
        and fortnight changes.

        This method delete lines at right moment and unlink/link the
        withholding document to the related invoices.
        @param type: invoice type
        @param partner_id: partner_id at current view
        @param period_id: period_id at current view
        @param fortnight: fortnight at current view
        """
        context = context or {}
        ai_obj = self.pool.get('account.invoice')
        per_obj = self.pool.get('account.period')
        rp_obj = self.pool.get('res.partner')
        values_data = dict()
        acc_id = False
        wh_type = (type in ('out_invoice', 'out_refund')) and 'sale' or 'purchase'

        #~ pull account info
        if partner_id:
            acc_part_id = rp_obj._find_accounting_partner(rp_obj.browse(cr, uid, partner_id))
            if wh_type == 'sale':
                acc_id = acc_part_id.property_account_receivable and acc_part_id.property_account_receivable.id or False
            else:
                acc_id = acc_part_id.property_account_payable and acc_part_id.property_account_payable.id or False
            values_data['account_id'] = acc_id

        #~ clear lines
        self.clear_wh_lines(cr, uid, ids, context=context)

        if not partner_id:
            if wh_type == 'sale':
                return {'value': values_data}
            else:
                if not period_id or not fortnight:
                    return {'value': values_data}

        #~ add lines
        ttype = wh_type == 'sale' and ['out_invoice', 'out_refund'] \
            or ['in_invoice', 'in_refund']
        ai_ids = ai_obj.search(cr, uid, [
            ('state', '=', 'open'), ('wh_iva', '=', False),
            ('wh_iva_id', '=', False), ('type', 'in', ttype),
            '|',
            ('partner_id', '=', acc_part_id.id),
            ('partner_id', 'child_of', acc_part_id.id),
            ('period_id', '=', period_id)],
            context=context)

        if wh_type == 'purchase':
            ai_ids = [
                ai_brw.id
                for ai_brw in ai_obj.browse(cr, uid, ai_ids, context=context)
                if per_obj.find_fortnight(cr, uid, ai_brw.date_invoice,
              context=context) == (period_id, fortnight)]

        ai_ids = self._withholdable_tax_(cr, uid, ai_ids, context=context)
        #~ print 'ai_ids', ai_ids
        if ai_ids:
            values_data['wh_lines'] = \
                [{'invoice_id': inv_brw.id,
                  'name': inv_brw.name or _('N/A'),
                  'wh_iva_rate': rp_obj._find_accounting_partner(inv_brw.partner_id).wh_iva_rate}
                 for inv_brw in ai_obj.browse(cr, uid, ai_ids, context=context)
                 ]
            # TODO: integrate to the dictionary the value like this:
            # """'consolidate_vat_wh': rp_obj._find_accounting_partner(inv_brw.partner_id).consolidate_vat_wh,"""
            # This only applies in purchase.
        return {'value': values_data}

    def _partner_invoice_check(self, cr, uid, ids, context=None):
        """ Verify that the partner associated of the invoice is correct
        @param values: Contain withholding lines, partner id and invoice_id
        """
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        rp_obj = self.pool.get('res.partner')

        for id in ids:
            inv_str = ''
            awi_brw = self.browse(cr, uid, id, context=context)
            for awil_brw in awi_brw.wh_lines:
                acc_part_id = rp_obj._find_accounting_partner(awil_brw.invoice_id.partner_id)
                if acc_part_id.id != awi_brw.partner_id.id:
                    inv_str += '%s' % '\n' + (awil_brw.invoice_id.name or
                        awil_brw.invoice_id.number or '')

            if inv_str:
                raise osv.except_osv(_('Incorrect Invoices !'), _("The following invoices are not from the selected partner: %s ") % (inv_str,))

        return True

    def compute_amount_wh(self, cr, uid, ids, context=None):
        """ Calculate withholding amount each line
        """
        context = context or {}
        awil_obj = self.pool.get('account.wh.iva.line')

        if self.check_wh_lines_fortnights(cr, uid, ids, context=context):
            for retention in self.browse(cr, uid, ids, context=context):
                whl_ids = [line.id for line in retention.wh_lines]
                if whl_ids:
                    awil_obj.load_taxes(cr, uid, whl_ids, context=context)
        return True

    def _dummy_cancel_check(self, cr, uid, ids, context=None):
        '''
        This will be the method that another developer should use to create new
        check on Withholding Document
        Make super to this method and create your own cases
        '''
        return True

    def _check_tax_iva_lines(self, cr, uid, ids, context=None):
        """Check if this IVA WH DOC is being used in a TXT IVA DOC"""
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        til_obj = self.pool.get("txt.iva.line")
        ti_obj = self.pool.get("txt.iva")
        args = [('txt_id.state', '!=', 'draft'), ('voucher_id', 'in', ids)]
        til_ids = til_obj.search(cr, uid, args, context=context)

        if not til_ids:
            return True

        note = _('The Following IVA TXT DOC should be set to Draft before Cancelling this Document\n\n')
        ti_ids = list(set([til_brw.txt_id.id
            for til_brw in til_obj.browse(cr, uid, til_ids, context=context)]))
        for ti_brw in ti_obj.browse(cr, uid, ti_ids, context=context):
            note += '%s\n' % ti_brw.name
        raise osv.except_osv(_("Invalid Procedure!"), note)
        return True

    def cancel_check(self, cr, uid, ids, context=None):
        '''
        Unique method to check if we can cancel the Withholding Document
        '''
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids

        if not self._check_tax_iva_lines(cr, uid, ids, context=context):
            return False
        if not self._dummy_cancel_check(cr, uid, ids, context=context):
            return False
        return True

    def _dummy_confirm_check(self, cr, uid, ids, context=None):
        '''
        This will be the method that another developer should use to create new
        check on Withholding Document
        Make super to this method and create your own cases
        '''
        return True

    def confirm_check(self, cr, uid, ids, context=None):
        '''
        Unique method to check if we can confirm the Withholding Document
        '''
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids

        if not self.check_wh_lines(cr, uid, ids, context=context):
            return False
        if not self.check_wh_lines_fortnights(cr, uid, ids, context=context):
            return False
        if not self.check_invoice_nro_ctrl(cr, uid, ids, context=context):
            return False
        if not self.check_vat_wh(cr, uid, ids, context=context):
            return False
        if not self.check_wh_taxes(cr, uid, ids, context=context):
            return False
        if not self.write_wh_invoices(cr, uid, ids, context=context):
            return False
        if not self._dummy_confirm_check(cr, uid, ids, context=context):
            return False
        return True

    def check_wh_lines(self, cr, uid, ids, context=None):
        """ Check that wh iva has lines to withhold."""
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        awi_brw = self.browse(cr, uid, ids[0], context=context)
        if not awi_brw.wh_lines:
            raise osv.except_osv(
                _("Missing Values !"),
                _("Missing Withholding Lines!!!"))
        return True

    def check_wh_lines_fortnights(self, cr, uid, ids, context=None):
        """ Check that every wh iva line belongs to the wh iva fortnight."""
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        per_obj = self.pool.get('account.period')
        error_msg = str()
        fortnight_str = {'True': ' - Second Fortnight)',
                        'False': ' - First Fortnight)'}
        for awi_brw in self.browse(cr, uid, ids, context=context):
            if awi_brw.type in ['out_invoice']:
                return True
            for awil_brw in awi_brw.wh_lines:
                awil_period_id, awil_fortnight = per_obj.find_fortnight(
                    cr, uid, awil_brw.invoice_id.date_invoice,
                    context=context)
                if awil_period_id != awi_brw.period_id.id or \
                   awil_fortnight != awi_brw.fortnight:
                    error_msg += \
                        (" * Line '" + awil_brw.invoice_id.number +
                         "' belongs to (" + per_obj.browse(cr, uid,
                         awil_period_id, context=context).name +
                         fortnight_str[awil_fortnight] + ".\n")
            if error_msg:
                raise osv.except_osv(
                    _("Invalid action !"),
                    _("Some withholding lines being withheld dont match"
                      " with the withholding document period and"
                      " fortnight.\n\n * Withholding VAT document correspond"
                      " to (" + awi_brw.period_id.name + fortnight_str[
                          awi_brw.fortnight] + ".\n\n" + error_msg))
                return False
            else:
                return True

    def copy(self, cr, uid, id, default=None, context=None):
        """ Update fields when duplicating
        """
        if not default:
            default = {}
        if context is None:
            context = {}
        if self.browse(cr, uid, id, context=context).type == 'in_invoice':
            raise osv.except_osv(_('Alert !'), _('you can not duplicate this document!!!'))

        default.update({
            'state': 'draft',
            'number': False,
            'code': False,
            'wh_lines': [],
            'period_id': False
        })

        return super(account_wh_iva, self).copy(cr, uid, id, default, context)

    def unlink(self, cr, uid, ids, context=None):
        """ Overwrite the unlink method to throw an exception if the
        withholding is not in cancel state."""
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        for awi_brw in self.browse(cr, uid, ids, context=context):
            if awi_brw.state != 'cancel':
                raise osv.except_osv(_("Invalid Procedure!!"),
                    _("The withholding document needs to be in cancel state to be deleted."))
            else:
                self.clear_wh_lines(cr, uid, [awi_brw.id], context)
                super(account_wh_iva, self).unlink(cr, uid, [awi_brw.id], context=context)
        return True
