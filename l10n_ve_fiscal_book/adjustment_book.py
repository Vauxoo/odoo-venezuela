# coding: utf-8
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############################################################################
#    Credits:
#    Coded by: Humberto Arocha           <humberto@openerp.com.ve>
#              María Gabriela Quilarque  <gabrielaquilarque97@gmail.com>
#              Javier Duran              <javier@vauxoo.com>
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
from openerp.addons import decimal_precision as dp
from openerp.osv import fields, osv


class AdjustmentBook(osv.osv):

    def _get_amount_total(self, cr, uid, ids, name, args, context=None):
        res = {}
        for adj in self.browse(cr, uid, ids, context):
            res[adj.id] = {
                'amount_total': 0.0,
                'amount_untaxed_n_total': 0.0,
                'amount_with_vat_n_total': 0.0,
                'amount_untaxed_i_total': 0.0,
                'amount_with_vat_i_total': 0.0,
                'uncredit_fiscal_total': 0.0,
                'amount_with_vat_total': 0.0,
                'amount_base_total': 0.0,
                'amount_percent_total': 0.0,
            }
            for line in adj.adjustment_ids:
                res[adj.id]['amount_total'] += line.amount
                res[adj.id]['amount_untaxed_n_total'] += line.amount_untaxed_n
                res[adj.id]['amount_with_vat_n_total'] += \
                    line.amount_with_vat_n
                res[adj.id]['amount_untaxed_i_total'] += line.amount_untaxed_i
                res[adj.id]['amount_with_vat_i_total'] += \
                    line.amount_with_vat_i
                res[adj.id]['uncredit_fiscal_total'] += line.uncredit_fiscal
                res[adj.id]['amount_with_vat_total'] += line.amount_with_vat
            res[adj.id]['amount_base_total'] += (
                adj.vat_general_i + adj.vat_general_add_i + adj.vat_reduced_i +
                adj.vat_general_n + adj.vat_general_add_n + adj.vat_reduced_n +
                adj.adjustment + adj.no_grav + adj.sale_export)
            res[adj.id]['amount_percent_total'] += (
                adj.vat_general_icf + adj.vat_general_add_icf +
                adj.vat_reduced_icf + adj.vat_general_ncf +
                adj.vat_general_add_ncf + adj.vat_reduced_ncf +
                adj.adjustment_cf + adj.sale_export_cf)

        return res

    _name = 'adjustment.book'
    _columns = {
        'name': fields.char(
            'Description', size=256, required=True,
            help="Description of adjustment book"),
        'period_id': fields.many2one(
            'account.period', 'Period', required=True,
            help="Period of adjustment book"),
        'adjustment_ids': fields.one2many(
            'adjustment.book.line', 'adjustment_id', 'Adjustment Book Line'),
        'note': fields.text('Note', required=True),
        'type': fields.selection(
            [('sale', 'Sale'),
             ('purchase', 'Purchase'), ],
            'Type', select=True, required=True,
            help="Type of adjustment book: Sale or Purchase"),
        'amount_total': fields.function(
            _get_amount_total, multi='all', method=True,
            digits_compute=dp.get_precision('Account'),
            string='VAT Withholding Total Amount', readonly=True,
            help="Total Amount for adjustment book of invoice"),
        'amount_untaxed_n_total': fields.function(
            _get_amount_total, multi='all', method=True,
            digits_compute=dp.get_precision('Account'),
            string='Amount Untaxed National', readonly=True,
            help="Amount Total Untaxed for adjustment book of nacional"
                 " operations"),
        'amount_with_vat_n_total': fields.function(
            _get_amount_total, multi='all', method=True,
            digits_compute=dp.get_precision('Account'),
            string='Amount Withheld National', readonly=True,
            help="Amount Total Withheld for adjustment book of national"
                 " operations"),
        'amount_untaxed_i_total': fields.function(
            _get_amount_total, multi='all', method=True,
            digits_compute=dp.get_precision('Account'),
            string='Amount Untaxed International', readonly=True,
            help="Amount Total Untaxed for adjustment book of internacional"
                 " operations"),
        'amount_with_vat_i_total': fields.function(
            _get_amount_total, multi='all', method=True,
            digits_compute=dp.get_precision('Account'),
            string='Amount Withheld International', readonly=True,
            help="Amount Total Withheld for adjustment book of international"
                 " operations"),
        'uncredit_fiscal_total': fields.function(
            _get_amount_total, multi='all', method=True,
            digits_compute=dp.get_precision('Account'),
            string='Sin derecho a credito fiscal', readonly=True,
            help="Sin derecho a credito fiscal"),
        'amount_with_vat_total': fields.function(
            _get_amount_total, multi='all', method=True,
            digits_compute=dp.get_precision('Account'),
            string='VAT Withholding Total Amount', readonly=True,
            help="VAT Withholding total amount for adjustment book"),
        'no_grav': fields.float(
            'Compras/Ventas no Gravadas y/o SDCF',
            digits_compute=dp.get_precision('Account'),
            help="Compras/Ventas no gravadas y/o sin derecho a credito"
                 " fiscal/ Ventas Internas no grabadas"),
        'vat_general_i': fields.float(
            'Alicuota general', digits_compute=dp.get_precision('Account'),
            help="Importaciones gravadas por alicuota general"),
        'vat_general_add_i': fields.float(
            'Alicuota general + Alicuota adicional',
            digits_compute=dp.get_precision('Account'),
            help="Importaciones gravadas por alicuota general mas alicuota"
                 " adicional"),
        'vat_reduced_i': fields.float(
            'Alicuota Reducida', digits_compute=dp.get_precision('Account'),
            help="Importaciones gravadas por alicuota reducida"),
        'vat_general_n': fields.float(
            'Alicuota general', digits_compute=dp.get_precision('Account'),
            help="Compras gravadas por alicuota general/Ventas internas"
                 " gravadas por alicuota general"),
        'vat_general_add_n': fields.float(
            'Alicuota general + Alicuota adicional',
            digits_compute=dp.get_precision('Account'),
            help="Compras/Ventas internas gravadas por alicuota general mas"
                 " alicuota adicional"),
        'vat_reduced_n': fields.float(
            'Alicuota Reducida', digits_compute=dp.get_precision('Account'),
            help="Compras/Ventas Internas gravadas por alicuota reducida"),
        'adjustment': fields.float(
            'Ajustes', digits_compute=dp.get_precision('Account'),
            help="Ajustes a los creditos/debitos fiscales de los periodos"
                 " anteriores"),
        'vat_general_icf': fields.float(
            'Alicuota general', digits_compute=dp.get_precision('Account'),
            help="Importaciones gravadas por alicuota general"),
        'vat_general_add_icf': fields.float(
            'Alicuota general + Alicuota adicional',
            digits_compute=dp.get_precision('Account'),
            help="Importaciones gravadas por alicuota general mas alicuota"
                 " adicional"),
        'vat_reduced_icf': fields.float(
            'Alicuota Reducida', digits_compute=dp.get_precision('Account'),
            help="Importaciones gravadas por alicuota reducida"),
        'vat_general_ncf': fields.float(
            'Alicuota general', digits_compute=dp.get_precision('Account'),
            help="Compras gravadas por alicuota general/Ventas internas"
                 " gravadas por alicuota general"),
        'vat_general_add_ncf': fields.float(
            'Alicuota general + Alicuota adicional',
            digits_compute=dp.get_precision('Account'),
            help="Compras/Ventas internas gravadas por alicuota general mas"
                 " alicuota adicional"),
        'vat_reduced_ncf': fields.float(
            'Alicuota Reducida', digits_compute=dp.get_precision('Account'),
            help="Compras/Ventas Internas gravadas por alicuota reducida"),
        'adjustment_cf': fields.float(
            'Ajustes', digits_compute=dp.get_precision('Account'),
            help="Ajustes a los creditos/debitos fiscales de los periodos"
                 " anteriores"),
        'amount_base_total': fields.function(
            _get_amount_total, multi='all', method=True,
            digits_compute=dp.get_precision('Account'),
            string='Total Base Imponible', readonly=True,
            help="TOTAL COMPRAS DEL PERIODO/TOTAL VENTAS PARA EFECTOS DE"
                 " DETERMINACION"),
        'amount_percent_total': fields.function(
            _get_amount_total, multi='all', method=True,
            digits_compute=dp.get_precision('Account'),
            string='Total % Fiscal', readonly=True,
            help="TOTALCREDITOS FISCALES DEL PERIODO/TOTAL DEBITOS FISCALES"
                 " PARA EFECTOS DE DETERMINACION"),
        'sale_export': fields.float(
            'Ventas de Exportacion',
            digits_compute=dp.get_precision('Account'),
            help="Ventas de Exportacion"),
        'sale_export_cf': fields.float(
            'Ventas de Exportacion',
            digits_compute=dp.get_precision('Account'),
            help="Ventas de Exportacion"),
    }

    _sql_constraints = [
        ('period_id_type_uniq', 'unique (period_id,type)',
         'The period and type combination must be unique!')
    ]

    # def action_set_totals(self,cr,uid,ids, *args):
    # self.write(cr, uid, ids, {'vat_general_i':0.00,
    # 'vat_general_add_i':0.00,'vat_reduced_i':0.00,
    # 'vat_general_n':0.00,'vat_general_add_n':0.00,
    # 'vat_reduced_n':0.00,'sale_export':0.00,
    # })
    # total={'amount_untaxed_n':0.0,'amount_untaxed_n_scdf':0.0,
    # 'amount_untaxed_i':0.0,'amount_untaxed_i_scdf':0.0,
    # 'vat_general_ncf':0.0,'vat_general_ncf':0.0,
    # 'vat_add_ncf':0.0}
