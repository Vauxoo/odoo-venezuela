# coding: utf-8
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############################################################################
#    Credits:
#    Coded by: Humberto Arocha           <humberto@openerp.com.ve>
#              Maria Gabriela Quilarque  <gabrielaquilarque97@gmail.com>
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
import base64
import time
from xml.etree.ElementTree import Element, SubElement, tostring

from openerp import api
from openerp.addons import decimal_precision as dp
from openerp.osv import fields, osv
from openerp.tools.translate import _

ISLR_XML_WH_LINE_TYPES = [('invoice', 'Invoice'), ('employee', 'Employee')]


class IslrXmlWhDoc(osv.osv):
    _name = "islr.xml.wh.doc"
    _description = 'Generate XML'

    def _get_amount_total(self, cr, uid, ids, name, args, context=None):
        """ Return withhold total amount
        """
        res = {}
        for xml in self.browse(cr, uid, ids, context):
            res[xml.id] = 0.0
            for line in xml.xml_ids:
                res[xml.id] += line.wh
        return res

    def _get_amount_total_base(self, cr, uid, ids, name, args, context=None):
        """ Return base total amount
        """
        res = {}
        for xml in self.browse(cr, uid, ids, context):
            res[xml.id] = 0.0
            for line in xml.xml_ids:
                res[xml.id] += line.base
        return res

    def _get_company(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid)
        return user.company_id.id

    _columns = {
        'name': fields.char(
            string='Description', size=128, required=True, select=True,
            default='Income Withholding ' + time.strftime('%m/%Y'),
            help="Description about statement of income withholding"),
        'company_id': fields.many2one(
            'res.company', string='Company', required=True,
            default=lambda s: s._get_company(),
            help="Company"),
        'state': fields.selection([
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'),
            ('done', 'Done'),
            ('cancel', 'Cancelled')
            ], string='State', readonly=True, default='draft',
            help="Voucher state"),
        'period_id': fields.many2one(
            'account.period', string='Period', required=True,
            default=lambda s: s.period_return(),
            help="Period when the accounts entries were done"),
        'amount_total_ret': fields.function(
            _get_amount_total, method=True, digits=(16, 2), readonly=True,
            string='Income Withholding Amount Total',
            help="Amount Total of withholding"),
        'amount_total_base': fields.function(
            _get_amount_total_base, method=True, digits=(16, 2), readonly=True,
            string='Without Tax Amount Total', help="Total without taxes"),
        'xml_ids': fields.one2many(
            'islr.xml.wh.line', 'islr_xml_wh_doc', 'XML Document Lines',
            readonly=True, states={'draft': [('readonly', False)]},
            help='XML withhold invoice line id'),
        'invoice_xml_ids': fields.one2many(
            'islr.xml.wh.line', 'islr_xml_wh_doc', 'XML Document Lines',
            readonly=True, states={'draft': [('readonly', False)]},
            help='XML withhold invoice line id',
            domain=[('type', '=', 'invoice')]),
        'employee_xml_ids': fields.one2many(
            'islr.xml.wh.line', 'islr_xml_wh_doc', 'XML Document Lines',
            readonly=True, states={'draft': [('readonly', False)]},
            help='XML withhold employee line id',
            domain=[('type', '=', 'employee')]),
        'user_id': fields.many2one(
            'res.users', string='User', readonly=True,
            states={'draft': [('readonly', False)]},
            default=lambda s: s._uid,
            help='User Creating Document'),
    }

    @api.multi
    def copy(self, default=None):
        """ Initialized id by duplicating
        """
        if default is None:
            default = {}
        default = default.copy()
        default.update({
            'xml_ids': [],
            'invoice_xml_ids': [],
            'employee_xml_ids': [],
        })

        return super(IslrXmlWhDoc, self).copy(default)

    def period_return(self, cr, uid, context=None):
        """ Return current period
        """
        period_obj = self.pool.get('account.period')
        fecha = time.strftime('%m/%Y')
        period_id = period_obj.search(cr, uid, [('code', '=', fecha)])
        if period_id:
            return period_id[0]
        else:
            return False

    def search_period(self, cr, uid, ids, period_id, context=None):
        """ Return islr lines associated with the period_id
        @param period_id: period associated with returned islr lines
        """
        if context is None:
            context = {}
        res = {'value': {}}
        if period_id:
            islr_line = self.pool.get('islr.xml.wh.line')
            islr_line_ids = islr_line.search(
                cr, uid, [('period_id', '=', period_id)], context=context)
            if islr_line_ids:
                res['value'].update({'xml_ids': islr_line_ids})
                return res

    def name_get(self, cr, uid, ids, context=None):
        """ Return id and name of all records
        """
        context = context or {}
        if not len(ids):
            return []

        res = [(r['id'], r['name']) for r in self.read(
            cr, uid, ids, ['name'], context=context)]
        return res

    def action_anular1(self, cr, uid, ids, context=None):
        """ Return the document to draft status
        """
        context = context or {}
        return self.write(cr, uid, ids, {'state': 'draft'}, context=context)

    def action_confirm1(self, cr, uid, ids, context=None):
        """ Passes the document to state confirmed
        """
        # to set date_ret if don't exists
        context = context or {}
        obj_ixwl = self.pool.get('islr.xml.wh.line')
        for item in self.browse(cr, uid, ids, context={}):
            for ixwl in item.xml_ids:
                if not ixwl.date_ret and ixwl.islr_wh_doc_inv_id:
                    obj_ixwl.write(
                        cr, uid, [ixwl.id],
                        {'date_ret':
                            ixwl.islr_wh_doc_inv_id.islr_wh_doc_id.date_ret},
                        context=context)
        return self.write(cr, uid, ids, {'state': 'confirmed'})

    def action_done1(self, cr, uid, ids, context=None):
        """ Passes the document to state done
        """
        context = context or {}
        root = self._xml(cr, uid, ids)
        self._write_attachment(cr, uid, ids, root, context)
        self.write(cr, uid, ids, {'state': 'done'})
        return True

    def _write_attachment(self, cr, uid, ids, root, context):
        """ Codify the xml, to save it in the database and be able to
        see it in the client as an attachment
        @param root: data of the document in xml
        """
        fecha = time.strftime('%Y_%m_%d_%H%M%S')
        name = 'ISLR_' + fecha + '.' + 'xml'
        self.pool.get('ir.attachment').create(cr, uid, {
            'name': name,
            'datas': base64.encodestring(root),
            'datas_fname': name,
            'res_model': 'islr.xml.wh.doc',
            'res_id': ids[0],
        }, context=context
        )
        cr.commit()
        self.log(cr, uid, ids[0], _("File XML %s generated.") % name)

    def indent(self, elem, level=0):
        """ Return indented text
        @param level: number of spaces for indentation
        @param elem: text to indentig
        """
        i = "\n" + level * "  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for elem in elem:
                self.indent(elem, level + 1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i

    def import_xml_employee(self, cr, uid, ids, context=None):
        ids = isinstance(ids, (int, long)) and [ids] or ids
        xml_brw = self.browse(cr, uid, ids, context={})[0]
        period = time.strptime(xml_brw.period_id.date_stop, '%Y-%m-%d')
        return {'name': _('Import XML employee'),
                'type': 'ir.actions.act_window',
                'res_model': 'employee.income.wh',
                'view_type': 'form',
                'view_id': False,
                'view_mode': 'form',
                'nodestroy': True,
                'target': 'new',
                'domain': "",
                'context': {
                    'default_period_id': xml_brw.period_id.id,
                    'islr_xml_wh_doc_id': xml_brw.id,
                    'period_code': "%0004d%02d" % (
                        period.tm_year, period.tm_mon),
                    'company_vat': xml_brw.company_id.partner_id.vat[2:]}}

    def _xml(self, cr, uid, ids):
        """ Transform this document to XML format
        """
        rp_obj = self.pool.get('res.partner')
        inv_obj = self.pool.get('account.invoice')
        root = ''
        for ixwd_id in ids:
            wh_brw = self.browse(cr, uid, ixwd_id)

            period = time.strptime(wh_brw.period_id.date_stop, '%Y-%m-%d')
            period2 = "%0004d%02d" % (period.tm_year, period.tm_mon)

            sql = '''
            SELECT partner_vat,control_number,porcent_rete,
                concept_code,invoice_number,
                SUM(COALESCE(base,0)) as base,account_invoice_id,date_ret
            FROM islr_xml_wh_line
            WHERE period_id= %s and id in (%s)
            GROUP BY partner_vat,control_number,porcent_rete,concept_code,
                invoice_number,account_invoice_id,date_ret''' % (
                wh_brw.period_id.id, ', '.join([
                    str(i.id)
                    for i in wh_brw.xml_ids]))
            cr.execute(sql)
            xml_lines = cr.fetchall()

            root = Element("RelacionRetencionesISLR")
            root.attrib['RifAgente'] = rp_obj._find_accounting_partner(
                wh_brw.company_id.partner_id).vat[2:]
            root.attrib['Periodo'] = period2
            for line in xml_lines:
                partner_vat, control_number, porcent_rete, concept_code, \
                    invoice_number, base, inv_id, date_ret = line
                detalle = SubElement(root, "DetalleRetencion")
                SubElement(detalle, "RifRetenido").text = partner_vat
                SubElement(detalle, "NumeroFactura").text = ''.join(
                    i for i in invoice_number if i.isdigit())[-10:] or '0'
                SubElement(detalle, "NumeroControl").text = ''.join(
                    i for i in control_number if i.isdigit())[-8:] or 'NA'
                if date_ret:
                    date_ret = time.strptime(date_ret, '%Y-%m-%d')
                    SubElement(detalle, "FechaOperacion").text = time.strftime(
                        '%d/%m/%Y', date_ret)
                # This peace of code will be left for backward compatibility
                # TODO: Delete on V8 onwards
                elif inv_id and inv_obj.browse(cr, uid, inv_id).islr_wh_doc_id:
                    date_ret = time.strptime(inv_obj.browse(
                        cr, uid, inv_id).islr_wh_doc_id.date_ret, '%Y-%m-%d')
                    SubElement(detalle, "FechaOperacion").text = time.strftime(
                        '%d/%m/%Y', date_ret)
                SubElement(detalle, "CodigoConcepto").text = concept_code
                SubElement(detalle, "MontoOperacion").text = str(base)
                SubElement(detalle, "PorcentajeRetencion").text = str(
                    porcent_rete)
        self.indent(root)
        return tostring(root, encoding="ISO-8859-1")

IslrXmlWhDoc()


class IslrXmlWhLine(osv.osv):
    _name = "islr.xml.wh.line"
    _description = 'Generate XML Lines'

    _columns = {
        'concept_id': fields.many2one(
            'islr.wh.concept', 'Withholding Concept',
            help="Withholding concept associated with this rate",
            required=True, ondelete='cascade'),
        'period_id': fields.many2one(
            'account.period', 'Period', required=False,
            help="Period when the journal entries were done"),
        'partner_vat': fields.char(
            'VAT', size=10, required=True, help="Partner VAT"),
        'invoice_number': fields.char(
            'Invoice Number', size=10, required=True,
            default='0',
            help="Number of invoice"),
        'control_number': fields.char(
            'Control Number', size=8, required=True,
            default='NA',
            help="Reference"),
        'concept_code': fields.char(
            'Concept Code', size=10, required=True, help="Concept code"),
        'base': fields.float(
            'Base Amount', required=True,
            help="Amount where a withholding is going to be computed from",
            digits_compute=dp.get_precision('Withhold ISLR')),
        'raw_base_ut': fields.float(
            'UT Amount', digits_compute=dp.get_precision('Withhold ISLR'),
            help="UT Amount"),
        'raw_tax_ut': fields.float(
            'UT Withheld Tax',
            digits_compute=dp.get_precision('Withhold ISLR'),
            help="UT Withheld Tax"),
        'porcent_rete': fields.float(
            'Withholding Rate', required=True, help="Withholding Rate",
            digits_compute=dp.get_precision('Withhold ISLR')),
        'wh': fields.float(
            'Withheld Amount', required=True,
            help="Withheld amount to partner",
            digits_compute=dp.get_precision('Withhold ISLR')),
        'rate_id': fields.many2one(
            'islr.rates', 'Person Type',
            domain="[('concept_id','=',concept_id)]", required=False,
            help="Person type"),
        'islr_wh_doc_line_id': fields.many2one(
            'islr.wh.doc.line', 'Income Withholding Document',
            ondelete='cascade', help="Income Withholding Document"),
        'account_invoice_line_id': fields.many2one(
            'account.invoice.line', 'Invoice Line',
            help="Invoice line to Withhold"),
        'account_invoice_id': fields.many2one(
            'account.invoice', 'Invoice', help="Invoice to Withhold"),
        'islr_xml_wh_doc': fields.many2one(
            'islr.xml.wh.doc', 'ISLR XML Document', help="Income tax XML Doc"),
        'partner_id': fields.many2one(
            'res.partner', 'Partner', required=True,
            help="Partner object of withholding"),
        'sustract': fields.float(
            'Subtrahend', help="Subtrahend",
            digits_compute=dp.get_precision('Withhold ISLR')),
        'islr_wh_doc_inv_id': fields.many2one(
            'islr.wh.doc.invoices', 'Withheld Invoice',
            help="Withheld Invoices"),
        'date_ret': fields.date('Operation Date'),
        'type': fields.selection(
            ISLR_XML_WH_LINE_TYPES,
            string='Type', required=True, readonly=False,
            default='invoice'),
    }
    _rec_name = 'partner_id'

    def onchange_partner_vat(self, cr, uid, ids, partner_id, context=None):
        """ Changing the partner, the partner_vat field is updated.
        """
        context = context or {}
        rp_obj = self.pool.get('res.partner')
        acc_part_brw = rp_obj._find_accounting_partner(rp_obj.browse(
            cr, uid, partner_id))
        return {'value': {'partner_vat': acc_part_brw.vat[2:]}}

    def onchange_code_perc(self, cr, uid, ids, rate_id, context=None):
        """ Changing the rate of the islr, the porcent_rete and concept_code fields
        is updated.
        """
        context = context or {}
        rate_brw = self.pool.get('islr.rates').browse(cr, uid, rate_id)
        return {'value': {'porcent_rete': rate_brw.wh_perc,
                          'concept_code': rate_brw.code}}


IslrXmlWhLine()


class AccountInvoiceLine(osv.osv):
    _inherit = "account.invoice.line"

    _columns = {
        'wh_xml_id': fields.many2one(
            'islr.xml.wh.line', string='XML Id', default=0,
            help="XML withhold line id"),
    }

AccountInvoiceLine()
