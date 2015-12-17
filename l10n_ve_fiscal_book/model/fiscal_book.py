# coding: utf-8
###############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############################################################################
#    Credits:
#    Coded by: Humberto Arocha           <hbto@vauxoo.com>
#              Katherine Zaoral          <katherine.zaoral@vauxoo.com>
#    Planified by: Humberto Arocha & Nhomar Hernandez
#    Audited by: Humberto Arocha           <hbto@vauxoo.com>
###############################################################################
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
from openerp.osv import fields, orm, osv
from openerp.tools.translate import _


class FiscalBook(orm.Model):

    def _get_type(self, cr, uid, context=None):
        context = context or {}
        return context.get('type', 'purchase')

    def _get_article_number(self, cr, uid, context=None):
        context = context or {}
        company_brw = self.pool.get('res.users').browse(
            cr, uid, uid, context=context).company_id
        if context.get('type') == 'sale':
            return company_brw.printer_fiscal and '78' or '76'
        else:
            return '75'

    def _get_article_number_types(self, cr, uid, context=None):
        context = context or {}
        company_brw = self.pool.get('res.users').browse(
            cr, uid, uid, context=context).company_id
        if context.get('type') == 'sale':
            if company_brw.printer_fiscal:
                return [('77', 'Article 77'), ('78', 'Article 78')]
            else:
                return [('76', 'Article 76')]
        else:
            return [('75', 'Article 75')]

    def _get_partner_addr(self, cr, uid, ids, field_name, arg, context=None):
        """ It returns Partner address in printable format for the fiscal book
        report.
        @param field_name: field [get_partner_addr]
        """
        context = context or {}
        rp_obj = self.pool.get('res.partner')
        res = {}.fromkeys(ids, 'NO HAY DIRECCION FISCAL DEFINIDA')
        # TODO: ASK: what company, fisal.book.company_id?
        ru_obj = self.pool.get('res.users')
        rc_brw = ru_obj.browse(cr, uid, uid, context=context).company_id
        addr = rp_obj._find_accounting_partner(rc_brw.partner_id)
        for fb_id in ids:
            if addr:
                res[fb_id] = (addr.street or '') + \
                    ' ' + (addr.street2 or '') + ' ' + (addr.zip or '') + ' ' \
                    + (addr.city or '') + ' ' + \
                    (addr.country_id and addr.country_id.name or '') + \
                    ', TELF.:' + (addr.phone or '') or \
                    'NO HAY DIRECCION FISCAL DEFINIDA'
        return res

    def _get_month_year(self, cr, uid, ids, field_name, arg, context=None):
        """ It returns an string with the information of the the year and month
        of the fiscal book.
        @param field_name: field [get_month_year]
        """
        context = context or {}
        months = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                  "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre",
                  "Diciembre"]
        res = {}.fromkeys(ids, '')
        for fb_brw in self.browse(cr, uid, ids, context=context):
            month = months[time.strptime(fb_brw.period_id.date_start,
                                         "%Y-%m-%d")[1] - 1]
            year = time.strptime(fb_brw.period_id.date_start, "%Y-%m-%d")[0]
            res[fb_brw.id] = ("Correspodiente al Mes de " + str(month) +
                              " del año " + str(year))
        return res

    def _get_total_with_iva_sum(self, cr, uid, ids, field_names, arg,
                                context=None):
        """ It returns sum of of all columns total with iva of the fiscal book
        lines.
        @param field_name: ['get_total_with_iva_sum',
                            'get_total_with_iva_imex_sum',
                            'get_total_with_iva_do_sum',
                            'get_total_with_iva_tp_sum',
                            'get_total_with_iva_ntp_sum',
                            ]"""
        context = context or {}
        res = {}.fromkeys(ids, {}.fromkeys(field_names, 0.0))
        op_types = ["imex", "do", "tp", "ntp"]
        for fb_brw in self.browse(cr, uid, ids, context=context):
            for fbl_brw in fb_brw.fbl_ids:
                if fbl_brw.invoice_id or fbl_brw.cf_id:
                    fbl_op_type = fbl_brw.type in ['im', 'ex'] and 'imex' \
                        or fbl_brw.type
                    fbl_index = "get_total_with_iva_" + fbl_op_type + "_sum"
                    res[fb_brw.id][fbl_index] += fbl_brw.total_with_iva

            res[fb_brw.id]['get_total_with_iva_sum'] = \
                sum([res[fb_brw.id]["get_total_with_iva_" + optype + "_sum"]
                     for optype in op_types])
        return res

    def _get_vat_sdcf_sum(self, cr, uid, ids, field_name, arg, context=None):
        """ It returns the SDCF sumation of purchase (imported, domestic) or
        sale (Exports, tax payer, Non-Tax Payer) operations types.
        @param field_name: field ['get_vat_sdcf_sum'] """
        context = context or {}
        res = {}.fromkeys(ids, 0.0)
        for fb_brw in self.browse(cr, uid, ids, context=context):
            res[fb_brw.id] = fb_brw.type == 'purchase' \
                and (fb_brw.imex_sdcf_vat_sum + fb_brw.do_sdcf_vat_sum) \
                or (fb_brw.imex_sdcf_vat_sum + fb_brw.tp_sdcf_vat_sum +
                    fb_brw.ntp_sdcf_vat_sum)
        return res

    def _get_total_tax_credit_debit(self, cr, uid, ids, field_names, arg,
                                    context=None):
        """ It returns sum of of all data in the fiscal book summary table.
        @param field_name: ['get_total_tax_credit_debit_base_sum',
                            'get_total_tax_credit_debit_tax_sum']
        """
        # TODO: summations of all taxes types? only ret types?
        context = context or {}
        res = {}.fromkeys(ids, {}.fromkeys(field_names, 0.0))
        for fb_brw in self.browse(cr, uid, ids, context=context):
            op_types = fb_brw.type == 'purchase' and ['imex', 'do'] \
                or ['imex', 'tp', 'ntp']
            tax_types = ['reduced', 'general', 'additional']

            res[fb_brw.id]['get_total_tax_credit_debit_base_sum'] += \
                sum([getattr(fb_brw, op + '_' + ttax + '_vat_base_sum')
                     for ttax in tax_types
                     for op in op_types])

            res[fb_brw.id]['get_total_tax_credit_debit_tax_sum'] += \
                sum([getattr(fb_brw, op + '_' + ttax + '_vat_tax_sum')
                     for ttax in tax_types
                     for op in op_types])
        return res

    def _get_wh(self, cr, uid, ids, field_names, arg, context=None):
        """ It returns sum of all data in the withholding summary table.
        @param field_name: ['get_total_wh_sum', 'get_previous_wh_sum',
                            'get_wh_sum']"""
        # TODO: this works if its ensuring that that emmision date is always
        # set and and all periods for every past dates are created.
        context = context or {}
        res = {}.fromkeys(ids, {}.fromkeys(field_names, 0.0))
        period_obj = self.pool.get('account.period')
        for fb_brw in self.browse(cr, uid, ids, context=context):
            for fbl_brw in fb_brw.fbl_ids:
                if fbl_brw.iwdl_id:
                    emission_period = period_obj.find(cr, uid,
                                                      fbl_brw.emission_date,
                                                      context=context)
                    if emission_period[0] == fb_brw.period_id.id:
                        res[fb_brw.id]['get_wh_sum'] += \
                            fbl_brw.iwdl_id.amount_tax_ret
                        res[fb_brw.id]['get_wh_debit_credit_sum'] += \
                            fbl_brw.get_wh_debit_credit
                    else:
                        res[fb_brw.id]['get_previous_wh_sum'] += \
                            fbl_brw.iwdl_id.amount_tax_ret
            res[fb_brw.id]['get_total_wh_sum'] = \
                res[fb_brw.id]['get_wh_sum'] + \
                res[fb_brw.id]['get_previous_wh_sum']
        return res

    def _get_do_adjustment_vat_tax_sum(self, cr, uid, ids, field_name, arg,
                                       context=None):
        res = {}
        for fb_brw in self.browse(cr, uid, ids, context=context):
            avts = 0
            for fbl_brw in fb_brw.fbl_ids:
                if fbl_brw.doc_type == 'AJST':
                    avts += fbl_brw.get_wh_vat
            res[fb_brw.id] = avts
        return res

    def _get_company(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid, context)
        return user.company_id.id

    _description = "Venezuela's Sale & Purchase Fiscal Books"
    _name = 'fiscal.book'
    _inherit = ['mail.thread']
    _columns = {
        'name': fields.char('Description', size=256, required=True),
        'company_id': fields.many2one('res.company', 'Company',
                                      help='Company', required=True),
        'period_id': fields.many2one(
            'account.period',
            string='Period',
            required=True,
            help="Book's Fiscal Period. The periods listed are thouse how are"
            " regular periods, i.e. not opening/closing periods."),
        'fortnight': fields.selection(
            [('first', "First Fortnight"), ('second', "Second Fortnight")],
            string="Fortnight", default=None,
            help="Fortnight that applies to the current book."),
        'state': fields.selection([('draft', 'Getting Ready'),
                                   ('confirmed', 'Approved by Manager'),
                                   ('done', 'Seniat Submitted'),
                                   ('cancel', 'Cancel')],
                                  string='Status', required=True,
                                  readonly=True, default='draft'),
        'type': fields.selection([('sale', 'Sale Book'),
                                  ('purchase', 'Purchase Book')],
                                 help="Select Sale for Customers and"
                                 "  Purchase for Suppliers",
                                 string='Book Type', required=True,
                                 default=lambda s: s._get_type()),
        'base_amount': fields.float('Taxable Amount',
                                    help='Amount used as Taxing Base'),
        'tax_amount': fields.float('Taxed Amount',
                                   help='Taxed Amount on Taxing Base'),
        'fbl_ids': fields.one2many('fiscal.book.line', 'fb_id', 'Book Lines',
                                   help='Lines being recorded in the book'),
        'fbt_ids': fields.one2many('fiscal.book.taxes', 'fb_id', 'Tax Lines',
                                   help='Taxes being recorded in the book'),
        'fbts_ids': fields.one2many('fiscal.book.taxes.summary', 'fb_id',
                                    'Tax Summary'),
        'invoice_ids': fields.one2many('account.invoice', 'fb_id', 'Invoices',
                                       help="Invoices being recorded in a"
                                       " Fiscal Book"),
        'issue_invoice_ids': fields.one2many('account.invoice', 'issue_fb_id',
                                             'Issue Invoices',
                                             help="Invoices that are in"
                                             " pending state cancel or draft"),
        'iwdl_ids': fields.one2many('account.wh.iva.line', 'fb_id',
                                    'Vat Withholdings',
                                    help="Vat Withholdings being recorded"
                                    " in a Fiscal Book"),
        'cf_ids': fields.one2many('customs.form', 'fb_id', 'Customs Form',
                                  help="Customs Form being recorded in the"
                                  " Fiscal Book"),
        'abl_ids': fields.one2many('adjustment.book.line', 'fb_id',
                                   'Adjustment Lines',
                                   help="Adjustment Lines being recorded in "
                                   " a Fiscal Book"),
        'note': fields.text('Note'),
        'article_number': fields.selection(
            _get_article_number_types,
            string="Article Number",
            required=True,
            default=lambda s: s._get_article_number(),
            help="Article number describing the fiscal book special features"
                 " according to the Venezuelan RLIVA statement for fiscal"
                 " accounting books. Options:"
                 " - Art. 75: Pruchase Book."
                 " - Art. 76: Sale Book. Reflects every individual operation"
                 " detail."
                 " - Art. 77: Sale Book. Groups Non-Tax Payer operations in"
                 " one "
                 " consolidated line. Only fiscal billing."
                 " - Art. 78: Sale Book. Hybrid for 76 and 77 article. Show"
                 " automatic and mechanized operations in individual way, and "
                 " groups fiscal billing operationss in one consolidated"
                 " line."),

        # Withholding fields
        'get_wh_sum': fields.function(
            _get_wh,
            type="float", method=True, store=True, multi="get_wh",
            string="Current Period Withholding",
            help="Used at"
            " 1. Totalization row in Fiscal Book Line block at Withholding"
            " VAT Column"
            " 2. Second row at the Withholding Summary block"),
        'get_previous_wh_sum': fields.function(
            _get_wh,
            type="float", method=True, store=True, multi="get_wh",
            string="Previous Period Withholding",
            help="First row at the Withholding Summary block"),
        'get_total_wh_sum': fields.function(
            _get_wh,
            type="float", method=True, store=True, multi="get_wh",
            string="VAT Withholding Sum",
            help="Totalization row at the Withholding Summary block"),
        'get_wh_debit_credit_sum': fields.function(
            _get_wh,
            type="float", method=True, store=True, multi="get_wh",
            string="Based Tax Debit Sum",
            help="Totalization row in Fiscal Book Line block at"
            " Based Tax Debit Column"),

        # Printable report data
        'get_partner_addr': fields.function(
            _get_partner_addr,
            type="text", method=True,
            help='Partner address printable format'),
        'get_month_year': fields.function(
            _get_month_year,
            type="text", method=True,
            help='Year and Month ot the Fiscal book period'),

        # Totalization fields for all type of transactions
        'get_total_with_iva_sum': fields.function(
            _get_total_with_iva_sum,
            type="float", method=True, store=True,
            multi="get_total_with_iva",
            string='Total amount with VAT',
            help="Total with VAT Sum (Import/Export, Domestic, Tax Payer and"
            " Non-Tax Payer"),
        'get_vat_sdcf_sum': fields.function(
            _get_vat_sdcf_sum,
            type="float", method=True, store=True,
            string="Exempt and SDCF Tax Sum",
            help="Exempt and Non entitled to tax credit totalization. Sum of"
            " SDCF and Exempt Tax Totalization columns for all transaction"
            " types"),
        'get_total_tax_credit_debit_base_sum': fields.function(
            _get_total_tax_credit_debit,
            type="float", method=True, store=True,
            multi="get_total_tax_credit_debit",
            string="Tax Credit Total Base Amount",
            help="Uses at 1. purchase: total row at summary taxes."
            " 2. sales: row at summary taxes."),
        'get_total_tax_credit_debit_tax_sum': fields.function(
            _get_total_tax_credit_debit,
            type="float", method=True, store=True,
            multi="get_total_tax_credit_debit",
            string="Tax Credit Total Tax Amount"),
        'do_sdcf_and_exempt_sum': fields.float(
            digits_compute=dp.get_precision('Account'),
            string="Domestic Untaxed VAT Sum",
            help="SDCF and Exempt sum for domestict transanctions."
            " At Sale book represent the sum of Tax Payer and Non-Tax Payer"
            " transactions."),

        # Totalization fields for international transactions
        'get_total_with_iva_imex_sum': fields.function(
            _get_total_with_iva_sum,
            type="float", method=True, store=True,
            multi="get_total_with_iva",
            string="Total amount with VAT",
            help="Imported/Exported Total with VAT Totalization"),
        'imex_vat_base_sum': fields.float(
            digits_compute=dp.get_precision('Account'),
            string="International Taxable Amount",
            help="Sum of International Tax Base Amounts (reduced, general"
            " and additional). Used at 2nd row in thw Sale book's summary"
            " with Exports Sales title"),
        'imex_exempt_vat_sum': fields.float(
            digits_compute=dp.get_precision('Account'),
            string="Exempt Tax",
            help="Import/Export Exempt Tax Totalization: Sum of Exempt"
            " column for international transactions"),
        'imex_sdcf_vat_sum': fields.float(
            digits_compute=dp.get_precision('Account'),
            string="SDCF Tax",
            help="Import/Export SDCF Tax Totalization: Sum of SDCF column"
            " for international transactions"),
        'imex_general_vat_base_sum': fields.float(
            digits_compute=dp.get_precision('Account'),
            string="General VAT Taxable Amount",
            help="General VAT Taxed Imports/Exports Base Amount. Sum of"
            " General VAT Base column for international transactions"),
        'imex_general_vat_tax_sum': fields.float(
            digits_compute=dp.get_precision('Account'),
            string="General VAT Taxed Amount",
            help="General VAT Taxed Imports/Exports Tax Amount. Sum of"
            " General VAT Tax column for international transactions"),
        'imex_additional_vat_base_sum': fields.float(
            digits_compute=dp.get_precision('Account'),
            string="Additional VAT Taxable Amount",
            help="Additional VAT Taxed Imports/Exports Base Amount. Sum of"
            " Additional VAT Base column for international transactions"),
        'imex_additional_vat_tax_sum': fields.float(
            digits_compute=dp.get_precision('Account'),
            string="Additional VAT Taxed Amount",
            help="Additional VAT Taxed Imports/Exports Tax Amount. Sum of "
            " Additional VAT Tax column for international transactions"),
        'imex_reduced_vat_base_sum': fields.float(
            digits_compute=dp.get_precision('Account'),
            string="Reduced VAT Taxable Amount",
            help="Reduced VAT Taxed Imports/Exports Base Amount. Sum of "
            " Reduced VAT Base column for international transactions"),
        'imex_reduced_vat_tax_sum': fields.float(
            digits_compute=dp.get_precision('Account'),
            string="Reduced VAT Taxed Amount",
            help="Reduced VAT Taxed Imports/Exports Tax Amount. Sum of "
            " Reduced VAT Tax column for international transactions"),

        # Totalization fields for domestic transactions
        'get_total_with_iva_do_sum': fields.function(
            _get_total_with_iva_sum,
            type="float", method=True, store=True,
            multi="get_total_with_iva",
            string='Total amount with VAT',
            help="Domestic Total with VAT Totalization"),
        'do_vat_base_sum': fields.float(
            digits_compute=dp.get_precision('Account'),
            string="Domestic Taxable Amount",
            help="Sum of all domestic transaction base amounts (reduced,"
            " general and additional)"),
        'do_exempt_vat_sum': fields.float(
            digits_compute=dp.get_precision('Account'),
            string="Exempt Tax",
            help="Domestic Exempt Tax Totalization. For Purchase Book it"
            " sums Exempt column for domestic transactions. For Sale Book it"
            " sums Tax Payer and Non-Tax Payer Exempt columns"),
        'do_sdcf_vat_sum': fields.float(
            digits_compute=dp.get_precision('Account'),
            string="SDCF Tax",
            help="Domestic SDCF Tax Totalization. For Purchase Book it sums"
            " SDCF column for domestic transactions. For Sale Book it sums"
            " Tax Payer and Non-Tax Payer SDCF columns"),
        'do_general_vat_base_sum': fields.float(
            digits_compute=dp.get_precision('Account'),
            string="General VAT Taxable Amount",
            help="General VAT Taxed Domestic Base Amount Totalization."
            " For Purchase Book it sums General VAT Base column for domestic"
            " transactions. For Sale Book it sums Tax Payer and Non-Tax Payer"
            " General VAT Base columns"),
        'do_general_vat_tax_sum': fields.float(
            digits_compute=dp.get_precision('Account'),
            string="General VAT Taxed Amount",
            help="General VAT Taxed Domestic Tax Amount Totalization."
            " For Purchase Book it sums General VAT Tax column for domestic"
            " transactions. For Sale Book it sums Tax Payer and Non-Tax Payer"
            " General VAT Tax columns"),
        'do_additional_vat_base_sum': fields.float(
            digits_compute=dp.get_precision('Account'),
            string="Additional VAT Taxable Amount",
            help="Additional VAT Taxed Domestic Base Amount Totalization."
            " For Purchase Book it sums Additional VAT Base column for"
            " domestic transactions. For Sale Book it sums Tax Payer and No"
            " Tax Payer Additional VAT Base columns"),
        'do_additional_vat_tax_sum': fields.float(
            digits_compute=dp.get_precision('Account'),
            string="Additional VAT Taxed Amount",
            help="Additional VAT Taxed Domestic Tax Amount Totalization."
            " For Purchase Book it sums Additional VAT Tax column for"
            " domestic transactions. For Sale Book it sums Tax Payer and No"
            " Tax Payer Additional VAT Tax columns"),
        'do_reduced_vat_base_sum': fields.float(
            digits_compute=dp.get_precision('Account'),
            string="Reduced VAT Taxable Amount",
            help="Reduced VAT Taxed Domestic Base Amount Totalization."
            " For Purchase Book it sums Reduced VAT Base column for domestic"
            " transactions. For Sale Book it sums Tax Payer and Non-Tax Payer"
            " Reduced VAT Base columns"),
        'do_reduced_vat_tax_sum': fields.float(
            digits_compute=dp.get_precision('Account'),
            string="Reduced VAT Taxed Amount",
            help="Reduced VAT Taxed Domestic Tax Amount Totalization."
            " For Purchase Book it sums Reduced VAT Tax column for domestic"
            " transactions. For Sale Book it sums Tax Payer and Non-Tax Payer"
            " Reduced VAT Tax columns"),
        'do_adjustment_vat_tax_sum': fields.function(
            _get_do_adjustment_vat_tax_sum, method=True, type='float',
            string='Adjustment VAT Taxed Amount'),

        # Apply only for sale book
        # Totalization fields for tax payer and Non-Tax Payer transactions
        'ntp_fbl_ids': fields.one2many("fiscal.book.line", "ntp_fb_id",
                                       string="Non-Tax Payer Detail Lines",
                                       help="Non-Tax Payer Lines that are"
                                       " grouped by the statement law that"
                                       " represent the data of are"
                                       " consolidate book lines"),
        'get_total_with_iva_tp_sum': fields.function(
            _get_total_with_iva_sum,
            type="float", method=True, store=True,
            multi="get_total_with_iva",
            string="Total amount with VAT",
            help="Tax Payer Total with VAT Totalization"),
        'tp_vat_base_sum': fields.float(
            digits_compute=dp.get_precision('Account'),
            string="Tax Payer Taxable Amount",
            help="Sum of all Tax Payer Grand Base Sum (reduced, general and"
            " additional taxes)"),
        'tp_exempt_vat_sum': fields.float(
            digits_compute=dp.get_precision('Account'),
            string="Exempt Tax",
            help="Tax Payer Exempt Tax Totalization. Sum of Exempt column"
            " for tax payer transactions"),
        'tp_sdcf_vat_sum': fields.float(
            digits_compute=dp.get_precision('Account'),
            string="SDCF Tax",
            help="Tax Payer SDCF Tax Totalization. Sum of SDCF column for"
            " tax payer transactions"),
        'tp_general_vat_base_sum': fields.float(
            digits_compute=dp.get_precision('Account'),
            string="General VAT Taxable Amount",
            help="General VAT Taxed Tax Payer Base Amount Totalization."
            " Sum of General VAT Base column for taxy payer transactions"),
        'tp_general_vat_tax_sum': fields.float(
            digits_compute=dp.get_precision('Account'),
            string="General VAT Taxed Amount",
            help="General VAT Taxed Tax Payer Tax Amount Totalization."
            " Sum of General VAT Tax column for tax payer transactions"),
        'tp_additional_vat_base_sum': fields.float(
            digits_compute=dp.get_precision('Account'),
            string="Additional VAT Taxable Amount",
            help="Additional VAT Taxed Tax Payer Base Amount Totalization."
            " Sum of Additional VAT Base column for tax payer transactions"),
        'tp_additional_vat_tax_sum': fields.float(
            digits_compute=dp.get_precision('Account'),
            string="Additional VAT Taxed Amount",
            help="Additional VAT Taxed Tax Payer Tax Amount Totalization."
            " Sum of Additional VAT Tax column for tax payer transactions"),
        'tp_reduced_vat_base_sum': fields.float(
            digits_compute=dp.get_precision('Account'),
            string="Reduced VAT Taxable Amount",
            help="Reduced VAT Taxed Tax Payer Base Amount Totalization."
            " Sum of Reduced VAT Base column for tax payer transactions"),
        'tp_reduced_vat_tax_sum': fields.float(
            digits_compute=dp.get_precision('Account'),
            string="Reduced VAT Taxed Amount",
            help="Reduced VAT Taxed Tax Payer Tax Amount Totalization."
            " Sum of Reduced VAT Tax column for tax payer transactions"),

        'get_total_with_iva_ntp_sum': fields.function(
            _get_total_with_iva_sum,
            type="float", method=True, store=True,
            multi="get_total_with_iva",
            string="Total amount with VAT",
            help="Non-Tax Payer Total with VAT Totalization"),
        'ntp_vat_base_sum': fields.float(
            digits_compute=dp.get_precision('Account'),
            string="Non-Tax Payer Taxable Amount",
            help="Non-Tax Payer Grand Base Totalization. Sum of all no tax"
            " payer tax bases (reduced, general and additional)"),
        'ntp_exempt_vat_sum': fields.float(
            digits_compute=dp.get_precision('Account'),
            string="Exempt Tax",
            help="Non-Tax Payer Exempt Tax Totalization. Sum of Exempt"
            " column for Non-Tax Payer transactions"),
        'ntp_sdcf_vat_sum': fields.float(
            digits_compute=dp.get_precision('Account'),
            string="SDCF Tax",
            help="Non-Tax Payer SDCF Tax Totalization. Sum of SDCF column"
            " for Non-Tax Payer transactions"),
        'ntp_general_vat_base_sum': fields.float(
            digits_compute=dp.get_precision('Account'),
            string="General VAT Taxable Amount",
            help="General VAT Taxed Non-Tax Payer Base Amount Totalization."
            " Sum of General VAT Base column for taxy payer transactions"),
        'ntp_general_vat_tax_sum': fields.float(
            digits_compute=dp.get_precision('Account'),
            string="General VAT Taxed Amount",
            help="General VAT Taxed Non-Tax Payer Tax Amount Totalization."
            " Sum of General VAT Tax column for Non-Tax Payer transactions"),
        'ntp_additional_vat_base_sum': fields.float(
            digits_compute=dp.get_precision('Account'),
            string="Additional VAT Taxable Amount",
            help="Additional VAT Taxed Non-Tax Payer Base Amount Totalization."
                 " Sum of Additional VAT Base column for Non-Tax Payer"
                 " transactions"),
        'ntp_additional_vat_tax_sum': fields.float(
            digits_compute=dp.get_precision('Account'),
            string="Additional VAT Taxed Amount",
            help="Additional VAT Taxed Non-Tax Payer Tax Amount Totalization."
                 " Sum of Additional VAT Tax column for Non-Tax Payer"
                 " transactions"),
        'ntp_reduced_vat_base_sum': fields.float(
            digits_compute=dp.get_precision('Account'),
            string="Reduced VAT Taxable Amount",
            help="Reduced VAT Taxed Non-Tax Payer Base Amount Totalization."
            " Sum of Reduced VAT Base column for Non-Tax Payer transactions"),
        'ntp_reduced_vat_tax_sum': fields.float(
            digits_compute=dp.get_precision('Account'),
            string="Reduced VAT Taxed Amount",
            help="Reduced VAT Taxed Non-Tax Payer Tax Amount Totalization."
            " Sum of Reduced VAT Tax column for Non-Tax Payer transactions"),
    }

    _sql_constraints = [
        ('period_type_company_uniq',
         'unique (period_id,type,company_id,fortnight)',
         _('The period, type, fortnight combination must be unique per'
           ' company!')),
    ]

    # action methods

    def onchange_field_clear_book(self, cr, uid, ids, context=None):
        """ It make clear all stuff of book. """
        context = context or {}
        self.clear_book(cr, uid, ids, context=context)
        return {'value': {}}

    # update book methods

    def _get_invoice_ids(self, cr, uid, fb_id, context=None):
        """
        It returns ids from open and paid invoices regarding to the type and
        period of the fiscal book order by date invoiced.
        """
        context = context or {}
        inv_obj = self.pool.get('account.invoice')
        fb_brw = self.browse(cr, uid, fb_id, context=context)
        inv_type = fb_brw.type == 'sale' \
            and ['out_invoice', 'out_refund'] \
            or ['in_invoice', 'in_refund']
        inv_state = ['paid', 'open']
        # pull invoice data
        inv_ids = inv_obj.search(cr, uid,
                                 [('period_id', '=', fb_brw.period_id.id),
                                  ('company_id', '=', fb_brw.company_id.id),
                                  ('type', 'in', inv_type),
                                  ('state', 'in', inv_state)],
                                 order='date_invoice asc', context=context)
        if fb_brw.fortnight:
            inv_ids = self.get_invoices_from_fortnight(
                cr, uid, fb_id, inv_ids, context=context)
        if fb_brw.type == 'purchase':
            inv_ids = self.get_invoices_sin_cred(
                cr, uid, fb_id, inv_ids, context=context)
        return inv_ids

    def get_invoices_sin_cred(self, cr, uid, ids, inv_ids, context=None):
        """
        if the fiscal book is of type purchase then need to filter the invoice
        of the book by only the ones how has sin_cred == False.
        return the filter invoices list.
        @param inv_ids: list of invoice ids
        @return invoices list
        """
        context = context or {}
        inv_obj = self.pool.get('account.invoice')
        ids = isinstance(ids, (int, long)) and [ids] or ids
        res = list()
        for inv_id in inv_ids:
            inv_brw = inv_obj.browse(cr, uid, inv_id, context=context)
            if not inv_brw.sin_cred:
                res.append(inv_id)
        return res

    def get_invoices_from_fortnight(self, cr, uid, ids, inv_ids, context=None):
        """
        return the invoices with the same fortnight as the fiscal book.
        @param inv_ids: list of invoice ids
        @return invoices list
        """
        context = context or {}
        period_obj = self.pool.get('account.period')
        inv_obj = self.pool.get('account.invoice')
        ids = isinstance(ids, (int, long)) and ids or ids[0]
        res = list()
        fb_fortnight = self.browse(cr, uid, ids, context=context).fortnight
        fb_fortnight = fb_fortnight == 'second' and True or False
        for inv_id in inv_ids:
            inv_brw = inv_obj.browse(cr, uid, inv_id, context=context)
            period, fortnight = period_obj._find_fortnight(
                cr, uid, date=inv_brw.date_invoice, context=context)
            period = period
            if fb_fortnight == fortnight:
                res.append(inv_id)
        return res

    def update_book(self, cr, uid, ids, context=None):
        """ It generate and fill book data with invoices, wh iva lines and
        taxes. """
        context = context or {}
        for fb_brw in self.browse(cr, uid, ids, context=context):
            self.clear_book(cr, uid, [fb_brw.id], context=context)
            self.update_book_invoices(cr, uid, fb_brw.id, context=context)
            self.update_book_issue_invoices(cr, uid, fb_brw.id,
                                            context=context)
            self.update_book_wh_iva_lines(cr, uid, fb_brw.id, context=context)
            self.update_book_customs_form(cr, uid, fb_brw.id, context=context)
            self.update_book_lines(cr, uid, fb_brw.id, context=context)
        return True

    def update_book_invoices(self, cr, uid, fb_id, context=None):
        """ It relate/unrelate the invoices to the fical book.
        @param fb_id: fiscal book id
        """
        context = context or {}
        inv_obj = self.pool.get('account.invoice')
        # Relate invoices
        inv_ids = self._get_invoice_ids(cr, uid, fb_id, context=context)
        inv_obj.write(cr, uid, inv_ids, {'fb_id': fb_id}, context=context)

        # TODO: move this process to the cancel process of the invoice
        # Unrelate invoices (period book change, invoice now cancel/draft or
        # have change its period)
        all_inv_ids = inv_obj.search(cr, uid, [('fb_id', '=', fb_id)],
                                     context=context)
        for inv_id_to_check in all_inv_ids:
            if inv_id_to_check not in inv_ids:
                inv_obj.write(cr, uid, inv_id_to_check, {'fb_id': False},
                              context=context)
        return True

    def _get_issue_invoice_ids(self, cr, uid, fb_id, context=None):
        """ It returns ids from not open or paid invoices regarding to the type
        and period of the fiscal book order by date invoiced.
        @param fb_id: fiscal book id.
        """
        context = context or {}
        inv_obj = self.pool.get('account.invoice')
        fb_brw = self.browse(cr, uid, fb_id, context=context)
        inv_type = fb_brw.type == 'sale' \
            and ['out_invoice', 'out_refund'] \
            or ['in_invoice', 'in_refund']
        inv_state = ['paid', 'open']
        # pull invoice data
        issue_inv_ids = inv_obj.search(
            cr, uid,
            ['|', '&', ('fb_id', '=', fb_brw.id),
             ('period_id', '!=', fb_brw.period_id.id),
             '&', '&', ('period_id', '=', fb_brw.period_id.id),
             ('type', 'in', inv_type), ('state', 'not in', inv_state)],
            order='date_invoice asc', context=context)
        if fb_brw.fortnight:
            issue_inv_ids = self.get_invoices_from_fortnight(
                cr, uid, fb_id, issue_inv_ids, context=context)
        if fb_brw.type == 'purchase':
            issue_inv_ids = self.get_invoices_sin_cred(
                cr, uid, fb_id, issue_inv_ids, context=context)

        return issue_inv_ids

    def update_book_issue_invoices(self, cr, uid, fb_id, context=None):
        """ It relate the issue invoices to the fiscal book. That criterion is:
          - Invoices of the period in state different form open or paid state.
          - Invoices already related to the book but it have a period change.
        @param fb_id: fiscal book id
        """
        context = context or {}
        inv_obj = self.pool.get('account.invoice')
        issue_inv_ids = self._get_issue_invoice_ids(cr, uid, fb_id,
                                                    context=context)
        inv_obj.write(cr, uid, issue_inv_ids, {'issue_fb_id': fb_id},
                      context=context)
        return issue_inv_ids

    def _get_wh_iva_line_ids(self, cr, uid, fb_id, context=None):
        """ It returns ids from wh iva lines with state 'done' regarding to the
        fiscal book period.
        @param fb_id: fiscal book id
        """
        context = context or {}
        awi_obj = self.pool.get('account.wh.iva')
        awil_obj = self.pool.get('account.wh.iva.line')
        fb_brw = self.browse(cr, uid, fb_id, context=context)
        awil_type = fb_brw.type == 'sale' \
            and ['out_invoice', 'out_refund'] \
            or ['in_invoice', 'in_refund']
        # pull wh iva line data
        awil_ids = []
        awi_ids = awi_obj.search(cr, uid,
                                 [('period_id', '=', fb_brw.period_id.id),
                                  ('type', 'in', awil_type),
                                  ('state', '=', 'done')],
                                 context=context)
        if fb_brw.fortnight:
            awi_ids = self.get_awi_from_fortnight(
                cr, uid, fb_id, awi_ids, context=context)

        for awi_id in awi_ids:
            list_ids = awil_obj.search(cr, uid,
                                       [('retention_id', '=', awi_id)],
                                       context=context)
            awil_ids.extend(list_ids)
        return awil_ids or False

    def get_awi_from_fortnight(self, cr, uid, ids, awi_ids, context=None):
        """
        return the awi ids with the same fortnight as the fiscal book.
        @param awi_ids: list of account withholding iva document ids.
        @param ids: only one fiscal book id.
        @return account withholding document id list
        """
        context = context or {}
        period_obj = self.pool.get('account.period')
        awi_obj = self.pool.get('account.wh.iva')
        ids = isinstance(ids, (int, long)) and ids or ids[0]
        res = list()
        fb_fortnight = self.browse(cr, uid, ids, context=context).fortnight
        fb_fortnight = fb_fortnight == 'second' and True or False
        for awi_id in awi_ids:
            awi_brw = awi_obj.browse(cr, uid, awi_id, context=context)
            period, fortnight = period_obj._find_fortnight(
                cr, uid, date=awi_brw.date_ret, context=context)
            period = period
            if fb_fortnight == fortnight:
                res.append(awi_id)
        return res

    # TODO: test this method.
    def update_book_wh_iva_lines(self, cr, uid, fb_id, context=None):
        """ It relate/unrelate the wh iva lines to the fiscal book.
        @param fb_id: fiscal book id
        """
        context = context or {}
        iwdl_obj = self.pool.get('account.wh.iva.line')
        rp_obj = self.pool.get('res.partner')
        fb_brw = self.browse(cr, uid, fb_id, context=context)
        # Relate wh iva lines
        iwdl_ids = self._get_wh_iva_line_ids(cr, uid, fb_id, context=context)

        if (fb_brw.type == "purchase" and iwdl_ids and not
                rp_obj._find_accounting_partner(
                    fb_brw.company_id.partner_id).wh_iva_agent):
            raise osv.except_osv(
                _("Error!"),
                _("You have withholdings registred but you are"
                  " not a withholding agent"))

        iwdl_obj.write(cr, uid, iwdl_ids, {'fb_id': fb_id}, context=context)
        # Unrelate wh iva lines (period book change, wh iva line have been
        # cancel or have change its period)
        all_iwdl_ids = iwdl_obj.search(cr, uid, [('fb_id', '=', fb_id)],
                                       context=context)
        for iwdl_id_to_check in all_iwdl_ids:
            if iwdl_id_to_check not in iwdl_ids:
                iwdl_obj.write(cr, uid, iwdl_id_to_check, {'fb_id': False},
                               context=context)
        return True

    def _get_invoice_iwdl_id(self, cr, uid, fb_id, inv_id, context=None):
        """ It check if the invoice have wh iva lines asociated and if its
        check if it is at the same period. Return the wh iva line ID or False
        instead.
        @param fb_id: fiscal book id.
        @param inv_id: invoice id to get wh line.
        """
        context = context or {}
        inv_obj = self.pool.get('account.invoice')
        inv_brw = inv_obj.browse(cr, uid, inv_id, context=context)
        iwdl_obj = self.pool.get('account.wh.iva.line')
        iwdl_id = False
        if inv_brw.wh_iva_id:
            iwdl_id = iwdl_obj.search(cr, uid,
                                      [('invoice_id', '=', inv_brw.id),
                                       ('fb_id', '=', fb_id)],
                                      context=context)
        return iwdl_id and iwdl_id[0] or False

    def _get_orphan_iwdl_ids(self, cr, uid, fb_id, context=None):
        """ It returns a list of ids from the orphan wh iva lines in the period
        that have not associated invoice.
        @param fb_id: fiscal book id
        """
        context = context or {}
        iwdl_obj = self.pool.get('account.wh.iva.line')
        inv_ids = [inv_brw.id
                   for inv_brw in self.browse(
                       cr, uid, fb_id, context=context).invoice_ids]
        inv_wh_ids = \
            [iwdl_brw.invoice_id.id for iwdl_brw in self.browse(
                cr, uid, fb_id, context=context).iwdl_ids]
        orphan_inv_ids = set(inv_wh_ids) - set(inv_ids)
        orphan_inv_ids = list(orphan_inv_ids)
        return orphan_inv_ids and iwdl_obj.search(
            cr, uid, [('invoice_id', 'in', orphan_inv_ids)],
            context=context) or []

    def get_order_criteria_adjustment(self, cr, uid, book_type, context=None):
        return book_type == 'sale' \
            and 'accounting_date asc, nro_ctrl asc' \
            or 'emission_date asc, invoice_number asc'

    def get_order_criteria(self, cr, uid, book_type, context=None):
        return book_type == 'sale' \
            and 'accounting_date asc, invoice_number asc' \
            or 'emission_date asc, invoice_number asc'

    def order_book_lines(self, cr, uid, fb_id, context=None):
        """ It orders book lines by a set of criteria:
            - chronologically ascendant date (For purchase book by
              emission date, for sale book by accounting date).
            - ascendant ordering for fiscal printer ascending number.
            - ascendant ordering for z report number.
            - ascendant ordering for invoice number.
        @param fb_id: book id.
        """
        context = context or {}
        fbl_obj = self.pool.get('fiscal.book.line')
        fb_brw = self.browse(cr, uid, fb_id, context=context)
        fbl_ids = [line_brw.id for line_brw in fb_brw.fbl_ids]

        ajst_order_criteria = self.get_order_criteria_adjustment(
            cr, uid, fb_brw.type, context=context)
        ajst_ordered_fbl_ids = \
            fbl_obj.search(
                cr, uid, [('id', 'in', fbl_ids), ('doc_type', '=', 'AJST')],
                order=ajst_order_criteria, context=context)

        for rank, fbl_id in enumerate(ajst_ordered_fbl_ids, 1):
            fbl_obj.write(cr, uid, fbl_id, {'rank': rank}, context=context)

        order_criteria = self.get_order_criteria(cr, uid, fb_brw.type,
                                                 context=context)
        ordered_fbl_ids = \
            fbl_obj.search(
                cr, uid, [('id', 'in', fbl_ids), ('doc_type', '!=', 'AJST')],
                order=order_criteria, context=context)

        for rank, fbl_id in enumerate(ordered_fbl_ids,
                                      len(ajst_ordered_fbl_ids) + 1):
            fbl_obj.write(cr, uid, fbl_id, {'rank': rank}, context=context)

        return True

    def _get_no_match_date_iwdl_ids(self, cr, uid, fb_id, context=None):
        """ It returns a list of wh iva lines ids that have a invoice in the
        same book period but where the invoice date_invoice is different from
        the wh iva line date.
        @param fb_id: fiscal book id.
        """
        context = context or {}
        iwdl_obj = self.pool.get('account.wh.iva.line')
        res = []
        for inv_brw in self.browse(cr, uid, fb_id,
                                   context=context).invoice_ids:
            iwdl_id = self._get_invoice_iwdl_id(cr, uid, fb_id, inv_brw.id,
                                                context=context)
            if iwdl_id:
                if inv_brw.date_invoice != iwdl_obj.browse(
                        cr, uid, iwdl_id, context=context).date_ret:
                    res.append(iwdl_id)
        return res

    def update_book_customs_form(self, cr, uid, ids, context=None):
        """ It relate the customs form to the fiscal book basing on the date
        liq of customs form.
        """
        # TODO: make this method aware of fortnight.
        context = context or {}
        cf_obj = self.pool.get('customs.form')

        ids = isinstance(ids, (int, long)) and [ids] or ids
        for fb_brw in self.browse(cr, uid, ids, context=context):
            if fb_brw.type == 'sale':
                continue
            add_cf_ids = cf_obj.search(
                cr, uid,
                [('state', '=', 'done'),
                 ('date_liq', '>=', fb_brw.period_id.date_start),
                 ('date_liq', '<=', fb_brw.period_id.date_stop)],
                context=context)
            if add_cf_ids:
                self.write(
                    cr, uid, fb_brw.id,
                    {'cf_ids': [(4, cf) for cf in add_cf_ids]},
                    context=context)
        return True

    def update_book_lines(self, cr, uid, fb_id, context=None):
        """ It updates the fiscal book lines values. Cretate, order and rank
        the book lines. Creates the book taxes too acorring to lines created.
        @param fb_id: fiscal book id
        """
        context = context or {}
        data = []
        iwdl_obj = self.pool.get('account.wh.iva.line')
        fb_brw = self.browse(cr, uid, fb_id, context=context)
        rp_obj = self.pool.get('res.partner')

        # add book lines for withholding iva lines
        if fb_brw.iwdl_ids:
            orphan_iwdl_ids = self._get_orphan_iwdl_ids(cr, uid, fb_id,
                                                        context=context)
            no_match_dt_iwdl_ids = \
                self._get_no_match_date_iwdl_ids(cr, uid, fb_id,
                                                 context=context)
            iwdl_ids = orphan_iwdl_ids + no_match_dt_iwdl_ids
            t_type = fb_brw.type == 'sale' and 'tp' or 'do'
            for iwdl_brw in iwdl_obj.browse(cr, uid, iwdl_ids,
                                            context=context):
                rp_brw = rp_obj._find_accounting_partner(
                    iwdl_brw.retention_id.partner_id)
                values = {
                    'iwdl_id': iwdl_brw.id,
                    'type': t_type,
                    'accounting_date': iwdl_brw.date_ret or False,
                    'emission_date':
                        iwdl_brw.date or iwdl_brw.date_ret or False,
                    'doc_type': self.get_doc_type(cr, uid, iwdl_id=iwdl_brw.id,
                                                  fb_id=fb_id,
                                                  context=context),
                    'wh_number': iwdl_brw.retention_id.number or False,
                    'partner_name': rp_brw.name or 'N/A',
                    'partner_vat': rp_brw.vat or 'N/A',
                    'affected_invoice':
                        iwdl_brw.invoice_id.fiscal_printer and
                        iwdl_brw.invoice_id.invoice_printer or
                        (fb_brw.type == 'sale' and
                         iwdl_brw.invoice_id.number or
                         iwdl_brw.invoice_id.supplier_invoice_number),
                    'affected_invoice_date':
                        iwdl_brw.invoice_id.date_document or
                        iwdl_brw.invoice_id.date_invoice,
                    'wh_rate': iwdl_brw.wh_iva_rate,
                }
                data.append((0, 0, values))

        # add book lines for invoices
        for inv_brw in self.browse(cr, uid, fb_id,
                                   context=context).invoice_ids:
            imex_invoice = self.is_invoice_imex(cr, uid, inv_brw.id,
                                                context=context)
            iwdl_id = self._get_invoice_iwdl_id(cr, uid, fb_id, inv_brw.id,
                                                context=context)
            doc_type = self.get_doc_type(cr, uid, inv_id=inv_brw.id,
                                         fb_id=fb_id, context=context)

            rp_brw = rp_obj._find_accounting_partner(inv_brw.partner_id)

            iwdl_brw = iwdl_obj.browse(cr, uid, iwdl_id, context=context) if \
                iwdl_id and iwdl_id not in no_match_dt_iwdl_ids else False

            values = {
                'invoice_id': inv_brw.id,
                'emission_date':
                    (not imex_invoice) and
                    (inv_brw.date_document or inv_brw.date_invoice) or
                    False,
                'accounting_date':
                    (not imex_invoice) and
                    inv_brw.date_invoice or
                    False,
                'imex_date':
                    imex_invoice and
                    inv_brw.customs_form_id.date_liq or
                    False,
                'type': self.get_transaction_type(
                    cr, uid, fb_id, inv_brw.id, context=context),
                'debit_affected':
                    inv_brw.parent_id and
                    inv_brw.parent_id.type in
                    ['in_invoice', 'out_invoice'] and
                    inv_brw.parent_id.parent_id and
                    inv_brw.parent_id.number or
                False,
                'credit_affected':
                    inv_brw.parent_id and
                    inv_brw.parent_id.type in
                    ['in_refund', 'out_refund'] and
                    inv_brw.parent_id.number or
                    False,
                'ctrl_number':
                    not inv_brw.fiscal_printer and
                    inv_brw.nro_ctrl or
                    False,
                'affected_invoice':
                    (doc_type == "N/DE" or doc_type == "N/CR") and (
                        inv_brw.parent_id and
                        inv_brw.parent_id.number or
                        False) or
                    False,
                'partner_name': rp_brw.name or 'N/A',
                'partner_vat': rp_brw.vat and rp_brw.vat[2:] or 'N/A',
                'invoice_number':
                    inv_brw.fiscal_printer and
                    inv_brw.invoice_printer or(
                        fb_brw.type == 'sale' and
                        inv_brw.number or
                        inv_brw.supplier_invoice_number),
                'doc_type': doc_type,
                'void_form':
                    inv_brw.name and (
                        inv_brw.name.find('PAPELANULADO') >= 0 and
                        '03-ANU' or
                        '01-REG') or
                    '01-REG',
                'fiscal_printer': inv_brw.fiscal_printer or False,
                'z_report': inv_brw.z_report or False,
                'custom_statement': inv_brw.customs_form_id.name or False,
                'iwdl_id': iwdl_brw and iwdl_brw.id,
                'wh_number': iwdl_brw and iwdl_brw.retention_id.number or '',
                'wh_rate': iwdl_brw and iwdl_brw.wh_iva_rate or 0.0,
            }
            data.append((0, 0, values))

        # add book lines for customs forms
        for cf_brw in fb_brw.cf_ids:

            cf_partner_brws = \
                list(set([
                    rp_obj._find_accounting_partner(
                        cfl_brw.tax_code.partner_id)
                    for cfl_brw in cf_brw.cfl_ids
                    if not cfl_brw.tax_code.vat_detail]))

            common_values = {
                'cf_id': cf_brw.id,
                'type': 'do',
                'emission_date': cf_brw.date_liq or False,
                'doc_type': self.get_doc_type(cr, uid, cf_id=cf_brw.id,
                                              fb_id=fb_id, context=context),
            }

            for partner_brw in cf_partner_brws:
                values = common_values.copy()
                values['partner_name'] = partner_brw.name or 'N/A'
                values['partner_vat'] = partner_brw.vat \
                    and partner_brw.vat[2:] or 'N/A'
                values['total_with_iva'] = \
                    self.get_cfl_sum(cr, uid, cf_brw.id, partner_brw.id,
                                     context=context)
                values['vat_sdcf'] = values['total_with_iva']

                data.append((0, 0, values))

        if data:
            self.write(cr, uid, fb_id, {'fbl_ids': data}, context=context)
            self.link_book_lines_and_taxes(cr, uid, fb_id, context=context)

        if fb_brw.article_number in ['77', '78']:
            self.update_book_ntp_lines(cr, uid, fb_brw.id, context=context)
        else:
            self.order_book_lines(cr, uid, fb_brw.id, context=context)

        return True

    def get_cfl_sum(self, cr, uid, cf_id, partner_id, context=None):
        """
        Returns the sum of the current customs form lines that have the same
        partner
        @param cf_id: customs form id
        @param partner_id: partner id
        """
        # KEEP AN EYE ON HERE, No check has been made on accounting partner
        context = context or {}
        cf_obj = self.pool.get('customs.form')
        cfl_brws = cf_obj.browse(cr, uid, cf_id, context=context).cfl_ids
        amount = sum([cfl_brw.amount
                      for cfl_brw in cfl_brws
                      if cfl_brw.tax_code.partner_id.id == partner_id and
                      not cfl_brw.tax_code.vat_detail])
        return amount

    def get_grouped_consecutive_lines_ids(self, cr, uid, lines_ids,
                                          context=None):
        """ Return a list of tuples that represent every line in the book.
        If there is a group of consecutive Non-Tax Payer with fiscal printer
        billing lines, it will return a unique tuple that holds the information
        of the lines. The return tutple has this format
            ('invoice_number'[0], 'invoice_number'[-1], [line_brw])
            - 'invoice_number'[0]: invoice number of the first line in the
            group
            - 'invoice_number'[-1]: invoice number of the last line in the
            group
            - [line_brw] list o browse records that weel be into the line.
        @param line_ids: list of book lines ids.
        """
        context = context or {}
        lines_brws = self.pool.get('fiscal.book.line').browse(
            cr, uid, lines_ids, context=context)
        res = list()
        group_list = list()
        group_value = False

        for line_brw in lines_brws:
            group_value = group_value or line_brw.type
            if line_brw.type == group_value and group_value == 'ntp' \
                    and line_brw.fiscal_printer:
                group_list.append(line_brw)
            else:
                if group_list:
                    res.append(
                        (group_list[0].invoice_number,
                         group_list[-1].invoice_number, group_value,
                         group_list))
                    group_value = line_brw.type
                    group_list = [line_brw]
                else:
                    res.append((
                        line_brw.invoice_number, line_brw.invoice_number,
                        group_value, [line_brw]))
                    group_value = False

        if group_list:
            res.append((
                group_list[0].invoice_number, group_list[-1].invoice_number,
                group_value, group_list))

        return res

    def update_book_ntp_lines(self, cr, uid, fb_id, context=None):
        """ It consolidate Non-Tax Payer book lines into one line considering
        the consecutiveness and next criteria: fiscal printer and z report.
        This consolidated groups are move to another field: Non-Tax Payer
        Detail operations. (This only applys when is a sale book)
        @param fb_id: fiscal book id
        """
        context = context or {}
        fbl_obj = self.pool.get('fiscal.book.line')
        fb_brw = self.browse(cr, uid, fb_id, context=context)

        # separating groups
        lines_brws = fb_brw.fbl_ids
        order_dict = dict()
        date_values = list(set([line_brw.emission_date
                                for line_brw in lines_brws]))
        date_values.sort()
        order_dict = {}.fromkeys(date_values)
        for date in date_values:
            date_records = [line_brw
                            for line_brw in lines_brws
                            if line_brw.emission_date == date]
            printers_values = list(set([line_brw.fiscal_printer
                                        for line_brw in date_records]))
            printers_values.sort()
            order_dict[date] = {}.fromkeys(printers_values)
            for printer in printers_values:
                printer_records = [line_brw
                                   for line_brw in date_records
                                   if line_brw.fiscal_printer == printer]
                z_report_values = list(set([line_brw.z_report
                                            for line_brw in printer_records]))
                z_report_values.sort()
                order_dict[date][printer] = {}.fromkeys(z_report_values)
                for z_report in z_report_values:
                    # this records needs to be order by invoice number
                    z_records = \
                        [(line_brw.invoice_number, line_brw)
                         for line_brw in printer_records
                         if line_brw.z_report == z_report]
                    z_records.sort()
                    z_records = [item[1] for item in z_records]
                    # group by type of line
                    order_dict[date][printer][z_report] = \
                        self.get_grouped_consecutive_lines_ids(
                        cr, uid, [item.id for item in z_records],
                        context=context)

        # import pprint
        # print 'order_dict'
        # pprint.pprint(order_dict)

        # agruping and ranking
        rank = 1
        # order_dict[date][printer][z_report] = [ ('desde', 'hasta', 'tipot',
        #                                          list(line_brws)) ]
        ntp_groups_list = list()
        # format [ ( rank, invoice_number, [line_brws] ) ]
        ntp_no_group_list = list()      # format [ ( rank, [line_brws] ) ]
        order_no_group_list = list()    # format [ ( rank, line_id ) ]

        order_dates = order_dict.keys()
        order_dates.sort()
        for date in order_dates:
            order_printers = order_dict[date].keys()
            order_printers.sort()
            for printer in order_printers:
                order_z_reports = order_dict[date][printer].keys()
                order_z_reports.sort()
                for z_report in order_z_reports:
                    for line in order_dict[date][printer][z_report]:
                        if line[2] == 'ntp':
                            if line[0] == line[1] and len(line[3]) == 1:
                                ntp_no_group_list.append(
                                    (rank, line[3][0].id))
                            elif line[0] != line[1] and len(line[3]) > 1:
                                ntp_groups_list.append(
                                    (rank, 'Desde: ' + line[0] +
                                     ' ... Hasta: ' + line[1], line[3]))
                            else:
                                raise osv.except_osv(
                                    _("Error!"),
                                    _("This is a no valid line. Be sure you"
                                      " have two or more invoices with the"
                                      " same invoice number"))
                        elif line[2] != 'ntp':
                            order_no_group_list.append(
                                (rank, line[3][0].id))
                        rank += 1

        # import pprint
        # print '\n ntp_no_group_list'
        # pprint.pprint(ntp_no_group_list)
        # print '\n ntp_groups_list'
        # pprint.pprint(ntp_groups_list)
        # print '\n order_no_group_list'
        # pprint.pprint(order_no_group_list)

        # ~ # rank lines that have nothing to do with ntp.
        for line in order_no_group_list:
            fbl_obj.write(cr, uid, line[1], {'rank': line[0]}, context=context)

        # ~ # rank ntp individual lines.
        for line in ntp_no_group_list:
            fbl_obj.write(
                cr, uid, line[1],
                {'rank': line[0],
                 'partner_name': 'No Contribuyente',
                 'partner_vat': False},
                context=context)

        # create consolidate line using ntp_groups_list list, move group lines
        # to Non-Tax Payer lines detail.
        for line_tuple in ntp_groups_list:
            consolidate_line_id = \
                self.create_consolidate_line(cr, uid, fb_id, line_tuple,
                                             context=context)
            for rank, line_brw in enumerate(line_tuple[-1], 1):
                fbl_obj.write(
                    cr, uid, line_brw.id,
                    {'fb_id': False,
                     'ntp_fb_id': fb_id,
                     'parent_id': consolidate_line_id,
                     'rank': -1},
                    context=context)

        return True

    def create_consolidate_line(self, cr, uid, fb_id, line_tuple,
                                context=None):
        """ Create a new consolidate Non-Tax Payer line for a group of no tax
        payer operations.
        @param fb_id: fiscal book line id.
        @param line_tuple: tuple with the information for construct the
                          consolidate line (rank, [brws]).
                          # format [ ( rank, invoice_number, [line_brws] ) ]
        """
        context = context or {}
        fbl_obj = self.pool.get('fiscal.book.line')
        float_colums = ['total_with_iva', 'vat_sdcf', 'vat_exempt',
                        'vat_reduced_base', 'vat_reduced_tax',
                        'vat_general_base', 'vat_general_tax',
                        'vat_additional_base', 'vat_additional_tax']

        rank, invoice_number, child_brws = line_tuple
        child_ids = [line_brw.id for line_brw in child_brws]
        first_item_brw = fbl_obj.browse(cr, uid, child_brws[0].id,
                                        context=context)
        # fill common value
        values = {
            'rank': rank,
            'invoice_number': invoice_number,
            'child_ids': [(6, 0, child_ids)],
            'fb_id': first_item_brw.fb_id.id,
            'partner_name': 'No Contribuyente',
            'emission_date': first_item_brw.emission_date,
            'accounting_date': first_item_brw.accounting_date,
            'doc_type': first_item_brw.doc_type,
            'type': first_item_brw.type,
            'fiscal_printer': first_item_brw.fiscal_printer,
            'z_report': first_item_brw.z_report,
        }
        # fill totalization values
        for col in float_colums:
            values[col] = \
                sum([getattr(line_brw, col) for line_brw in child_brws])

        return fbl_obj.create(cr, uid, values, context=context)

    def update_book_taxes_summary(self, cr, uid, fb_id, context=None):
        """ It update the summaroty of taxes by type for this book.
        @param fb_id: fiscal book id
        """
        context = context or {}
        self.clear_book_taxes_summary(cr, uid, fb_id, context=context)
        tax_types = ['exento', 'sdcf', 'reducido', 'general', 'adicional']
        op_types = self.browse(cr, uid, fb_id, context=context).type \
            == 'sale' and ['ex', 'tp', 'ntp'] or ['im', 'do']
        base_sum = {}.fromkeys(op_types)
        tax_sum = base_sum.copy()
        for op_type in op_types:
            tax_sum[op_type] = {}.fromkeys(tax_types, 0.0)
            base_sum[op_type] = {}.fromkeys(tax_types, 0.0)

        for fbl in self.browse(cr, uid, fb_id, context=context).fbl_ids:
            if fbl.invoice_id:
                sign = 1 if fbl.doc_type != 'N/CR' else -1
                tax_lines = fbl.type in ['im', 'ex'] \
                    and fbl.invoice_id.imex_tax_line \
                    or fbl.invoice_id.tax_line
                for ait in tax_lines:
                    if ait.tax_id.appl_type:
                        base_sum[fbl.type][ait.tax_id.appl_type] += \
                            ait.base_amount * sign
                        tax_sum[fbl.type][ait.tax_id.appl_type] += \
                            ait.tax_amount * sign
                    else:
                        raise osv.except_osv(
                            _('Error!'),
                            _('You must assign the Aliquot Type to: %s') % (
                                ait.tax_id.name))
            elif fbl.cf_id:
                if fbl.type != 'do':
                    raise osv.except_osv(
                        _('Programing Error!'),
                        _("Customs form lines are domestic transactions"))
                base_sum['do']['sdcf'] += fbl.vat_sdcf

        data = [(0, 0, {'tax_type': ttype, 'op_type': optype,
                        'base_amount_sum': base_sum[optype][ttype],
                        'tax_amount_sum': tax_sum[optype][ttype]
                        })
                for ttype in tax_types
                for optype in op_types
                ]
        return data and self.write(cr, uid, fb_id, {'fbts_ids': data},
                                   context=context)

    def update_book_taxes_amount_fields(self, cr, uid, fb_id, context=None):
        """ It update the base_amount and the tax_amount field for book, and
        extract data from the book tax summary to store fields inside the
        book model.
        @param fb_id: fiscal book id
        """
        context = context or {}
        data = {}
        # totalization of book tax amount and base amount fields
        tax_amount = base_amount = 0.0
        for fbl_brw in self.browse(cr, uid, fb_id, context=context).fbl_ids:
            sign = 1 if fbl_brw.doc_type != 'N/CR' else -1
            if fbl_brw.invoice_id:
                taxes = fbl_brw.type in ['im', 'ex'] \
                    and fbl_brw.invoice_id.imex_tax_line \
                    or fbl_brw.invoice_id.tax_line
                for ait in taxes:
                    if ait.tax_id:
                        base_amount += ait.base_amount * sign
                        if ait.tax_id.ret:
                            tax_amount += ait.tax_amount * sign

        data['tax_amount'] = tax_amount
        data['base_amount'] = base_amount

        # totalization of book taxable and taxed amount for every tax type and
        # operation type
        vat_fields = [
            'imex_exempt_vat_sum',
            'imex_sdcf_vat_sum',
            'imex_general_vat_base_sum',
            'imex_general_vat_tax_sum',
            'imex_additional_vat_base_sum',
            'imex_additional_vat_tax_sum',
            'imex_reduced_vat_base_sum',
            'imex_reduced_vat_tax_sum',
            'do_exempt_vat_sum',
            'do_sdcf_vat_sum',
            'do_general_vat_base_sum',
            'do_general_vat_tax_sum',
            'do_additional_vat_base_sum',
            'do_additional_vat_tax_sum',
            'do_reduced_vat_base_sum',
            'do_reduced_vat_tax_sum',
            'tp_exempt_vat_sum',
            'tp_sdcf_vat_sum',
            'tp_general_vat_base_sum',
            'tp_general_vat_tax_sum',
            'tp_additional_vat_base_sum',
            'tp_additional_vat_tax_sum',
            'tp_reduced_vat_base_sum',
            'tp_reduced_vat_tax_sum',
            'ntp_exempt_vat_sum',
            'ntp_sdcf_vat_sum',
            'ntp_general_vat_base_sum',
            'ntp_general_vat_tax_sum',
            'ntp_additional_vat_base_sum',
            'ntp_additional_vat_tax_sum',
            'ntp_reduced_vat_base_sum',
            'ntp_reduced_vat_tax_sum',
        ]
        for field_name in vat_fields:
            data[field_name] = \
                self.update_vat_fields(cr, uid, fb_id, field_name,
                                       context=context)

        # more complex totalization amounts.
        fb_brw = self.browse(cr, uid, fb_id, context=context)

        data['do_sdcf_and_exempt_sum'] = fb_brw.type == 'sale' \
            and (data['tp_exempt_vat_sum'] + data['tp_sdcf_vat_sum'] +
                 data['ntp_exempt_vat_sum'] + data['ntp_sdcf_vat_sum']) \
            or (data['do_exempt_vat_sum'] + data['do_sdcf_vat_sum'])

        for optype in ['imex', 'do', 'tp', 'ntp']:
            data[optype + '_vat_base_sum'] = \
                sum([data[optype + '_' + ttax + "_vat_base_sum"]
                     for ttax in ["general", "additional", "reduced"]])

        data['imex_vat_base_sum'] += \
            data['imex_exempt_vat_sum'] + data['imex_sdcf_vat_sum']

        # sale book domestic fields transformations (ntp and tp sums)
        if fb_brw.type == 'sale':

            data["do_vat_base_sum"] = \
                data["tp_vat_base_sum"] + data["ntp_vat_base_sum"]

            for ttax in ["general", "additional", "reduced"]:
                for amttype in ["base", "tax"]:
                    data['do_' + ttax + '_vat_' + amttype + '_sum'] = sum(
                        [data[optype + "_" + ttax + "_vat_" + amttype + "_sum"]
                         for optype in ["ntp", "tp"]])
            for ttax in ["exempt", "sdcf"]:
                data['do_' + ttax + '_vat_sum'] =  \
                    sum([data[optype + "_" + ttax + "_vat_sum"]
                         for optype in ["ntp", "tp"]
                         ])

        return self.write(cr, uid, fb_id, data, context=context)

    def update_vat_fields(self, cr, uid, fb_id, field_name, context=None):
        """ It returns summation of a fiscal book tax column (Using
        fiscal.book.taxes.summary).
        @param: field_name [
            'imex_sdcf_vat_sum',
            'imex_exempt_vat_sum',
            'imex_general_vat_base_sum',
            'imex_general_vat_tax_sum',
            'imex_additional_vat_base_sum',
            'imex_additional_vat_tax_sum',
            'imex_reduced_vat_base_sum',
            'imex_reduced_vat_tax_sum',

            'do_sdcf_vat_sum',
            'do_exempt_vat_sum',
            'do_general_vat_base_sum',
            'do_general_vat_tax_sum',
            'do_additional_vat_base_sum',
            'do_additional_vat_tax_sum',
            'do_reduced_vat_base_sum',
            'do_reduced_vat_tax_sum'

            'tp_sdcf_vat_sum',
            'tp_exempt_vat_sum',
            'tp_general_vat_base_sum',
            'tp_general_vat_tax_sum',
            'tp_additional_vat_base_sum',
            'tp_additional_vat_tax_sum',
            'tp_reduced_vat_base_sum',
            'tp_reduced_vat_tax_sum'

            'ntp_sdcf_vat_sum',
            'ntp_exempt_vat_sum',
            'ntp_general_vat_base_sum',
            'ntp_general_vat_tax_sum',
            'ntp_additional_vat_base_sum',
            'ntp_additional_vat_tax_sum',
            'ntp_reduced_vat_base_sum',
            'ntp_reduced_vat_tax_sum'
        ]
        """
        context = context or {}
        res = 0.0
        # fbts_obj = self.pool.get('fiscal.book.taxes.summary')

        # Identifying the field
        field_info = field_name[:-4].split('_')
        field_info.remove('vat')

        field_op, field_tax, field_amount = (len(field_info) == 3) \
            and field_info \
            or field_info + ['base']

        # Translation between the fb fields names and the fbts records data.
        tax_type = {'exempt': 'exento', 'sdcf': 'sdcf', 'reduced': 'reducido',
                    'general': 'general', 'additional': 'adicional'}
        amount_type = {'base': 'base_amount_sum', 'tax': 'tax_amount_sum'}

        # Calculate
        fb_brw = self.browse(cr, uid, fb_id, context=context)
        if field_op == 'imex':
            field_op = fb_brw.type == 'purchase' and 'im' or 'ex'
        for fbts_brw in fb_brw.fbts_ids:
            if (fbts_brw.tax_type == tax_type[field_tax] and
                    fbts_brw.op_type == field_op):
                res = getattr(fbts_brw, amount_type[field_amount])
        return res

    def link_book_lines_and_taxes(self, cr, uid, fb_id, context=None):
        """ Updates the fiscal book taxes. Link the tax with the corresponding
        book line and update the fields of sum taxes in the book.
        @param fb_id: the id of the current fiscal book """
        context = context or {}
        fbl_obj = self.pool.get('fiscal.book.line')
        ut_obj = self.pool.get('l10n.ut')
        # write book taxes
        data = []
        for fbl in self.browse(cr, uid, fb_id, context=context).fbl_ids:
            if fbl.invoice_id:
                f_xc = ut_obj.sxc(
                    cr, uid,
                    fbl.invoice_id.currency_id.id,
                    fbl.invoice_id.company_id.currency_id.id,
                    fbl.invoice_id.date_invoice)
                sign = 1 if fbl.doc_type != 'N/CR' else -1
                amount_field_data = \
                    {'total_with_iva':
                     f_xc(fbl.invoice_id.amount_untaxed) * sign,
                     'vat_sdcf': 0.0, 'vat_exempt': 0.0}
                taxes = fbl.type in ['im', 'ex'] \
                    and fbl.invoice_id.imex_tax_line \
                    or fbl.invoice_id.tax_line
                for ait in taxes:
                    if ait.tax_id:

                        data.append((0, 0, {'fb_id': fb_id,
                                            'fbl_id': fbl.id,
                                            'ait_id': ait.id}))
                        amount_field_data['total_with_iva'] += \
                            ait.tax_amount * sign
                        if ait.tax_id.appl_type == 'sdcf':
                            amount_field_data['vat_sdcf'] += \
                                ait.base_amount * sign
                        if ait.tax_id.appl_type == 'exento':
                            amount_field_data['vat_exempt'] += \
                                ait.base_amount * sign
                    else:
                        data.append((0, 0, {
                            'fb_id': fb_id, 'fbl_id': False,
                            'ait_id': ait.id}))
                fbl_obj.write(cr, uid, fbl.id, amount_field_data,
                              context=context)

        if data:
            self.write(cr, uid, fb_id, {'fbt_ids': data}, context=context)
        self.update_book_taxes_summary(cr, uid, fb_id, context=context)
        self.update_book_lines_taxes_fields(cr, uid, fb_id, context=context)
        self.update_book_taxes_amount_fields(cr, uid, fb_id, context=context)
        return True

    def update_book_lines_taxes_fields(self, cr, uid, fb_id, context=None):
        """ Update taxes data for every line in the fiscal book given,
        extrating de data from the fiscal book taxes associated.
        @param fb_id: fiscal book line id.
        """
        context = context or {}
        fbl_obj = self.pool.get('fiscal.book.line')
        field_names = ['vat_reduced_base', 'vat_reduced_tax',
                       'vat_general_base', 'vat_general_tax',
                       'vat_additional_base', 'vat_additional_tax']
        tax_type = {'reduced': 'reducido', 'general': 'general',
                    'additional': 'adicional'}
        for fbl_brw in self.browse(cr, uid, fb_id, context=context).fbl_ids:
            sign = 1 if fbl_brw.doc_type != 'N/CR' else -1
            data = {}.fromkeys(field_names, 0.0)
            for fbt_brw in fbl_brw.fbt_ids:
                for field_name in field_names:
                    field_tax, field_amount = field_name[4:].split('_')
                    if fbt_brw.ait_id.tax_id.appl_type == tax_type[field_tax]:
                        data[field_name] += field_amount == 'base' \
                            and fbt_brw.base_amount * sign \
                            or fbt_brw.tax_amount * sign
            fbl_obj.write(cr, uid, fbl_brw.id, data, context=context)
        return True

    # clear book methods

    def clear_book(self, cr, uid, fb_id, context=None):
        """ It delete all book data information.
        @param fb_id: fiscal book line id
        """
        context = context or {}
        # clear fields
        self.clear_book_taxes_amount_fields(cr, uid, fb_id, context=context)
        # delete data
        self.clear_book_lines(cr, uid, fb_id, context=context)
        self.clear_book_taxes(cr, uid, fb_id, context=context)
        self.clear_book_taxes_summary(cr, uid, fb_id, context=context)
        # unrelate data
        self.clear_book_invoices(cr, uid, fb_id, context=context)
        self.clear_book_issue_invoices(cr, uid, fb_id, context=context)
        self.clear_book_iwdl_ids(cr, uid, fb_id, context=context)
        self.clear_book_customs_form(cr, uid, fb_id, context=context)
        return True

    def clear_book_lines(self, cr, uid, ids, context=None):
        """ It delete all book lines loaded in the book """
        context = context or {}
        fbl_obj = self.pool.get("fiscal.book.line")
        for fb_id in ids:
            fbl_brws = self.browse(cr, uid, fb_id, context=context).fbl_ids
            fbl_ids = [fbl.id for fbl in fbl_brws]
            fbl_obj.unlink(cr, uid, fbl_ids, context=context)
            self.clear_book_taxes_amount_fields(cr, uid, fb_id,
                                                context=context)
        return True

    def clear_book_taxes(self, cr, uid, ids, context=None):
        """ It delete all book taxes loaded in the book """
        context = context or {}
        fbt_obj = self.pool.get("fiscal.book.taxes")
        for fb_id in ids:
            fbt_brws = self.browse(cr, uid, fb_id, context=context).fbt_ids
            fbt_ids = [fbt.id for fbt in fbt_brws]
            fbt_obj.unlink(cr, uid, fbt_ids, context=context)
            self.clear_book_taxes_amount_fields(cr, uid, fb_id,
                                                context=context)
        return True

    def clear_book_taxes_summary(self, cr, uid, fb_id, context=None):
        """ It delete fiscal book taxes summary data for the book """
        context = context or {}
        fbts_obj = self.pool.get('fiscal.book.taxes.summary')
        fb_id = isinstance(fb_id, (int, long)) and [fb_id] or fb_id
        fbts_ids = fbts_obj.search(cr, uid, [('fb_id', 'in', fb_id)],
                                   context=context)
        fbts_obj.unlink(cr, uid, fbts_ids, context=context)
        return True

    def clear_book_taxes_amount_fields(self, cr, uid, fb_id, context=None):
        """ Clean amount taxes fields in fiscal book """
        context = context or {}
        vat_fields = [
            'tax_amount',
            'base_amount',
            'imex_vat_base_sum',
            'imex_exempt_vat_sum',
            'imex_sdcf_vat_sum',
            'imex_general_vat_base_sum',
            'imex_general_vat_tax_sum',
            'imex_additional_vat_base_sum',
            'imex_additional_vat_tax_sum',
            'imex_reduced_vat_base_sum',
            'imex_reduced_vat_tax_sum',
            'do_vat_base_sum',
            'do_exempt_vat_sum',
            'do_sdcf_vat_sum',
            'do_general_vat_base_sum',
            'do_general_vat_tax_sum',
            'do_additional_vat_base_sum',
            'do_additional_vat_tax_sum',
            'do_reduced_vat_base_sum',
            'do_reduced_vat_tax_sum',
            'tp_vat_base_sum',
            'tp_exempt_vat_sum',
            'tp_sdcf_vat_sum',
            'tp_general_vat_base_sum',
            'tp_general_vat_tax_sum',
            'tp_additional_vat_base_sum',
            'tp_additional_vat_tax_sum',
            'tp_reduced_vat_base_sum',
            'tp_reduced_vat_tax_sum',
            'ntp_vat_base_sum',
            'ntp_exempt_vat_sum',
            'ntp_sdcf_vat_sum',
            'ntp_general_vat_base_sum',
            'ntp_general_vat_tax_sum',
            'ntp_additional_vat_base_sum',
            'ntp_additional_vat_tax_sum',
            'ntp_reduced_vat_base_sum',
            'ntp_reduced_vat_tax_sum',
        ]

        return self.write(cr, uid, fb_id, {}.fromkeys(vat_fields, 0.0),
                          context=context)

    def clear_book_invoices(self, cr, uid, ids, context=None):
        """ Unrelate all invoices of the book. And delete fiscal book taxes """
        context = context or {}
        inv_obj = self.pool.get("account.invoice")
        for fb_id in ids:
            self.clear_book_taxes(cr, uid, [fb_id], context=context)
            inv_brws = self.browse(cr, uid, fb_id, context=context).invoice_ids
            inv_ids = [inv.id for inv in inv_brws]
            inv_obj.write(cr, uid, inv_ids, {'fb_id': False}, context=context)
        return True

    def clear_book_issue_invoices(self, cr, uid, ids, context=None):
        """ Unrelate all issue invoices of the book """
        context = context or {}
        inv_obj = self.pool.get("account.invoice")
        for fb_id in ids:
            inv_brws = self.browse(
                cr, uid, fb_id, context=context).issue_invoice_ids
            inv_ids = [inv.id for inv in inv_brws]
            inv_obj.write(cr, uid, inv_ids, {'issue_fb_id': False},
                          context=context)
        return True

    def clear_book_customs_form(self, cr, uid, ids, context=None):
        """ Unrelate all customs form of the book """
        context = context or {}
        cf_obj = self.pool.get("customs.form")
        for fb_id in ids:
            cf_brws = self.browse(cr, uid, fb_id, context=context).cf_ids
            if cf_brws:
                cf_ids = [cf.id for cf in cf_brws]
                cf_obj.write(cr, uid, cf_ids, {'fb_id': False},
                             context=context)
        return True

    def clear_book_iwdl_ids(self, cr, uid, ids, context=None):
        """ Unrelate all wh iva lines of the book. """
        context = context or {}
        iwdl_obj = self.pool.get("account.wh.iva.line")
        for fb_id in ids:
            iwdl_brws = self.browse(cr, uid, fb_id, context=context).iwdl_ids
            iwdl_ids = [iwdl.id for iwdl in iwdl_brws]
            iwdl_obj.write(
                cr, uid, iwdl_ids, {'fb_id': False}, context=context)
        return True

    def get_doc_type(self, cr, uid, inv_id=None, iwdl_id=None, cf_id=None,
                     fb_id=None, context=None):
        """ Returns a string that indicates de document type. For withholding
        returns 'AJST' and for invoice docuemnts returns different values
        depending of the invoice type: Debit Note 'N/DE', Credit Note 'N/CR',
        Invoice 'FACT'.
        @param inv_id : invoice id
        @param iwdl_id: wh iva line id
        """
        context = context or {}
        res = False
        if fb_id:
            obj_fb = self.pool.get('fiscal.book')
            fb_brw = obj_fb.browse(cr, uid, fb_id, context=context)
        if inv_id:
            inv_obj = self.pool.get('account.invoice')
            inv_brw = inv_obj.browse(cr, uid, inv_id, context=context)
            if (inv_brw.type in ["in_invoice"] and inv_brw.parent_id) \
                    or inv_brw.type in ["in_refund"]:
                res = "N/DB"
            elif (inv_brw.type in ["out_invoice"] and inv_brw.parent_id) or \
                    inv_brw.type in ["out_refund"]:
                res = "N/CR"
            elif inv_brw.type in ["in_invoice", "out_invoice"]:
                res = "FACT"

            assert res, str(inv_brw) + ": Error in the definition \
            of the document type. \n There is not type category definied for \
            your invoice."
        elif iwdl_id:
            res = 'AJST' if fb_id and fb_brw.type == 'sale' else 'RET'
        elif cf_id:
            res = 'F/IMP'

        return res

    def get_invoice_import_form(self, cr, uid, inv_id, context=None):
        """ Returns the Invoice reference
        @param inv_id: invoice id
        """
        context = context or {}
        inv_obj = self.pool.get('account.invoice')
        inv_brw = inv_obj.browse(cr, uid, inv_id, context=context)
        return inv_brw.reference or False

    def is_invoice_imex(self, cr, uid, inv_id, context=None):
        """ Boolean method that verify is a invoice is imported by cheking the
        customs form associated.
        @param inv_id: invoice id
        """
        context = context or {}
        inv_obj = self.pool.get('account.invoice')
        inv_brw = inv_obj.browse(cr, uid, inv_id, context=context)
        return inv_brw.customs_form_id and True or False

    def get_transaction_type(self, cr, uid, fb_id, inv_id, context=None):
        """ Method that returns the type of the fiscal book line related to the
        given invoice by cheking the customs form associated and the fiscal
        book type.
        @param fb_id: fiscal book id
        @param inv_id: invoice id
        """
        context = context or {}
        inv_obj = self.pool.get('account.invoice')
        inv_brw = inv_obj.browse(cr, uid, inv_id, context=context)
        fb_brw = self.browse(cr, uid, fb_id, context=context)
        if inv_brw.customs_form_id:
            return 'ex' if fb_brw.type == 'sale' else 'im'
        else:
            if fb_brw.type == 'purchase':
                return 'do'
            else:
                return 'tp' if inv_brw.partner_id.vat_subjected else 'ntp'

    def unlink(self, cr, uid, ids, context=None):
        """ Overwrite the unlink method to throw an exception if the book is
        not in cancel state."""
        context = context or {}
        for fb_brw in self.browse(cr, uid, ids, context=context):
            if fb_brw.state != 'cancel':
                raise osv.except_osv(
                    "Invalid Procedure!!",
                    "Your book needs to be in cancel state to be deleted.")
            else:
                super(FiscalBook, self).unlink(cr, uid, ids, context=context)
        return True


