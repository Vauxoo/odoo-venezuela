# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############################################################################
#    Credits:
#    Coded by: Humberto Arocha           <humberto@openerp.com.ve>
#              Maria Gabriela Quilarque  <gabriela@openerp.com.ve>
#              Javier Duran              <javier@nvauxoo.com>
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
import base64
import time

from openerp.osv import fields, osv
from openerp.tools.translate import _


class txt_iva(osv.osv):
    _name = "txt.iva"
    _inherit = ['mail.thread']

    def _get_amount_total(self, cr, uid, ids, name, args, context=None):
        """ Return total amount withheld of each selected bill
        """
        context = context or {}
        res = {}
        for txt in self.browse(cr, uid, ids, context):
            res[txt.id] = 0.0
            for txt_line in txt.txt_ids:
                if txt_line.invoice_id.type in ['out_refund', 'in_refund']:
                    res[txt.id] -= txt_line.amount_withheld
                else:
                    res[txt.id] += txt_line.amount_withheld
        return res

    def _get_amount_total_base(self, cr, uid, ids, name, args, context=None):
        """ Return total amount base of each selected bill
        """
        context = context or {}
        res = {}
        for txt in self.browse(cr, uid, ids, context):
            res[txt.id] = 0.0
            for txt_line in txt.txt_ids:
                if txt_line.invoice_id.type in ['out_refund', 'in_refund']:
                    res[txt.id] -= txt_line.untaxed
                else:
                    res[txt.id] += txt_line.untaxed
        return res

    _columns = {
        'name': fields.char(
            'Description', 128, required=True, select=True,
            help="Description about statement of withholding income"),
        'company_id': fields.many2one(
            'res.company', 'Company', required=True, readonly=True,
            states={'draft': [('readonly', False)]}, help='Company'),
        'state': fields.selection([
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'),
            ('done', 'Done'),
            ('cancel', 'Cancelled')
        ], 'Estado', select=True, readonly=True, help="proof status"),
        'period_id': fields.many2one(
            'account.period', 'Period', required=True, readonly=True,
            states={'draft': [('readonly', False)]}, help='fiscal period'),
        'type': fields.boolean(
            'Retention Suppliers?', required=True,
            states={'draft': [('readonly', False)]},
            help="Select the type of retention to make"),
        'date_start': fields.date(
            'Begin Date', required=True,
            states={'draft': [('readonly', False)]},
            help="Begin date of period"),
        'date_end': fields.date(
            'End date', required=True, states={'draft': [('readonly', False)]},
            help="End date of period"),
        'txt_ids': fields.one2many(
            'txt.iva.line', 'txt_id', readonly=True,
            states={'draft': [('readonly', False)]},
            help='Txt field lines of ar required by SENIAT for'
                 ' VAT withholding'),
        'amount_total_ret': fields.function(
            _get_amount_total, method=True, digits=(16, 2), readonly=True,
            string='Withholding total amount', help="Monto Total Retenido"),
        'amount_total_base': fields.function(
            _get_amount_total_base, method=True, digits=(16, 2), readonly=True,
            string='Taxable total amount', help="Total de la Base Imponible"),
    }
    _defaults = {
        'state': lambda *a: 'draft',
        'company_id': lambda self, cr, uid, context:
        self.pool.get('res.users').browse(cr, uid, uid,
                                          context=context).company_id.id,
        'type': lambda *a: True,
        'period_id': lambda self, cr, uid, context: self.period_return(
            cr, uid, context),
        'name': (lambda self, cr, uid, context:
                 'Withholding Vat ' + time.strftime('%m/%Y'))
    }

    def period_return(self, cr, uid, context=None):
        """ Return current period
        """
        context = context or {}
        period_obj = self.pool.get('account.period')
        fecha = time.strftime('%m/%Y')
        period_id = period_obj.search(cr, uid, [('code', '=', fecha)])
        if period_id:
            return period_id[0]
        else:
            return False

    def name_get(self, cr, uid, ids, context=None):
        """ Return a list with id and name of the current register
        """
        context = context or {}
        if not len(ids):
            return []
        res = [(r['id'], r['name'])
               for r in self.read(cr, uid, ids, ['name'], context)]
        return res

    def action_anular(self, cr, uid, ids, context=None):
        """ Return document state to draft
        """
        context = context or {}
        return self.write(cr, uid, ids, {'state': 'draft'})

    def check_txt_ids(self, cr, uid, ids, context=None):
        """ Check that txt_iva has lines to process."""
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        awi_brw = self.browse(cr, uid, ids[0], context=context)
        if not awi_brw.txt_ids:
            raise osv.except_osv(
                _("Missing Values !"),
                _("Missing VAT TXT Lines!!!"))
        return True

    def action_confirm(self, cr, uid, ids, context=None):
        """ Transfers the document status to confirmed
        """
        context = context or {}
        self.check_txt_ids(cr, uid, ids, context=context)
        return self.write(cr, uid, ids, {'state': 'confirmed'})

    def action_generate_lines_txt(self, cr, uid, ids, context=None):
        """ Current lines are cleaned and rebuilt
        """
        context = context or {}
        rp_obj = self.pool.get('res.partner')
        voucher_obj = self.pool.get('account.wh.iva')
        txt_iva_obj = self.pool.get('txt.iva.line')
        voucher_ids = ''
        txt_brw = self.browse(cr, uid, ids[0])
        txt_ids = txt_iva_obj.search(cr, uid, [('txt_id', '=', txt_brw.id)])
        if txt_ids:
            txt_iva_obj.unlink(cr, uid, txt_ids)

        if txt_brw.type:
            voucher_ids = voucher_obj.search(
                cr, uid, [('date_ret', '>=', txt_brw.date_start),
                          ('date_ret', '<=', txt_brw.date_end),
                          ('period_id', '=', txt_brw.period_id.id),
                          ('state', '=', 'done'),
                          ('type', 'in', ['in_invoice', 'in_refund'])])
        else:
            voucher_ids = voucher_obj.search(
                cr, uid, [('date_ret', '>=', txt_brw.date_start),
                          ('date_ret', '<=', txt_brw.date_end),
                          ('period_id', '=', txt_brw.period_id.id),
                          ('state', '=', 'done'),
                          ('type', 'in', ['out_invoice', 'out_refund'])])

        for voucher in voucher_obj.browse(cr, uid, voucher_ids):
            acc_part_id = rp_obj._find_accounting_partner(voucher.partner_id)
            for voucher_lines in voucher.wh_lines:
                if voucher_lines.invoice_id.state not in ['open', 'paid']:
                    continue
                for voucher_tax_line in voucher_lines.tax_line:
                    txt_iva_obj.create(
                        cr, uid,
                        {'partner_id': acc_part_id.id,
                         'voucher_id': voucher.id,
                         'invoice_id': voucher_lines.invoice_id.id,
                         'txt_id': txt_brw.id,
                         'untaxed': voucher_tax_line.base,
                         'amount_withheld': voucher_tax_line.amount_ret,
                         'tax_wh_iva_id': voucher_tax_line.id,
                         })
        return True

    def action_done(self, cr, uid, ids, context=None):
        """ Transfer the document status to done
        """
        context = context or {}
        root = self.generate_txt(cr, uid, ids)
        self._write_attachment(cr, uid, ids, root, context)
        self.write(cr, uid, ids, {'state': 'done'})

        return True

    def get_type_document(self, cr, uid, txt_line):
        """ Return the document type
        @param txt_line: line of the current document
        """
        inv_type = '03'
        if txt_line.invoice_id.type in ['out_invoice', 'in_invoice']:
            inv_type = '01'
        elif (txt_line.invoice_id.type in ['out_invoice', 'in_invoice']
              and txt_line.invoice_id.parent_id):
            inv_type = '02'
        return inv_type

    def get_document_affected(self, cr, uid, txt_line, context=None):
        """ Return the reference or number depending of the case
        @param txt_line: line of the current document
        """
        context = context or {}
        number = '0'
        if (txt_line.invoice_id.type in ['in_invoice', 'in_refund']
                and txt_line.invoice_id.parent_id):
            number = txt_line.invoice_id.parent_id.supplier_invoice_number
        elif txt_line.invoice_id.parent_id:
            number = txt_line.invoice_id.parent_id.number
        return number

    def get_number(self, cr, uid, number, inv_type, max_size):
        """ Return a list of number for document number
        @param number: list of characters from number or reference of the bill
        @param inv_type: invoice type
        @param long: max size oh the number
        """
        if not number:
            return '0'
        result = ''
        for i in number:
            if inv_type == 'vou_number' and i.isdigit():
                if len(result) < max_size:
                    result = i + result
            elif i.isalnum():
                if len(result) < max_size:
                    result = i + result
        return result[::-1].strip()

    def get_document_number(self, cr, uid, ids, txt_line, inv_type,
                            context=None):
        """ Return the number o reference of the invoice into txt line
        @param txt_line: One line of the current txt document
        @param inv_type: invoice type into txt line
        """
        context = context or {}
        number = 0
        if txt_line.invoice_id.type in ['in_invoice', 'in_refund']:
            if not txt_line.invoice_id.supplier_invoice_number:
                raise osv.except_osv(
                    _('Invalid action !'),
                    _("Unable to make txt file, because the bill has no"
                      " reference number free!"))
            else:
                number = self.get_number(
                    cr, uid,
                    txt_line.invoice_id.supplier_invoice_number.strip(),
                    inv_type, 20)
        elif txt_line.invoice_id.number:
            number = self.get_number(
                cr, uid, txt_line.invoice_id.number.strip(), inv_type, 20)
        return number

    def get_amount_exempt_document(self, cr, uid, txt_line):
        """ Return total amount not entitled to tax credit and the remaining
        amounts
        @param txt_line: One line of the current txt document
        """
        tax = 0
        amount_doc = 0
        for tax_line in txt_line.invoice_id.tax_line:
            if 'SDCF' in tax_line.name or \
                    (tax_line.base and not tax_line.amount):
                tax = tax_line.base + tax
            else:
                amount_doc = tax_line.base + amount_doc
        return (tax, amount_doc)

    def get_buyer_vendor(self, cr, uid, txt, txt_line):
        """ Return the buyer and vendor of the sale or purchase invoice
        @param txt: current txt document
        @param txt_line: One line of the current txt document
        """
        rp_obj = self.pool.get('res.partner')
        vat_company = rp_obj._find_accounting_partner(
            txt.company_id.partner_id).vat[2:]
        vat_partner = rp_obj._find_accounting_partner(
            txt_line.partner_id).vat[2:]
        if txt_line.invoice_id.type in ['out_invoice', 'out_refund']:
            vendor = vat_company
            buyer = vat_partner
        else:
            buyer = vat_company
            vendor = vat_partner
        return (vendor, buyer)

    def get_max_aliquot(self, cr, uid, txt_line):
        """Get maximum aliquot per invoice"""
        res = []
        for tax_line in txt_line.invoice_id.tax_line:
            res.append(int(tax_line.tax_id.amount * 100))
        return max(res)

    def get_amount_line(self, cr, uid, txt_line, amount_exempt):
        """Method to compute total amount"""
        ali_max = self.get_max_aliquot(cr, uid, txt_line)
        exempt = 0

        if ali_max == int(txt_line.tax_wh_iva_id.tax_id.amount * 100):
            exempt = amount_exempt
        total = (txt_line.tax_wh_iva_id.base + txt_line.tax_wh_iva_id.amount +
                 exempt)
        return total, exempt

    def get_alicuota(self, cr, uid, txt_line):
        """ Return aliquot of the withholding into line
        @param txt_line: One line of the current txt document
        """
        return int(txt_line.tax_wh_iva_id.tax_id.amount * 100)

    def generate_txt(self, cr, uid, ids, context=None):
        """ Return string with data of the current document
        """
        context = context or {}
        txt_string = ''
        rp_obj = self.pool.get('res.partner')
        for txt in self.browse(cr, uid, ids, context):
            vat = rp_obj._find_accounting_partner(
                txt.company_id.partner_id).vat[2:]
            vat = vat
            for txt_line in txt.txt_ids:

                vendor, buyer = self.get_buyer_vendor(cr, uid, txt, txt_line)
                period = txt.period_id.name.split('/')
                period2 = period[0] + period[1]
                # TODO: use the start date of the period to get the period2
                # with the 'YYYYmm'

                operation_type = ('V' if txt_line.invoice_id.type in
                                  ['out_invoice', 'out_refund'] else 'C')
                document_type = self.get_type_document(cr, uid, txt_line)
                document_number = self.get_document_number(
                    cr, uid, ids, txt_line, 'inv_number')
                control_number = self.get_number(
                    cr, uid, txt_line.invoice_id.nro_ctrl, 'inv_ctrl', 20)
                document_affected = self.get_document_affected(cr, uid,
                                                               txt_line)
                voucher_number = self.get_number(
                    cr, uid, txt_line.voucher_id.number, 'vou_number', 14)
                amount_exempt, amount_untaxed = \
                    self.get_amount_exempt_document(cr, uid, txt_line)
                amount_untaxed = amount_untaxed
                alicuota = self.get_alicuota(cr, uid, txt_line)
                amount_total, amount_exempt = self.get_amount_line(
                    cr, uid, txt_line, amount_exempt)

                txt_string = (
                    txt_string + buyer + '\t' + period2.strip() + '\t'
                    + txt_line.invoice_id.date_invoice + '\t' + operation_type
                    + '\t' + document_type + '\t' + vendor + '\t'
                    + document_number + '\t' + control_number + '\t'
                    + str(round(amount_total, 2)) + '\t'
                    + str(round(txt_line.untaxed, 2)) + '\t'
                    + str(round(txt_line.amount_withheld, 2)) + '\t'
                    + document_affected + '\t' + voucher_number + '\t'
                    + str(round(amount_exempt, 2)) + '\t' + str(alicuota)
                    + '\t' + '0' + '\n')
        return txt_string

    def _write_attachment(self, cr, uid, ids, root, context=None):
        """ Encrypt txt, save it to the db and view it on the client as an
        attachment
        @param root: location to save document
        """
        context = context or {}
        fecha = time.strftime('%Y_%m_%d_%H%M%S')
        name = 'IVA_' + fecha + '.' + 'txt'
        self.pool.get('ir.attachment').create(cr, uid, {
            'name': name,
            'datas': base64.encodestring(root),
            'datas_fname': name,
            'res_model': 'txt.iva',
            'res_id': ids[0],
        }, context=context
        )
        cr.commit()
        self.message_post(cr, uid, ids[0], _('File Created'),
                          _("File TXT %s generated.") % name)

txt_iva()


class txt_iva_line(osv.osv):
    _name = "txt.iva.line"

    _columns = {
        'partner_id': fields.many2one(
            'res.partner', 'Buyer/Seller',
            help="Natural or juridical person that generates the Invoice, "
                 "Credit Note, Debit Note or C ertification (seller)"),
        'invoice_id': fields.many2one(
            'account.invoice', 'Bill/ND/NC',
            help="Date of invoice, credit note, debit note or certificate,"
                 " I mportación Statement"),
        'voucher_id': fields.many2one(
            'account.wh.iva', 'Tax Withholding',
            help="Withholding of Value Added Tax (VAT)"),
        'amount_withheld': fields.float(
            'Amount Withheld', help='amount to withhold'),
        'untaxed': fields.float(
            'Untaxed', help='Untaxed amount'),
        'txt_id': fields.many2one(
            'txt.iva', 'Generate-Document txt VAT', help='withholding lines'),
        'tax_wh_iva_id': fields.many2one(
            'account.wh.iva.line.tax', 'Tax Wh Iva Line'),
    }
    _rec_name = 'partner_id'

txt_iva_line()
