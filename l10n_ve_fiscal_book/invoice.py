#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############################################################################
#    Credits:
#    Coded by:       Luis Escobar <luis@vauxoo.com>
#                    Tulio Ruiz <tulio@vauxoo.com>
#    Planified by: Nhomar Hernandez
#############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
##############################################################################

from openerp.osv import fields, osv


class inherited_invoice(osv.osv):
    _inherit = "account.invoice"

    def _get_date_document(self, cr, uid, ids, name, args, context=None):
        '''
        Get date document if it is not an import
        '''
        res = self.browse(cr, uid, ids)
        ret = {}
        for i in ids:
            ret.update({i: ''})
        if res:
            for inv_brw in res:
                if not inv_brw.get_is_imported:
                    ret.update({inv_brw.id: inv_brw.date_document})
#                ret =r.date_document
        return ret

    def _get_date_invoice(self, cr, uid, ids, name, args, context=None):
        '''
        Get Date Invoce
        '''
        res = self.browse(cr, uid, ids)
        ret = {}
        for i in ids:
            ret.update({i: ''})
        if res:
            for inv_brw in res:
                ret.update({inv_brw.id: inv_brw.date_invoice})
#                ret =r.date_document
        return ret

    def _get_date_invoiced(self, cr, uid, ids, name, args, context=None):
        '''
        Get The date invoiced if the document is not an import
        '''

        res = self.browse(cr, uid, ids)
        ret = {}
        for i in ids:
            ret.update({i: ''})
        if res:
            for inv_brw in res:
                if not inv_brw.get_is_imported:
                    ret.update({inv_brw.id: inv_brw.date_invoice})
