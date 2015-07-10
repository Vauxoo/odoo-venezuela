# -*- encoding: utf-8 -*-
###############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (c) 2013 Vauxoo C.A. (http://openerp.com.ve/)
#    All Rights Reserved
###############################################################################
#    Credits:
#    Coded by:  Juan Marzquez (Tecvemar, c.a.) <jmarquez@tecvemar.com.ve>
#               Katherine Zaoral               <katherine.zaoral@vauxoo.com>
#    Planified by:
#                Juan Marquez                  <jmarquez@tecvemar.com.ve>
#                Humberto Arocha               <hbto@vauxoo.com>
#    Audited by: Humberto Arocha               <hbto@vauxoo.com>
###############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
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

from openerp.addons.decimal_precision import decimal_precision as dp
from openerp.osv import fields, osv
from openerp.tools.translate import _


class customs_form(osv.osv):

    _name = 'customs.form'
    _description = ''

    def name_get(self, cr, uid, ids, context=None):
        if not len(ids):
            return []
        res = []
        so_brw = self.browse(cr, uid, ids, context)
        for item in so_brw:
            res.append((item.id,
                        'F86 # %s - %s' % (item.name, item.ref or '')))
        return res

    def _amount_total(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for f86 in self.browse(cr, uid, ids, context=context):
            amount_total = 0.0
            for line in f86.cfl_ids:
                amount_total += line.amount
            res[f86.id] = amount_total
        return res

    def _default_cfl_ids(self, cr, uid, context=None):
        """ Gets default cfl_ids from customs_duty. """
        obj_ct = self.pool.get('customs.duty')
        ct_ids = obj_ct.search(cr, uid, [], context=context)
        res = []
        for cd_id in ct_ids:
            vat = obj_ct.browse(cr, uid, cd_id, context=context)
            res.append({'tax_code': cd_id,
                        'amount': 0.0, 'vat_detail': vat.vat_detail})
        return res

    def _gen_account_move_line(self, company_id, account_id, partner_id, name,
                               debit, credit):
        return (0, 0, {
                'auto': True,
                'company_id': company_id,
                'account_id': account_id,
                'partner_id': partner_id,
                'name': name[:64],
                'debit': debit,
                'credit': credit,
                'reconcile': False,
                })

    _columns = {
        'name': fields.char('Form #', size=16, required=True, readonly=True,
                            states={'draft': [('readonly', False)]}),
        'ref': fields.char('Reference', size=64, required=False, readonly=True,
                           states={'draft': [('readonly', False)]}),
        'date': fields.date('Date', required=True, readonly=True,
                            states={'draft': [('readonly', False)]},
                            select=True),
        'company_id': fields.many2one('res.company', 'Company', required=True,
                                      readonly=True, ondelete='restrict'),
        'broker_id': fields.many2one('res.partner', 'Broker',
                                     change_default=True, readonly=True,
                                     states={'draft': [('readonly', False)]},
                                     ondelete='restrict'),
        'ref_reg': fields.char('Reg. number', size=16, required=False,
                               readonly=True,
                               states={'draft': [('readonly', False)]}),
        'date_reg': fields.date('Reg. date', required=False, readonly=True,
                                states={'draft': [('readonly', False)]},
                                select=True),
        'ref_liq': fields.char('Liq. number', size=16, required=False,
                               readonly=True,
                               states={'draft': [('readonly', False)]}),
        'date_liq': fields.date('liq. date', required=True, readonly=True,
                                states={'draft': [('readonly', False)]},
                                select=True),
        'customs_facility_id': fields.many2one(
            'customs.facility', 'Customs Facility', change_default=True,
            readonly=True, states={'draft': [('readonly', False)]},
            ondelete='restrict'),
        'cfl_ids': fields.one2many('customs.form.line', 'customs_form_id',
                                   'Tax lines', readonly=True,
                                   states={'draft': [('readonly', False)]}),
        'amount_total': fields.function(_amount_total, method=True,
                                        type='float', string='Amount total',
                                        store=False),
        'move_id': fields.many2one('account.move', 'Account move',
                                   ondelete='restrict', select=True,
                                   readonly=True,
                                   help="The move of this entry line."),
        'narration': fields.text('Notes', readonly=False),
        'state': fields.selection([('draft', 'Draft'), ('open', 'Open'),
                                   ('done', 'Done'), ('cancel', 'Cancelled')],
                                  string='State', required=True,
                                  readonly=True),
    }

    _defaults = {
        'date': lambda *a: time.strftime('%Y-%m-%d'),
        'company_id': lambda self, cr, uid, c:
        self.pool.get('res.company')._company_default_get(cr, uid,
                                                          'customs.form',
                                                          context=c),
        'cfl_ids': _default_cfl_ids,
        'state': lambda *a: 'draft',
    }

    _sql_constraints = [
        ('name_uniq', 'UNIQUE(name)', 'The form # must be unique!'),
    ]

    def create_account_move_lines(self, cr, uid, f86, context=None):
        """ Creates the account.move.lines from cfl_ids detail except for
        taxes with "vat_detail", in this case create debits from
        cfl_ids.imex_tax_line and get debit account from account_tax model
        """
        lines = []
        context = context or {}
        company_id = context.get('f86_company_id')
        rp_obj = self.pool.get('res.partner')

        # expenses
        for line in f86.cfl_ids:
            debits = []
            acc_part_brw = rp_obj._find_accounting_partner(
                line.tax_code.partner_id)
            if line.tax_code.vat_detail:
                for vat in line.imex_tax_line:
                    if vat.tax_amount:
                        debits.append(
                            {'account_id': vat.tax_id.account_collected_id.id,
                             'amount': vat.tax_amount,
                             'tax_info': ' (%s)' % vat.tax_id.name})
            else:
                if line.amount:
                    debits.append({'account_id': line.tax_code.account_id.id,
                                   'amount': line.amount, 'tax_info': ''})

            credit_account_id = \
                acc_part_brw.property_account_payable.id

            for debit in debits:
                if not debit['account_id'] or not credit_account_id:
                    raise osv.except_osv(
                        _('Error!'), _('No account found, please check \
                        customs taxes settings (%s)') % line.tax_code.name)
                lines.append(
                    self._gen_account_move_line(
                        company_id, debit['account_id'],
                        acc_part_brw.id, '[%s] %s - %s%s'
                        % (line.tax_code.code, line.tax_code.ref,
                           line.tax_code.name, debit['tax_info']),
                        debit['amount'], 0.0)
                )
            lines.append(self._gen_account_move_line(
                company_id, credit_account_id, acc_part_brw.id,
                'F86 #%s - %s' % (f86.name, line.tax_code.name), 0.0,
                line.amount))

        lines.reverse()  # set real order ;-)
        return lines

    def create_account_move(self, cr, uid, ids, context=None):
        context = context or {}
        so_brw = self.browse(cr, uid, ids, context=context)
        for f86 in so_brw:
            if f86.move_id:  # ~ The move is already done, nothing to do
                return []
        obj_move = self.pool.get('account.move')
        obj_cfg = self.pool.get('customs.form.config')
        company_id = self.pool.get('res.users').browse(
            cr, uid, uid, context=context).company_id.id
        cfg_id = obj_cfg.search(cr, uid, [('company_id', '=', company_id)],
                                context=context)
        if cfg_id:
            f86_cfg = obj_cfg.browse(cr, uid, cfg_id[0], context=context)
        else:
            raise osv.except_osv(_('Error!'),
                                 _('Please set a valid configuration in \
                                 the imex settings'))
        context.update({'f86_company_id': company_id, 'f86_config': f86_cfg})
        move_ids = []
        for f86 in so_brw:
            move = {
                'ref': 'F86 #%s' % f86.name,
                'journal_id': f86_cfg.journal_id.id,
                'date': f86.date_liq,
                'company_id': company_id,
                'state': 'draft',
                'to_check': False,
                'narration': _('Form 86 # %s\n\tReference: %s\n\tBroker: %s')
                % (f86.name, f86.ref or '', f86.broker_id.name or ''),
            }
            lines = self.create_account_move_lines(
                cr, uid, f86, context=context)
            if lines:
                move.update({'line_id': lines})
                move_id = obj_move.create(cr, uid, move, context=context)
                obj_move.post(cr, uid, [move_id], context=context)
                if move_id:
                    move_ids.append(move_id)
                    self.write(cr, uid, f86.id, {'move_id': move_id},
                               context=context)
        return move_ids

    def button_draft(self, cr, uid, ids, context=None):
        context = context or {}
        vals = {'state': 'draft'}
        return self.write(cr, uid, ids, vals, context=context)

    def button_open(self, cr, uid, ids, context=None):
        context = context or {}
        vals = {'state': 'open'}
        return self.write(cr, uid, ids, vals, context=context)

    def button_done(self, cr, uid, ids, context=None):
        context = context or {}
        self.create_account_move(cr, uid, ids, context=context)
        vals = {'state': 'done'}
        return self.write(cr, uid, ids, vals, context=context)

    def button_cancel(self, cr, uid, ids, context=None):
        context = context or {}
        f86 = self.browse(cr, uid, ids[0], context=context)
        f86_move_id = f86.move_id.id if f86 and f86.move_id else False
        vals = {'state': 'cancel', 'move_id': 0}
        if f86_move_id:
            self.pool.get('account.move').unlink(cr, uid, [f86_move_id],
                                                 context=context)
        return self.write(cr, uid, ids, vals, context=context)

    def test_draft(self, cr, uid, ids, *args):
        return True

    def test_open(self, cr, uid, ids, *args):
        ids = isinstance(ids, (int, long)) and [ids] or ids
        for f86 in self.browse(cr, uid, ids, context={}):
            if f86.amount_total <= 0:
                raise osv.except_osv(_('Warning!'),
                                     _('You must indicate a amount'))
            vat_invoices = []  # for tax (vat) related invoices
            for line in f86.cfl_ids:
                if line.vat_detail:
                    vat_total = line.amount
                    for vat in line.imex_tax_line:
                        vat_total -= vat.tax_amount
                        if vat.imex_inv_id.id not in vat_invoices:
                            vat_invoices.append(vat.imex_inv_id.id)
                    if abs(vat_total) > 0.001:
                        raise osv.except_osv(
                            _('Warning!'),
                            _('The vat detail data does not correspond with '
                              'vat amount in line: %s') % line.tax_code.name)
        return True

    def test_done(self, cr, uid, ids, *args):
        return True

    def test_cancel(self, cr, uid, ids, *args):
        if len(ids) != 1:
            raise osv.except_osv(
                _('Error!'),
                _('Multiple operations not allowed'))
        for f86 in self.browse(cr, uid, ids, context=None):
            # Validate account_move.state != draft
            if f86.move_id and f86.move_id.state != 'draft':
                raise osv.except_osv(
                    _('Error!'),
                    _('Can\'t cancel a import while account move state <> \
                    "Draft" (%s)') % f86.move_id.name)
        return True


class customs_form_line(osv.osv):

    _name = 'customs.form.line'
    _description = ''
    _rec_name = 'tax_code'

    _columns = {
        'customs_form_id': fields.many2one('customs.form', 'Customs',
                                           required=True, ondelete='cascade'),
        'tax_code': fields.many2one('customs.duty', 'Tax',
                                    ondelete='restrict', required=True,
                                    readonly=False),
        'amount': fields.float('Amount', required=True,
                               digits_compute=dp.get_precision('Account')),
        'imex_tax_line': fields.one2many(
            'account.invoice.tax', 'cfl_id', 'Vat lines',
            attrs="{'readonly':[('vat_detail','=',True)], \
            'required':[('vat_detail','=',True)]}"),
        'vat_detail': fields.related('tax_code', 'vat_detail', type='boolean',
                                     string='Tax detail', store=False,
                                     readonly=True)
    }

    _defaults = {
    }

    _sql_constraints = [
        ('code_uniq', 'UNIQUE(customs_form_id,tax_code)',
         'The code must be unique! (for this form)'),
    ]