#
    # for adj in self.browse(cr, uid, ids):
    # if adj.type=='purchase':
    # self.write(cr, uid, ids, {'vat_general_i':adj.amount_untaxed_i_total,
    # 'vat_general_add_i':adj.amount_untaxed_i_total,
    # 'vat_reduced_i':adj.amount_untaxed_i_total,})
    # else:
    # self.write(cr, uid, ids, {'sale_export':adj.amount_untaxed_n_total,})
    # self.write(cr, uid, ids, {'vat_general_n':adj.amount_untaxed_n_total,
    # 'vat_general_add_n':adj.amount_untaxed_n_total,
    # 'vat_reduced_n':adj.amount_untaxed_n_total,
    # })
    # for line in adj.adjustment_ids:
    #
    # if 0==line.percent_with_vat_n:
    # total['amount_untaxed_n_scdf']+=line.amount_untaxed_n
    # total['amount_untaxed_i_scdf']+=line.amount_untaxed_i
    # else:
    # total['amount_untaxed_n']+=line.amount_untaxed_n
    # total['amount_untaxed_i']+=line.amount_untaxed_i
    # if 12 == line.percent_with_vat_n:
    # total['vat_general_ncf']+=12.0
    # if 8 == line.percent_with_vat_n:
    # total['vat_reduced_ncf']+=8.0
    # if 22 == line.percent_with_vat_n:
    # total['vat_additional_ncf']+=22.0
    # self.write(cr, uid, ids, {'vat_general_ncf':total['vat_general_ncf'],
    # 'vat_general_add_ncf':total['vat_general_ncf']+total['vat_add_ncf'],
    # 'vat_reduced_n':total['vat_reduced_n'],
    # })
    # return True