#                ret =r.date_document
        return ret

    def _get_vat(self, cr, uid, ids, name, args, context=None):
        '''
        Get Partner vat without two first letters
        '''
        res = self.browse(cr, uid, ids)
        ret = {}
        for i in ids:
            ret.update({i: 'N/A'})
        if res:
            for inv_brw in res:
                if inv_brw.partner_id.vat:
                    ret.update({inv_brw.id: inv_brw.partner_id.vat[2:]})
        return ret

    def _get_name(self, cr, uid, ids, name, args, context=None):
        '''
        Get Partner Name
        '''
        res = self.browse(cr, uid, ids)
        ret = {}
        if res:
            for inv_brw in res:
                ret.update({inv_brw.id: inv_brw.partner_id.name})
        return ret

    def _get_inv_number(self, cr, uid, ids, name, args, context=None):
        '''
        Get Invoice Number
        '''
        res = self.browse(cr, uid, ids)
        ret = {}
        for i in ids:
            ret.update({i: ''})
        if res:
            for inv_brw in res:
                ret.update({inv_brw.id:
                            inv_brw.number and str(inv_brw.number) or ''})
        return ret

    def _get_reference(self, cr, uid, ids, name, args, context=None):
        '''
        Get Invoice reference
        '''
        res = self.browse(cr, uid, ids)
        ret = {}
        for i in ids:
            ret.update({i: ''})
        if res:
            for inv_brw in res:
                ret.update({inv_brw.id:
                            inv_brw.reference and inv_brw.reference or ''})
        return ret

    def _get_control_number(self, cr, uid, ids, name, args, context=None):
        '''
        Get Invoice Control Number
        '''
        res = self.browse(cr, uid, ids)
        ret = {}
        if res:
            for inv_brw in res:
                ret.update({inv_brw.id:
                            inv_brw.nro_ctrl and inv_brw.nro_ctrl or ''})
        return ret

    def _get_total(self, cr, uid, ids, name, args, context=None):
        '''
        Get Total Invoice Amount
        '''
        res = self.browse(cr, uid, ids)
        ret = {}
        for i in ids:
            ret.update({i: 0})
        if res:
            for inv_brw in res:
                ret.update({inv_brw.id: inv_brw.amount_total})
        return ret

    def _get_wh_number(self, cr, uid, ids, name, args, context=None):
        '''
        Get Wh Number if any
        '''
        whl_obj = self.pool.get('account.wh.iva.line')

        ret = {}
        for i in ids:
            ret.update({i: ''})

        for inv_brw in ids:
            ret.update({inv_brw: False})
            whl_ids = whl_obj.search(cr, uid, [('invoice_id', '=', inv_brw)])
            whl_brw = whl_obj.browse(cr, uid, whl_ids)
            if whl_brw:
                for whl in whl_brw:
                    ret.update({inv_brw: whl.retention_id.number})
        return ret

    def _get_doc(self, cr, uid, ids, name, args, context=None):
        '''
        Get String Document Type
        '''
        invs = self.browse(cr, uid, ids)
        doc_type = ''
        ret = {}
        for i in ids:
            ret.update({i: ''})
        if invs:
            for inv in invs:
                if ((inv.type == "in_invoice" or inv.type == "out_invoice")
                        and inv.parent_id):
                    doc_type = "ND"
                elif ((inv.type == "in_invoice" or inv.type == "in_refund")
                      and inv.expedient):
                    doc_type = "E"
                elif inv.type == 'in_refund' or inv.type == 'out_refund':
                    doc_type = "NC"
                elif inv.type == "in_invoice" or inv.type == "out_invoice":
                    doc_type = "F"
                ret.update({inv.id: doc_type})
        return ret

    def _get_t_doc(self, cr, uid, ids, name, args, context=None):
        '''
        Get String Document Type
        '''
        invs = self.browse(cr, uid, ids)
        doc_type = ''
        ret = {}
        for i in ids:
            ret.update({i: ''})
        if invs:
            for inv in invs:
                if ((inv.type == "in_invoice" or inv.type == "out_invoice")
                        and inv.parent_id):
                    doc_type = "N/DE"
                elif ((inv.type == "in_invoice" or inv.type == "in_refund")
                      and inv.expedient):
                    doc_type = "E"
                elif inv.type == 'in_refund' or inv.type == 'out_refund':
                    doc_type = "N/CR"
                elif inv.type == "in_invoice" or inv.type == "out_invoice":
                    doc_type = "FACT"
                ret.update({inv.id: doc_type})
        return ret

    def _get_parent(self, cr, uid, ids, name, args, context=None):
        '''
        Get Parent Invoice
        '''
        res = self.browse(cr, uid, ids)
        ret = {}
        for i in ids:
            ret.update({i: None})
        if res:
            for inv_brw in res:
                ret.update({inv_brw.id: inv_brw.parent_id.number})
        return ret

    def _get_v_sdcf(self, cr, uid, ids, name, args, context=None):
        '''
        Get SDCF Amount
        '''
        res = self.browse(cr, uid, ids)
        ret = {}
        for i in ids:
            ret.update({i: 0.0})
        if not res:
            return ret
        for inv_brw in res:
            amount = 0.0
            for tax in inv_brw.tax_line:
                name = tax.name
                if name.find('SDCF') >= 0:
                    amount = tax.base + amount
                    if inv_brw.type in ['in_refund', 'out_refund']:
                        amount = amount * (-1)
            ret.update({inv_brw.id: amount})
        return ret

    def _get_v_exent(self, cr, uid, ids, name, args, context=None):
        '''
        Get Amount Exempt
        '''
        res = self.browse(cr, uid, ids)
        ret = {}
        for i in ids:
            ret.update({i: 0.0})
        if not res:
            return ret
        for inv_brw in res:
            amount = 0.0
            for tax in inv_brw.tax_line:
                name = tax.name
                if name.find('EXENTO') >= 0:
                    amount += tax.base
            if inv_brw.type in ['in_refund', 'out_refund']:
                amount = amount * (-1.0)
            ret.update({inv_brw.id: amount})
        return ret

    def _get_inv_tax_line(self, tax_brw):
        '''
        Get Tax Line
        '''
        name = tax_brw.name
        cont = 0
        if name.find('SDCF') >= 0:
            if cont == 0:
                return 0
        else:
            cont = cont + 1
        return tax_brw.base_amount

    def _get_taxes(self, cr, uid, ids, name, args, context=None):
        '''
        Get Invoice Taxes
        '''
        tax_obj = self.pool.get('account.invoice.tax')
        ret = {}
        for inv in ids:
            tax_ids = tax_obj.search(cr, uid, [('invoice_id', '=', inv)])
            tam = len(tax_ids)
            data = tax_obj.browse(cr, uid, tax_ids)

            for tax in data:
                if ('SDCF' in tax.name and tax.tax_id.amount == 0.00
                        and tam >= 2):
                    tax_ids.remove(tax.id)
                elif ('EXENTO' in tax.name and tax.tax_id.amount == 0.00
                      and tam >= 2):
                    tax_ids.remove(tax.id)
                elif tax.tax_id.amount == 0.00 and tam >= 2:
                    tax_ids.remove(tax.id)

            data = tax_obj.browse(cr, uid, tax_ids)
            if data:
                ret.update({inv: data})
            else:
                ret.update({inv: False})

        return ret

    def _get_papel_anulado(self, cr, uid, ids, name, args, context=None):
        '''
        Get Operation Type
        '''
        tipo = '03-ANU'
        data = '01-REG'
        res = self.browse(cr, uid, ids)
        ret = {}
        if res:
            for inv_brw in res:
                if inv_brw.name:
                    if inv_brw.name.find('PAPELANULADO') >= 0:
                        ret.update({inv_brw.id: tipo})
                    else:
                        ret.update({inv_brw.id: data})
                else:
                    # data = self._get_doc(cr, uid, ids, name, args, context)
                    ret.update({inv_brw.id: data})
        return ret

    def _get_lang(self, cr, uid, ids, name, args, context=None):
        '''
        Get Lang from partner
        '''
        res = self.browse(cr, uid, ids)
        ret = {}
        if res:
            for inv_brw in res:
                ret.update({inv_brw.id: inv_brw.company_id.partner_id.lang})
        return ret

    def _get_nro_inport_form(self, cr, uid, ids, name, args, context=None):
        res = self.browse(cr, uid, ids)
        ret = {}
        for i in ids:
            ret.update({i: ''})
        for inv_brw in res:
            if hasattr(inv_brw, 'num_import_form'):
                if inv_brw.num_import_form:
                    ret.pudate({inv_brw.id: inv_brw.num_import_form})
        return ret

    def _get_nro_inport_expe(self, cr, uid, ids, name, args, context=None):
        res = self.browse(cr, uid, ids)
        ret = {}
        for i in ids:
            ret.update({i: ''})
        for inv_brw in res:
            if hasattr(inv_brw, 'num_import_expe'):
                if inv_brw.num_import_expe:
                    ret.pudate({inv_brw.id: inv_brw.nro_inport_expe})
        return ret

    def _get_vat_subjected(self, cr, uid, ids, name, args, context=None):
        '''
        Get if partner is vat subjected
        '''
        res = self.browse(cr, uid, ids)
        ret = {}
        for i in ids:
            ret.update({i: False})
