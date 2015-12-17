# coding: utf-8
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

from openerp import api
from openerp.osv import fields, osv
from openerp.tools.translate import _


class AccountInvoice(osv.osv):

    def _get_journal(self, cr, uid, context=None):
        """ Return the journal which is
        used in the current user's company, otherwise
        it does not exist, return false
        """

        context = context or {}
        res = super(AccountInvoice, self)._get_journal(cr, uid,
                                                       context=context)
        if res:
            return res
        type_inv = context.get('type', 'sale')
        if type_inv in ('sale_debit', 'purchase_debit'):
            user = self.pool.get('res.users').browse(cr, uid, uid,
                                                     context=context)
            company_id = context.get('company_id', user.company_id.id)
            journal_obj = self.pool.get('account.journal')
            domain = [('company_id', '=', company_id), ('type', '=', type_inv)]
            res = journal_obj.search(cr, uid, domain, limit=1)
        return res and res[0] or False

    def _unique_invoice_per_partner(self, cr, uid, ids, context=None):
        """ Return false when it is found
        that the bill is not out_invoice or out_refund,
        and it is not unique to the partner.
        """

        if context is None:
            context = {}
        inv_brw = self.browse(cr, uid, ids, context=context)
        ids_ivo = []
        for inv in inv_brw:
            ids_ivo.append(inv.id)
            if inv.type in ('out_invoice', 'out_refund'):
                return True
            inv_ids = (
                inv.nro_ctrl is not '' and inv.nro_ctrl is not False and
                inv.supplier_invoice_number is not False and
                self.search(cr, uid, [
                    '|',
                    ('nro_ctrl', '=', inv.nro_ctrl and
                     inv.nro_ctrl.strip()),
                    ('supplier_invoice_number', '=',
                     inv.supplier_invoice_number and
                     inv.supplier_invoice_number.strip()),
                    ('type', '=', inv.type),
                    ('partner_id', '=', inv.partner_id.id)
                    ], context=context) or [])
            if [True for i in inv_ids if i not in ids_ivo] and inv_ids:
                return False
        return True

    def _get_loc_req(self, cr, uid, context=None):
        """Get if a field is required or not by a Localization
        @param uid: Integer value of the user
        """
        context = context or {}
        res = True
        ru_brw = self.pool.get('res.users').browse(
            cr, uid, uid, context=context)
        rc_obj = self.pool.get('res.company')
        rc_brw = rc_obj.browse(cr, uid, ru_brw.company_id.id, context=context)

        if rc_brw.country_id and rc_brw.country_id.code == 'VE' and \
                rc_brw.printer_fiscal:
            res = False
        return res

    _inherit = 'account.invoice'
    _columns = {
        'nro_ctrl': fields.char(
            'Control Number', size=32, readonly=True,
            states={'draft': [('readonly', False)]},
            help="Number used to manage pre-printed invoices, by law you will"
                 " need to put here this number to be able to declarate on"
                 " Fiscal reports correctly."),
        'sin_cred': fields.boolean(
            'Exclude this document from fiscal book', readonly=False,
            help="Set it true if the invoice is VAT excempt (Tax Exempt)"),
        'date_document': fields.date(
            "Document Date", states={'draft': [('readonly', False)]},
            help="Administrative date, generally is the date printed on"
                 " invoice, this date is used to show in the Purchase Fiscal"
                 " book", select=True),
        'invoice_printer': fields.char(
            'Fiscal printer invoice number', size=64, required=False,
            help="Fiscal printer invoice number, is the number of the invoice"
                 " on the fiscal printer"),
        # TODO: maybe it must be a many2one to declared FiscalPrinter when
        # FiscalV is ready
        'fiscal_printer': fields.char(
            'Fiscal printer number', size=64, required=False,
            help="Fiscal printer number, generally is the id number of the"
                 " printer."),
        'loc_req': fields.boolean(
            string='Required by Localization',
            default=lambda s: s._get_loc_req(),
            help='This fields is for technical use'),
        'z_report': fields.char(string='Report Z', size=64, help=""),
    }

    _constraints = [
        (_unique_invoice_per_partner,
         _('The Document you have been entering for this Partner has already'
           ' been recorded'),
         ['Control Number (nro_ctrl)', 'Reference (reference)']),
    ]

    @api.multi
    def copy(self, default=None):
        """ Allows you to duplicate a record,
        child_ids, nro_ctrl and reference fields are
        cleaned, because they must be unique
        """
        # NOTE: Use argument name ids instead of id for fix the pylint error
        # W0621 Redefining buil-in 'id'
        if default is None:
            default = {}
        default = default.copy()
        default.update({
            'nro_ctrl': None,
            'supplier_invoice_number': None,
            'sin_cred': False,
            # No cleaned in this copy because it is related to the previous
            # document, if previous document says so this too
            'date_document': False,
            'invoice_printer': '',
            'fiscal_printer': '',
            # No cleaned in this copy because it is related to the previous
            # document, if previous document says so this too
            # loc_req':False,
            'z_report': '',
        })
        return super(AccountInvoice, self).copy(default)

    def write(self, cr, uid, ids, vals, context=None):
        context = context or {}
        if vals.get('type') in ('out_invoice', 'out_refund') and \
                vals.get('date_invoice') and not vals.get('date_document'):
            vals['date_document'] = vals['date_invoice']
        return super(AccountInvoice, self).write(cr, uid, ids, vals,
                                                 context=context)


class AccountInvoiceTax(osv.osv):
    _inherit = 'account.invoice.tax'
    _columns = {
        'tax_id': fields.many2one(
            'account.tax', 'Tax', required=False, ondelete='set null',
            help="Tax relation to original tax, to be able to take off all"
                 " data from invoices."),
    }