AdjustmentBook()


class AdjustmentBookLine(osv.osv):

    _name = 'adjustment.book.line'
    _columns = {
        'vat': fields.char(
            'Vat', size=10, required=True,
            help="Vat of partner for adjustment book"),
        'date_admin': fields.date(
            'Date Administrative', required=True,
            help="Date administrative for adjustment book"),
        'invoice_number': fields.char(
            'Invoice Number', size=256, required=True,
            help="Invoice number for adjustment book"),
        'partner': fields.char(
            'Partner', size=256, required=True,
            help="Partner for adjustment book"),
        'amount': fields.float(
            'Amount Document at VAT Withholding',
            digits_compute=dp.get_precision('Account'), required=True,
            help="Amount document for adjustment book"),
        'control_number': fields.char(
            'Invoice Control', size=256, required=True,
            help="Invoice control for adjustment book"),
        'type_doc': fields.selection(
            [('F', 'Invoice'), ('ND', 'Debit Note'), ('NC', 'Credit Note')],
            'Document Type', select=True, required=True,
            help="Date accounting for adjustment book"),
        'date_accounting': fields.date(
            'Date Accounting', required=True,
            help="Type of Document for adjustment book: -Invoice(F),-Debit"
                 " Note(dn),-Credit Note(cn)"),
        'doc_affected': fields.char(
            'Affected Document', size=256, required=True,
            help="Affected Document for adjustment book"),
        'uncredit_fiscal': fields.float(
            'Sin derecho a Credito Fiscal',
            digits_compute=dp.get_precision('Account'), required=True,
            help="Sin derechoa credito fiscal"),
        'amount_untaxed_n': fields.float(
            'Amount Untaxed', digits_compute=dp.get_precision('Account'),
            required=True, help="Amount untaxed for national operations"),
        'percent_with_vat_n': fields.float(
            'VAT Withholding (%)', digits_compute=dp.get_precision('Account'),
            required=True, help="VAT Percent(%) for national operations"),
        'amount_with_vat_n': fields.float(
            'VAT Withholding Amount',
            digits_compute=dp.get_precision('Account'), required=True,
            help="VAT Amount for national operations"),
        'amount_untaxed_i': fields.float(
            'Amount Untaxed', digits_compute=dp.get_precision('Account'),
            required=True, help="Amount untaxed for international operations"),
        'percent_with_vat_i': fields.float(
            'VAT Withholding (%)', digits_compute=dp.get_precision('Account'),
            required=True, help="VAT Percent(%) for international operations"),
        'amount_with_vat_i': fields.float(
            'VAT Withholding Amount',
            digits_compute=dp.get_precision('Account'), required=True,
            help="VAT Amount for international operations"),
        'amount_with_vat': fields.float(
            'VAT Withholding Total Amount',
            digits_compute=dp.get_precision('Account'), required=True,
            help="VAT withholding total amount"),
        'voucher': fields.char(
            'VAT Withholding Voucher', size=256, required=True,
            help="VAT withholding voucher"),
        'adjustment_id': fields.many2one('adjustment.book', 'Adjustment Book')
    }
    _rec_rame = 'partner'

AdjustmentBookLine()