#        if not res:
#            return ret
        for inv_brw in res:
            ret.update({inv_brw.id: inv_brw.partner_id.vat_subjected})
        return ret

    def _get_debit_affected(self, cr, uid, ids, name, args, context=None):
        '''
        Get invoice affected
        '''
        res = self.browse(cr, uid, ids)
        ret = {}
        for inv_brw in res:
            if (inv_brw.parent_id and
                    inv_brw.parent_id.type in ['in_invoice', 'out_invoice']
                    and inv_brw.parent_id.parent_id):
                ret.update({inv_brw.id: inv_brw.parent_id.number})
            else:
                ret.update({inv_brw.id: ''})
        return ret

    def _get_credit_affected(self, cr, uid, ids, name, args, context=None):
        '''
        Get invoice affected
        '''
        res = self.browse(cr, uid, ids)
        ret = {}
        for inv_brw in res:
            if (inv_brw.parent_id
                    and inv_brw.parent_id.type in ['in_refund', 'out_refund']):
                ret.update({inv_brw.id: inv_brw.parent_id.number})
            else:
                ret.update({inv_brw.id: ''})
        return ret
#                if ((inv.type=="in_invoice" or inv.type=="out_invoice")
#                    and inv.parent_id):
#                    doc_type = "N/DE"
#                elif ((inv.type=="in_invoice" or inv.type=="in_refund") and
#                inv.expedient):
#                    doc_type="E"
#                elif inv.type=='in_refund' or inv.type=='out_refund':
#                    doc_type = "N/CR"
#                elif inv.type=="in_invoice" or inv.type=="out_invoice":
#                    doc_type = "FACT"

    def _get_invoice_affected(self, cr, uid, ids, name, args, context=None):
        '''
        Get Invoice affected if parente invoice is an invoice else return empty
        '''

        res = self.browse(cr, uid, ids)
        ret = {}
        for inv_brw in res:
            if (inv_brw.parent_id and
                    inv_brw.parent_id.type in ['in_invoice', 'out_invoice']):
                ret.update({inv_brw.id: inv_brw.parent_id.number})
            else:
                ret.update({inv_brw.id: ''})
        return ret

    def _get_is_imported(self, cr, uid, ids, name, args, context=None):
        '''
        Get If document is an import
        '''
        res = self.browse(cr, uid, ids)
        ret = {}
        for i in ids:
            ret.update({i: False})
        for inv_brw in res:
            if (inv_brw.company_id.partner_id.country.id !=
                    inv_brw.partner_id.country.id):
                ret.update({inv_brw.id: True})
        return ret

    def _get_date_imported(self, cr, uid, ids, name, args, context=None):
        '''
        Get Date Imported if it is imported, else an empty string is returned
        '''
        res = self.browse(cr, uid, ids)
        ret = {}
        for i in ids:
            ret.update({i: ''})
        for inv_brw in res:
            if inv_brw.get_is_imported:
                ret.update({inv_brw.id: inv_brw.get_date_invoice})
        return ret

    def _get_import_spreadsheets(self, cr, uid, ids, name, args, context=None):
        '''
        Get Import Spreadsheets
        '''
        ret = {}
        for i in ids:
            ret.update({i: []})
        for inv in ids:
            isp_ids = self.search(cr, uid, [
                ('affected_invoice', '=', inv),
                ('state', 'in', ['done', 'paid', 'open'])])
