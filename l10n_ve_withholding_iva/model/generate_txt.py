# coding: utf-8
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

from openerp import models, fields, api, exceptions, _
import openerp.addons.decimal_precision as dp


class TxtIva(models.Model):
    _name = "txt.iva"
    _inherit = ['mail.thread']

    @api.model
    def _default_period_id(self):
        """ Return current period
        """
        fecha = time.strftime('%m/%Y')
        periods = self.env['account.period'].search([('code', '=', fecha)])
        return periods and periods[0].id or False

    @api.multi
    def _get_amount_total(self):
        """ Return total amount withheld of each selected bill
        """
        res = {}
        for txt in self:
            res[txt.id] = 0.0
            for txt_line in txt.txt_ids:
                if txt_line.invoice_id.type in ['out_refund', 'in_refund']:
                    res[txt.id] -= txt_line.amount_withheld
                else:
                    res[txt.id] += txt_line.amount_withheld
        return res

    @api.multi
    def _get_amount_total_base(self):
        """ Return total amount base of each selected bill
        """
        res = {}
        for txt in self:
            res[txt.id] = 0.0
            for txt_line in txt.txt_ids:
                if txt_line.invoice_id.type in ['out_refund', 'in_refund']:
                    res[txt.id] -= txt_line.untaxed
                else:
                    res[txt.id] += txt_line.untaxed
        return res

    name = fields.Char(
        string='Description', size=128, required=True, select=True,
        default=lambda self: 'Withholding Vat ' + time.strftime('%m/%Y'),
        help="Description about statement of withholding income")
    company_id = fields.Many2one(
        'res.company', string='Company', required=True, readonly=True,
        states={'draft': [('readonly', False)]}, help='Company',
        default=lambda self: self.env['res.company']._company_default_get())
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')
        ], string='Estado', select=True, readonly=True, default='draft',
        help="proof status")
    period_id = fields.Many2one(
        'account.period', string='Period', required=True, readonly=True,
        default=_default_period_id,
        states={'draft': [('readonly', False)]}, help='fiscal period')
    type = fields.Boolean(
        string='Retention Suppliers?', required=True,
        states={'draft': [('readonly', False)]}, default=True,
        help="Select the type of retention to make")
    date_start = fields.Date(
        string='Begin Date', required=True,
        states={'draft': [('readonly', False)]},
        help="Begin date of period")
    date_end = fields.Date(
        string='End date', required=True,
        states={'draft': [('readonly', False)]},
        help="End date of period")
    txt_ids = fields.One2many(
        'txt.iva.line', 'txt_id', readonly=True,
        states={'draft': [('readonly', False)]},
        help='Txt field lines of ar required by SENIAT for'
        ' VAT withholding')
    amount_total_ret = fields.Float(
        string='Withholding total amount', digits=dp.get_precision('Account'),
        compute=_get_amount_total, readonly=True,
        help="Monto Total Retenido")
    amount_total_base = fields.Float(
        string='Taxable total amount', digits=dp.get_precision('Account'),
        compute=_get_amount_total_base, readonly=True,
        help="Total de la Base Imponible")

    @api.multi
    def name_get(self):
        """ Return a list with id and name of the current register
        """
        res = [(r.id, r.name) for r in self]
        return res

    @api.multi
    def action_anular(self):
        """ Return document state to draft
        """
        self.write({'state': 'draft'})
        return True

    @api.multi
    def check_txt_ids(self, cr, uid, ids, context=None):
        """ Check that txt_iva has lines to process."""
        for awi in self:
            if not awi.txt_ids:
                raise exceptions.except_orm(
                    _("Missing Values !"),
                    _("Missing VAT TXT Lines!!!"))
        return True

    @api.multi
    def action_confirm(self):
        """ Transfers the document status to confirmed
        """
        self.check_txt_ids()
        self.write({'state': 'confirmed'})
        return True

    @api.multi
    def action_generate_lines_txt(self):
        """ Current lines are cleaned and rebuilt
        """
        rp_obj = self.env['res.partner']
        voucher_obj = self.env['account.wh.iva']
        txt_iva_obj = self.env['txt.iva.line']
        vouchers = []
        txt_brw = self.browse()[0]
        txt_ids = txt_iva_obj.search([('txt_id', '=', txt_brw.id)])
        if txt_ids:
            txt_iva_obj.unlink(txt_ids)

        if txt_brw.type:
            vouchers = voucher_obj.search([
                ('date_ret', '>=', txt_brw.date_start),
                ('date_ret', '<=', txt_brw.date_end),
                ('period_id', '=', txt_brw.period_id.id),
                ('state', '=', 'done'),
                ('type', 'in', ['in_invoice', 'in_refund'])])
        else:
            vouchers = voucher_obj.search([
                ('date_ret', '>=', txt_brw.date_start),
                ('date_ret', '<=', txt_brw.date_end),
                ('period_id', '=', txt_brw.period_id.id),
                ('state', '=', 'done'),
                ('type', 'in', ['out_invoice', 'out_refund'])])

        for voucher in vouchers:
            acc_part_id = rp_obj._find_accounting_partner(voucher.partner_id)
            for voucher_lines in voucher.wh_lines:
                if voucher_lines.invoice_id.state not in ['open', 'paid']:
                    continue
                for voucher_tax_line in voucher_lines.tax_line:
                    txt_iva_obj.create(
                        {'partner_id': acc_part_id.id,
                         'voucher_id': voucher.id,
                         'invoice_id': voucher_lines.invoice_id.id,
                         'txt_id': txt_brw.id,
                         'untaxed': voucher_tax_line.base,
                         'amount_withheld': voucher_tax_line.amount_ret,
                         'tax_wh_iva_id': voucher_tax_line.id,
                         })
        return True

    @api.model
    def get_buyer_vendor(self, txt, txt_line):
        """ Return the buyer and vendor of the sale or purchase invoice
        @param txt: current txt document
        @param txt_line: One line of the current txt document
        """
        rp_obj = self.env['res.partner']
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

    @api.model
    def get_document_affected(self, txt_line):
        """ Return the reference or number depending of the case
        @param txt_line: line of the current document
        """
        number = '0'
        if txt_line.invoice_id.type in ['in_invoice', 'in_refund'] and \
                txt_line.invoice_id.parent_id:
            number = txt_line.invoice_id.parent_id.supplier_invoice_number
        elif txt_line.invoice_id.parent_id:
            number = txt_line.invoice_id.parent_id.number
        return number

    @api.model
    def get_number(self, number, inv_type, max_size):
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

    @api.model
    def get_document_number(self, txt_line, inv_type):
        """ Return the number o reference of the invoice into txt line
        @param txt_line: One line of the current txt document
        @param inv_type: invoice type into txt line
        """
        number = 0
        if txt_line.invoice_id.type in ['in_invoice', 'in_refund']:
            if not txt_line.invoice_id.supplier_invoice_number:
                raise exceptions.except_orm(
                    _('Invalid action !'),
                    _("Unable to make txt file, because the bill has no"
                      " reference number free!"))
            else:
                number = self.get_number(
                    txt_line.invoice_id.supplier_invoice_number.strip(),
                    inv_type, 20)
        elif txt_line.invoice_id.number:
            number = self.get_number(
                txt_line.invoice_id.number.strip(), inv_type, 20)
        return number

    @api.model
    def get_type_document(self, txt_line):
        """ Return the document type
        @param txt_line: line of the current document
        """
        inv_type = '03'
        if txt_line.invoice_id.type in ['out_invoice', 'in_invoice']:
            inv_type = '01'
        elif txt_line.invoice_id.type in ['out_invoice', 'in_invoice'] and \
                txt_line.invoice_id.parent_id:
            inv_type = '02'
        return inv_type

    @api.model
    def get_max_aliquot(self, txt_line):
        """Get maximum aliquot per invoice"""
        res = []
        for tax_line in txt_line.invoice_id.tax_line:
            res.append(int(tax_line.tax_id.amount * 100))
        return max(res)

    @api.model
    def get_amount_line(self, txt_line, amount_exempt):
        """Method to compute total amount"""
        ali_max = self.get_max_aliquot(txt_line)
        exempt = 0

        if ali_max == int(txt_line.tax_wh_iva_id.tax_id.amount * 100):
            exempt = amount_exempt
        total = (txt_line.tax_wh_iva_id.base + txt_line.tax_wh_iva_id.amount +
                 exempt)
        return total, exempt

    @api.model
    def get_amount_exempt_document(self, txt_line):
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

    @api.model
    def get_alicuota(self, txt_line):
        """ Return aliquot of the withholding into line
        @param txt_line: One line of the current txt document
        """
        return int(txt_line.tax_wh_iva_id.tax_id.amount * 100)

    @api.multi
    def generate_txt(self):
        """ Return string with data of the current document
        """
        txt_string = ''
        rp_obj = self.env['res.partner']
        for txt in self:
            vat = rp_obj._find_accounting_partner(
                txt.company_id.partner_id).vat[2:]
            vat = vat
            for txt_line in txt.txt_ids:
                vendor, buyer = self.get_buyer_vendor(txt, txt_line)
                period = txt.period_id.name.split('/')
                period2 = period[0] + period[1]
                # TODO: use the start date of the period to get the period2
                # with the 'YYYYmm'
                operation_type = ('V' if txt_line.invoice_id.type in
                                  ['out_invoice', 'out_refund'] else 'C')
                document_type = self.get_type_document(txt_line)
                document_number = self.get_document_number(
                    txt_line, 'inv_number')
                control_number = self.get_number(
                    txt_line.invoice_id.nro_ctrl, 'inv_ctrl', 20)
                document_affected = self.get_document_affected(txt_line)
                voucher_number = self.get_number(
                    txt_line.voucher_id.number, 'vou_number', 14)
                amount_exempt, amount_untaxed = \
                    self.get_amount_exempt_document(txt_line)
                amount_untaxed = amount_untaxed
                alicuota = self.get_alicuota(txt_line)
                amount_total, amount_exempt = self.get_amount_line(
                    txt_line, amount_exempt)

                txt_string = (
                    txt_string + buyer + '\t' + period2.strip() + '\t' +
                    txt_line.invoice_id.date_invoice + '\t' + operation_type +
                    '\t' + document_type + '\t' + vendor + '\t' +
                    document_number + '\t' + control_number + '\t' +
                    str(round(amount_total, 2)) + '\t' +
                    str(round(txt_line.untaxed, 2)) + '\t' +
                    str(round(txt_line.amount_withheld, 2)) + '\t' +
                    document_affected + '\t' + voucher_number + '\t' +
                    str(round(amount_exempt, 2)) + '\t' + str(alicuota) +
                    '\t' + '0' + '\n')
        return txt_string

    @api.multi
    def _write_attachment(self, root, context=None):
        """ Encrypt txt, save it to the db and view it on the client as an
        attachment
        @param root: location to save document
        """
        fecha = time.strftime('%Y_%m_%d_%H%M%S')
        name = 'IVA_' + fecha + '.' + 'txt'
        self.env['ir.attachment'].create({
            'name': name,
            'datas': base64.encodestring(root),
            'datas_fname': name,
            'res_model': 'txt.iva',
            'res_id': self.ids[0],
        })
        msg = _("File TXT %s generated.") % (name)
        self.message_post(body=msg)

    @api.multi
    def action_done(self):
        """ Transfer the document status to done
        """
        root = self.generate_txt()
        self._write_attachment(root)
        self.write({'state': 'done'})

        return True


class TxtIvaLine(models.Model):
    _name = "txt.iva.line"

    partner_id = fields.Many2one(
        'res.partner', string='Buyer/Seller',
        help="Natural or juridical person that generates the Invoice, "
        "Credit Note, Debit Note or C ertification (seller)")
    invoice_id = fields.Many2one(
        'account.invoice', 'Bill/ND/NC',
        help="Date of invoice, credit note, debit note or certificate,"
        " Importación Statement")
    voucher_id = fields.Many2one(
        'account.wh.iva', string='Tax Withholding',
        help="Withholding of Value Added Tax (VAT)")
    amount_withheld = fields.Float(
        string='Amount Withheld', help='amount to withhold')
    untaxed = fields.Float(
        string='Untaxed', help='Untaxed amount')
    txt_id = fields.Many2one(
        'txt.iva', string='Generate-Document txt VAT',
        help='withholding lines')
    tax_wh_iva_id = fields.Many2one(
        'account.wh.iva.line.tax', string='Tax Wh Iva Line')

    _rec_name = 'partner_id'
