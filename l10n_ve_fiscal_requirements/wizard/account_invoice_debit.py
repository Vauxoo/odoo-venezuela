# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
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
#
##############################################################################

import ast
import time

from openerp.osv import fields, osv
from openerp.tools.translate import _


class account_invoice_debit(osv.osv_memory):

    """Debits Note from Invoice"""

    _name = "account.invoice.debit"
    _description = "Invoice Debit Note"
    _columns = {
        'date': fields.date(
            'Operation date',
            help='This date will be used as the invoice date for Refund'
                 ' Invoice and Period will be chosen accordingly!'),
        'period': fields.many2one(
            'account.period', 'Force period',
            help='Fiscal period to assign to the invoice. Keep empty to use'
                 ' the period of the current date.'),
        'journal_id': fields.many2one(
            'account.journal', 'Debits Journal',
            help='You can select here the journal to use for the debit note'
                 ' that will be created. If you leave that field empty, it'
                 ' will use the same journal as the current invoice.'),
        'description': fields.char(
            'Description', size=128, required=True,
            help='Name or reference of the invoice'),
        'comment': fields.text(
            'Comment', required=True, help='Additional Information'),
    }

    def _get_journal(self, cr, uid, context=None):
        """ Return partner journal depending of the invoice type
        """
        obj_journal = self.pool.get('account.journal')
        if context is None:
            context = {}
        journal = []
        company_id = self.pool.get('res.users').browse(
            cr, uid, uid, context=context).company_id.id
        company_id = context.get('company_id', company_id)
        if context.get('type', False) in ('out_invoice', 'out_refund'):
            journal = obj_journal.search(
                cr, uid, [('type', '=', 'sale_debit'),
                          ('company_id', '=', company_id)])
        elif context.get('type', False) in ('in_invoice', 'in_refund'):
            journal = obj_journal.search(
                cr, uid, [('type', '=', 'purchase_debit'),
                          ('company_id', '=', company_id)])
        if not journal:
            raise osv.except_osv(
                _('No Debit Journal !'), _("You must define a debit journal"))
        return journal[0]

    _defaults = {
        'date': lambda *a: time.strftime('%Y-%m-%d'),
        'journal_id': _get_journal,
        # filter_refund': 'modify',
    }

    def fields_view_get(self, cr, uid, view_id=None, view_type=False,
                        context=None, toolbar=False, submenu=False):
        """ Change fields position in the view
        """
        if context is None:
            context = {}

        journal_obj = self.pool.get('account.journal')
        res = super(account_invoice_debit, self).fields_view_get(
            cr, uid, view_id=view_id, view_type=view_type, context=context,
            toolbar=toolbar, submenu=submenu)
        # Debit note only from customer o purchase invoice
        # type = context.get('journal_type', 'sale_refund')
        journal_type = context.get('journal_type', 'sale')
        if journal_type in ('sale', 'sale_refund'):
            journal_type = 'sale_debit'
        else:
            journal_type = 'purchase_debit'
        company_id = self.pool.get('res.users').browse(
            cr, uid, uid, context=context).company_id.id
        company_id = context.get('company_id', company_id)
        for field in res['fields']:
            if field == 'journal_id':
                journal_select = journal_obj._name_search(
                    cr, uid, '',
                    [('type', '=', journal_type),
                     ('company_id', '=', company_id)],
                    context=context, limit=None, name_get_uid=1)
                res['fields'][field]['selection'] = journal_select
        return res

    def _get_orig(self, cr, uid, inv, ref, context=None):
        """ Return default origin value
        """
        if context is None:
            context = {}
        nro_ref = ref
        if inv.type == 'out_invoice':
            nro_ref = inv.number
        orig = ('FACT:' + (nro_ref or '') +
                '- DE FECHA:' + (inv.date_invoice or '') +
                (' TOTAL:' + str(inv.amount_total) or ''))
        return orig

    def compute_debit(self, cr, uid, ids, context=None):
        """ Create a debit note
        @param cr: The current row, from the database cursor,
        @param uid: The current user’s ID for security checks,
        @param ids: The account invoice refund’s ID or list of IDs
        """
        inv_obj = self.pool.get('account.invoice')
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
        if context is None:
            context = {}

        form = self.browse(cr, uid, ids[0], context=context)
        created_inv = []
        date = False
        period = False
        description = False

        journal_id = form.journal_id and form.journal_id.id or False
        inv = inv_obj.browse(cr, uid, context.get('active_ids')[0],
                             context=context)
        # TODOK: no seria mejor ids=context.get(active_id)

        company_id = inv.company_id.id
        context.update({'company_id': company_id})

        if inv.state in ['draft', 'proforma2', 'cancel']:
            raise osv.except_osv(
                _('Error !'),
                _('Can not create a debit note from draft/proforma/cancel'
                  ' invoice.'))
        if inv.reconciled in ('cancel', 'modify'):
            raise osv.except_osv(
                _('Error !'),
                _('Can not create a debit note from invoice which is already'
                  ' reconciled, invoice should be unreconciled first. You can'
                  ' only Refund or Debit this invoice'))
        if inv.type not in ['in_invoice', 'out_invoice']:
            raise osv.except_osv(
                _('Error !'),
                _('Can not make a debit note on a refund invoice.'))

        # Check for the form fields

        if form.period:
            period = form.period.id
        else:
            # Take period from the current date
            period = self.pool.get('account.period').find(
                cr, uid, context=context)
            period = period and period[0] or False
            if not period:
                raise osv.except_osv(
                    _('No Pediod Defined'),
                    _('You have been left empty the period field that'
                      ' automatically fill with the current period. However'
                      ' there is not period defined for the current company.'
                      ' Please check in Accounting/Configuration/Periods'))
            self.write(cr, uid, ids, {'period': period}, context=context)

        if not journal_id:
            journal_id = inv.journal_id.id

        if form.date:
            date = form.date
        else:
            # Take current date
            # date = inv.date_invoice
            date = time.strftime('%Y-%m-%d')
        if form.description:
            description = form.description
        else:
            description = inv.name

        # we get original data of invoice to create a new invoice that is the
        # copy of the original
        invoice = inv_obj.read(cr, uid, [inv.id], [
            'name', 'type', 'number', 'supplier_invoice_number',
            'comment', 'date_due', 'partner_id',
            'partner_insite', 'partner_contact',
            'partner_ref', 'payment_term', 'account_id',
            'currency_id', 'invoice_line', 'tax_line',
            'journal_id', 'period_id'], context=context)
        invoice = invoice[0]
        del invoice['id']
        invoice_lines = []
        tax_lines = []
        # Add origin, parent and comment values
        orig = self._get_orig(cr, uid, inv, invoice['supplier_invoice_number'],
                              context)
        invoice.update({
            'type': inv.type,
            'date_invoice': date,
            'state': 'draft',
            'number': False,
            'invoice_line': invoice_lines,
            'tax_line': tax_lines,
            'period_id': period,
            'parent_id': inv.id,
            'name': description,
            'origin': orig,
            'comment': form.comment,
            'journal_id': journal_id
        })
        # take the id part of the tuple returned for many2one fields
        for field in ('partner_id', 'account_id', 'currency_id',
                      'payment_term'):
            invoice[field] = invoice[field] and invoice[field][0]
        # create the new invoice
        inv_id = inv_obj.create(cr, uid, invoice, {})
        # we compute due date
        if inv.payment_term.id:
            data = inv_obj.onchange_payment_term_date_invoice(
                cr, uid, [inv_id], inv.payment_term.id, date)
            if 'value' in data and data['value']:
                inv_obj.write(cr, uid, [inv_id], data['value'])
        created_inv.append(inv_id)
        # we get the view id
        if inv.type in ('out_invoice', 'out_refund'):
            xml_id = 'action_sale_debit_tree'
        else:
            xml_id = 'action_purchase_debit_tree'
        # we get the model
        result = mod_obj.get_object_reference(
            cr, uid, 'l10n_ve_fiscal_requirements', xml_id)
        xml_id = result and result[1] or False
        # we read the act window
        result = act_obj.read(cr, uid, xml_id, context=context)
        # we add the new invoices into domain list
        invoice_domain = ast.literal_eval(result['domain'])
        invoice_domain.append(('id', 'in', created_inv))
        result['domain'] = invoice_domain
        return result

    def invoice_debit(self, cr, uid, ids, context=None):
        """ Call method compute_debit
        """
        if context is None:
            context = {}
        return self.compute_debit(cr, uid, ids, context=context)


account_invoice_debit()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