#            print isp_ids
            if isp_ids:
                res = self.browse(cr, uid, isp_ids)
                ret.update({inv: res})
#                print ret
        return ret

    def _get_invoice_printer(self, cr, uid, ids, name, args, context=None):
        '''
        Get Fiscal Printer Invoice Number
        '''
        res = self.browse(cr, uid, ids)
        ret = {}
        for i in ids:
            ret.update({i: ''})
        for inv_brw in res:
            ret.update({inv_brw.id: inv_brw.invoice_printer})
        return ret

    def _get_fiscal_printer(self, cr, uid, ids, name, args, context=None):
        '''
        Get Fiscal Machine Number
        '''
        res = self.browse(cr, uid, ids)
        ret = {}
        for i in ids:
            ret.update({i: ''})
        for inv_brw in res:
            ret.update({inv_brw.id: inv_brw.fiscal_printer})
        return ret

    _columns = {
        'get_date_document': fields.function(
            _get_date_document, method=True, string='Document date',
            type='date', help=""),
        'get_date_invoice': fields.function(
            _get_date_invoice, method=True, string='Invoice date', type='date',
            help=""),
        'get_partner_name': fields.function(
            _get_name, method=True, string='Partner Name', type='char',
            help=""),
        'get_partner_vat': fields.function(
            _get_vat, method=True, string='Partner vat', type='char',
            help=""),
        'get_reference': fields.function(
            _get_inv_number, method=True, string='Invoice number', type='char',
            help=""),
        'get_number': fields.function(
            _get_control_number, method=True, string='Control number',
            type='char', help=""),
        'get_total': fields.function(
            _get_total, method=True, string='Invoice total', type='float',
            help=""),
        'get_wh_number': fields.function(
            _get_wh_number, method=True, string='Wh document number',
            type='char', help=""),
        'get_doc': fields.function(
            _get_doc, method=True, string='Transaction Type', type='char',
            help=""),
        'get_t_doc': fields.function(
            _get_t_doc, method=True, string='Document Type', type='char',
            help=""),
        'get_parent': fields.function(
            _get_invoice_affected, method=True, string='Parent invoice',
            type='char', help=""),
        'get_v_sdcf': fields.function(
            _get_v_sdcf, method=True, string='SDCF', type='float', help=""),
        'get_v_exent': fields.function(
            _get_v_exent, method=True, string='Amount excempt', type='float',
            help=""),
        'get_tax_line': fields.function(
            _get_inv_tax_line, method=True, string='Tax line', type='char',
            help=""),
        #   'get_parent': fields.function(_get_parent, method=True,
        #       string='kind of document', type='char', help=""),
        'get_lang': fields.function(
            _get_lang, method=True, string='Language', type='char',
            help=""),
        'get_taxes': fields.function(
            _get_taxes, method=True, string='Invoice Taxes', type='char',
            help=""),
        'get_papel_anulado': fields.function(
            _get_papel_anulado, method=True, string='Transaction type',
            type='char', help=""),
        'get_nro_inport_form': fields.function(
            _get_nro_inport_form, method=True, string='Import form number',
            type='char', help=""),
        'get_nro_inport_expe': fields.function(
            _get_nro_inport_expe, method=True, string='Import file number',
            type='char', help=""),
        'get_vat_subjected': fields.function(
            _get_vat_subjected, method=True, string='Vat subjected',
            type='boolean', help=""),
        'get_debit_affected': fields.function(
            _get_debit_affected, method=True, string='Debit notes affected',
            type='char', help=""),
        'get_credit_affected': fields.function(
            _get_credit_affected, method=True, string='Credit notes affected',
            type='char', help=""),
        'get_import_form': fields.function(
            _get_reference, method=True, string='kind of document',
            type='char', help=""),
        'get_import_exp': fields.function(
            _get_nro_inport_expe, method=True, string='kind of document',
            type='char', help=""),
        'get_is_imported': fields.function(
            _get_is_imported, method=True, string='Is an import',
            type='boolean', help=""),
        'get_date_imported': fields.function(
            _get_date_imported, method=True, string='Imported date',
            type='date', help=""),
        'get_date_invoiced': fields.function(
            _get_date_invoiced, method=True, string='Invoiced date',
            type='date', help=""),
        'get_import_spreadsheets': fields.function(
            _get_import_spreadsheets, method=True,
            string='Import spreadsheets', type='date', help=""),
        'get_invoice_printer': fields.function(
            _get_invoice_printer, method=True,
            string='Fiscal printer invoice number', type='char', help=""),
        'get_fiscal_printer': fields.function(
            _get_fiscal_printer, method=True, string='Fiscal machine number',
            type='char', help=""),
    }

inherited_invoice()