class FiscalBookLines(orm.Model):

    def _get_wh_vat(self, cr, uid, ids, field_name, arg, context=None):
        """ For a given book line it returns the vat withholding amount.
        (This is a method used in functional fields).
        @param field_name: ['get_wh_vat'].
        """
        context = context or {}
        res = {}.fromkeys(ids, 0.0)
        for fbl_brw in self.browse(cr, uid, ids, context=context):
            sign = 1 if fbl_brw.doc_type != 'AJST' else -1
            if fbl_brw.iwdl_id:
                res[fbl_brw.id] = fbl_brw.iwdl_id.amount_tax_ret * sign
        return res

    def _get_based_tax_debit(self, cr, uid, ids, field_name, arg,
                             context=None):
        """ It Returns the sum of all tax amount for the taxes realeted to the
        wh iva line.
        @param field_name: ['get_based_tax_debit'].
        """
        # TODO: for all taxes realted? only a tax type group?
        context = context or {}
        res = {}.fromkeys(ids, 0.0)
        for fbl_brw in self.browse(cr, uid, ids, context=context):
            if fbl_brw.iwdl_id:
                sign = 1 if fbl_brw.doc_type != 'AJST' else -1
                for tax in fbl_brw.iwdl_id.tax_line:
                    res[fbl_brw.id] += tax.amount * sign
        return res

    def _compute_vat_rates(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for item in self.browse(cr, uid, ids, context=context):
            res[item.id] = {
                'vat_reduced_rate': item.vat_reduced_base and
                item.vat_reduced_tax * 100 / item.vat_reduced_base,
                'vat_general_rate': item.vat_general_base and
                item.vat_general_tax * 100 / item.vat_general_base,
                'vat_additional_rate': item.vat_additional_base and
                item.vat_additional_tax * 100 / item.vat_additional_base,
            }
        return res

    _description = "Venezuela's Sale & Purchase Fiscal Book Lines"
    _name = 'fiscal.book.line'
    _rec_name = 'rank'
    _order = 'parent_id, rank'
    _parent_store = "True"
    _columns = {
        'fb_id': fields.many2one(
            'fiscal.book', 'Fiscal Book',
            help='Fiscal Book that owns this book line', ondelete='cascade'),
        'ntp_fb_id': fields.many2one(
            "fiscal.book", "Non-Tax Payer Detail",
            help="Fiscal Book that owns this book line"
                 " This Book is only for Non-Tax Payer lines"),
        'fbt_ids': fields.one2many(
            'fiscal.book.taxes', 'fbl_id', string='Tax Lines',
            help="Tax Lines being recorded in a Fiscal Book"),
        'invoice_id': fields.many2one(
            'account.invoice', 'Invoice',
            help="Invoice related to this book line"),
        'iwdl_id': fields.many2one(
            'account.wh.iva.line', 'Vat Withholding',
            help="Withholding iva line related to this book line"),
        'cf_id': fields.many2one(
            'customs.form', 'Customs Form',
            help="Customs Form being recorded to this book line"),
        'parent_id': fields.many2one(
            "fiscal.book.line",
            string="Consolidated Line",
            ondelete='cascade',
            help="Non-Tax Payer Consolidated Line. Indicate the id of the"
            " consolidated line where this Non-Tax Payer line belongs"),
        'parent_left': fields.integer('Left Parent', select=1),
        'parent_right': fields.integer('Right Parent', select=1),
        'child_ids': fields.one2many(
            "fiscal.book.line",
            "parent_id",
            string="Non-Tax Payer Detail Line",
            help="Non-Tax Payer Group of book lines that this line represent"),

        #  Invoice and/or Document Data
        'rank': fields.integer(
            "Line", required=True, default=0,
            help="Line Position"),
        'emission_date': fields.date(
            string='Emission Date',
            help='Invoice Document Date / Wh IVA Line Voucher Date'),
        'accounting_date': fields.date(
            string='Accounting Date',
            help="The day of the accounting record [(invoice, date_invoice),"
            " (wh iva line, date_ret)]"),
        'doc_type': fields.char('Doc. Type', size=8, help='Document Type'),
        'partner_name': fields.char(size=128, string='Partner Name', help=''),
        'partner_vat': fields.char(size=128, string='Partner TIN', help=''),
        'affected_invoice': fields.char(
            string='Affected Invoice',
            size=64,
            help="For an invoice line type means parent invoice for a Debit"
            " or Credit Note. For an withholding line type means the invoice"
            " number related to the withholding"),
        # Apply for wh iva lines
        'get_wh_vat': fields.function(_get_wh_vat,
                                      type="float", method=True, store=True,
                                      string="VAT Withholding",
                                      help="VAT Withholding"),
        'wh_number': fields.char(string='Withholding number', size=64,
                                 help=""),
        'affected_invoice_date': fields.date(string="Affected Invoice Date",
                                             help=""),
        'wh_rate': fields.float(string="Withholding percentage",
                                help=""),
        'get_wh_debit_credit': fields.function(
            _get_based_tax_debit,
            type="float", method=True, store=True,
            string="Based Tax Debit",
            help="Sum of all tax amount for the taxes realeted to the wh iva"
            " line."),

        # Apply for invoice lines
        'ctrl_number': fields.char(string='Invoice Control number', size=64,
                                   help=''),
        'invoice_number': fields.char(string='Invoice number', size=64,
                                      help="Invoice Number. In case of use"
                                      " of fiscal printer this field will"
                                      " store the invoice number generate"
                                      " by the fiscal printer machine"),
        'imex_date': fields.date(string='Imex Date',
                                 help='Invoice Imports/Exports Date'),
        'debit_affected': fields.char(string='Affected Debit Notes',
                                      size=256,
                                      help='Debit notes affected'),
        'credit_affected': fields.char(string='Affected Credit Notes',
                                       size=256,
                                       help='Credit notes affected'),
        'type': fields.selection(
            [('im', 'Imports'),
             ('do', 'Domestic'),
             ('ex', 'Exports'),
             ('tp', 'Tax Payer'),
             ('ntp', 'Non-Tax Payer')],
            string='Transaction Type', required=True,
            help="Book line transtaction type:"
            " - Purchase: Import or Domestic."
            " - Sales: Expertation, Tax Payer, Non-Tax Payer."),
        'void_form': fields.char(string='Transaction type', size=192,
                                 help="Operation Type"),
        'fiscal_printer': fields.char(string='Fiscal machine number',
                                      size=192, help=""),
        'z_report': fields.char(string='Report Z', size=64, help=""),
        'custom_statement': fields.char(string="Custom Statement",
                                        size=192, help=""),
        # -- taxes fields
        'total_with_iva': fields.float('Total with IVA', help="Sub Total of"
                                       " the invoice (untaxed amount) plus"
                                       " all tax amount of the related taxes"),
        'vat_sdcf': fields.float(
            "SDCF",
            help="Not entitled to tax credit (The field name correspond to the"
                 " spanih acronym for 'Sin Derecho a Credito Fiscal')"),
        'vat_exempt': fields.float("Exempt", help="Exempt is a Tax with 0"
                                   " tax percentage"),
        'vat_reduced_base': fields.float("RED BASE", help="Vat Reduced Base"
                                         " Amount"),
        'vat_reduced_tax': fields.float("RED TAX", help="Vat Reduced Tax"
                                        " Amount"),
        'vat_general_base': fields.float("GRAL BASE", help="Vat General Base"
                                         " Amount"),
        'vat_general_tax': fields.float("GRAL TAX", help="Vat General Tax"
                                        " Amount"),
        'vat_additional_base': fields.float("ADD BASE", help="Vat Generald"
                                            " plus Additional Base Amount"),
        'vat_additional_tax': fields.float("ADD TAX", help="Vat General plus"
                                           " Additional Tax Amount"),
        'vat_reduced_rate': fields.function(
            _compute_vat_rates, method=True, type='float',
            string='Reduced rate', multi='all',
            help="Vat reduced tax rate "),
        'vat_general_rate': fields.function(
            _compute_vat_rates, method=True, type='float',
            string='General rate', multi='all',
            help="Vat general tax rate "),
        'vat_additional_rate': fields.function(
            _compute_vat_rates, method=True, type='float',
            string='Additional rate', multi='all',
            help="Vat plus additional tax rate "),
    }


class FiscalBookTaxes(orm.Model):

    _description = "Venezuela's Sale & Purchase Fiscal Book Taxes"
    _name = 'fiscal.book.taxes'
    _rec_name = 'ait_id'
    _columns = {
        'name': fields.related('ait_id', 'name', size=64,
                               relation="account.invoice.tax", type="char",
                               string='Description', store=True),
        'fb_id': fields.many2one(
            'fiscal.book', 'Fiscal Book',
            help='Fiscal Book where this tax is related to'),
        'fbl_id': fields.many2one(
            'fiscal.book.line', 'Fiscal Book Lines',
            help='Fiscal Book Lines where this tax is related to'),
        'base_amount': fields.related('ait_id', 'base_amount',
                                      relation="account.invoice.tax",
                                      type="float", string='Taxable Amount',
                                      help='Amount used as Taxing Base',
                                      store=True),
        'tax_amount': fields.related('ait_id', 'tax_amount',
                                     relation="account.invoice.tax",
                                     type="float", string='Taxed Amount',
                                     help='Taxed Amount on Taxing Base',
                                     store=True),
        'ait_id': fields.many2one(
            'account.invoice.tax', 'Tax',
            help='Tax where is related to'),
    }


class FiscalBookTaxesSummary(orm.Model):

    _description = "Venezuela's Sale & Purchase Fiscal Book Taxes Summary"
    _name = 'fiscal.book.taxes.summary'
    _order = 'op_type, tax_type asc'
    _columns = {
        'fb_id': fields.many2one('fiscal.book', 'Fiscal Book'),
        'tax_type': fields.selection(
            [('exento', '0% Exento'),
             ('sdcf', 'Not entitled to tax credit'),
             ('general', 'General Aliquot'),
             ('reducido', 'Reducted Aliquot'),
             ('adicional', 'General Aliquot + Additional')],
            'Tax Type'),
        'op_type': fields.selection(
            [('im', 'Imports'),
             ('do', 'Domestic'),
             ('ex', 'Exports'),
             ('tp', 'Tax Payer'),
             ('ntp', 'Non-Tax Payer')],
            string='Operation Type',
            help="Operation Type:"
            " - Purchase: Import or Domestic."
            " - Sales: Expertation, Tax Payer, Non-Tax Payer."),
        'base_amount_sum': fields.float('Taxable Amount Sum'),
        'tax_amount_sum': fields.float('Taxed Amount Sum'),
    }


class AdjustmentBookLine(orm.Model):

    _name = 'adjustment.book.line'
    _columns = {
        'date_accounting': fields.date(
            'Date Accounting', required=True,
            help="Date accounting for adjustment book"),
        'date_admin': fields.date(
            'Date Administrative', required=True,
            help="Date administrative for adjustment book"),
        'vat': fields.char(
            'Vat', size=10, required=True,
            help="Vat of partner for adjustment book"),
        'partner': fields.char(
            'Partner', size=256, required=True,
            help="Partner for adjustment book"),
        'invoice_number': fields.char(
            'Invoice Number', size=256, required=True,
            help="Invoice number for adjustment book"),
        'control_number': fields.char(
            'Invoice Control', size=256, required=True,
            help="Invoice control for adjustment book"),
        'amount': fields.float(
            'Amount Document at VAT Withholding',
            digits_compute=dp.get_precision('Account'), required=True,
            help="Amount document for adjustment book"),
        'type_doc': fields.selection([
            ('F', 'Invoice'), ('ND', 'Debit Note'), ('NC', 'Credit Note'), ],
            'Document Type', select=True, required=True,
            help="Type of Document for adjustment book:"
            " -Invoice(F),-Debit Note(dn),-Credit Note(cn)"),
        'doc_affected': fields.char(
            'Affected Document', size=256, required=True,
            help="Affected Document for adjustment book"),
        'uncredit_fiscal': fields.float(
            'Sin derecho a Credito Fiscal',
            digits_compute=dp.get_precision('Account'), required=True,
            help="Sin derechoa credito fiscal"),
        'amount_untaxed_n': fields.float(
            'Amount Untaxed',
            digits_compute=dp.get_precision('Account'), required=True,
            help="Amount untaxed for national operations"),
        'percent_with_vat_n': fields.float(
            'VAT Withholding (%)',
            digits_compute=dp.get_precision('Account'), required=True,
            help="VAT percent (%) for national operations"),
        'amount_with_vat_n': fields.float(
            'VAT Withholding Amount',
            digits_compute=dp.get_precision('Account'), required=True,
            help="Percent(%) VAT for national operations"),
        'amount_untaxed_i': fields.float(
            'Amount Untaxed',
            digits_compute=dp.get_precision('Account'), required=True,
            help="Amount untaxed for international operations"),
        'percent_with_vat_i': fields.float(
            'VAT Withholding (%)',
            digits_compute=dp.get_precision('Account'), required=True,
            help="VAT percent (%) for international operations"),
        'amount_with_vat_i': fields.float(
            'VAT Withholding Amount',
            digits_compute=dp.get_precision('Account'), required=True,
            help="VAT amount for international operations"),
        'amount_with_vat': fields.float(
            'VAT Withholding Total Amount',
            digits_compute=dp.get_precision('Account'), required=True,
            help="VAT withholding total amount"),
        'voucher': fields.char(
            'VAT Withholding Voucher', size=256,
            required=True, help="VAT withholding voucher"),
        'fb_id': fields.many2one(
            'fiscal.book', 'Fiscal Book',
            help='Fiscal Book where this line is related to'),
    }
    _rec_rame = 'partner'
