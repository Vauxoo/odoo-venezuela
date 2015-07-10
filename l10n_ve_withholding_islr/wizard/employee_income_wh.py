# -*- encoding: utf-8 -*-
##############################################################################
#    Company: Tecvemar, c.a.
#    Author: Juan V. Márquez L.
#    Creation Date: 26/11/2012
#    Version: 0.0.0.0
#
#    Description: Gets a CSV file from data collector and import it to
#                 sale order
#
##############################################################################
# from datetime import datetime
import base64
import functools
import logging

import libxml2
from openerp.osv import fields, osv
from openerp.tools.translate import _

from StringIO import StringIO

# import pooler
# import decimal_precision as dp
import time
# import netsvc
import csv

FIELDNAMES = [
    'RifRetenido',
    'NumeroFactura',
    'NumeroControl',
    'FechaOperacion',
    'CodigoConcepto',
    'MontoOperacion',
    'PorcentajeRetencion']

# ---------------------------------------------------------- employee_income_wh


class employee_income_wh(osv.osv_memory):

    _name = 'employee.income.wh'

    _description = ''

    logger = logging.getLogger('employee.income.wh')

    # -------------------------------------------------------------------------

    # ------------------------------------------------------- _internal methods

    def _parse_csv_employee_income_wh(self, cr, uid, csv_file, context=None):
        '''
        Method to parse CSV File
        '''
        stream = StringIO(csv_file)
        csv_file = csv.DictReader(stream)

        if set(csv_file.fieldnames) < set(FIELDNAMES):
            msg = _('Missing Fields in CSV File.\n'
                    'File shall bear following fields:\n')
            for fn in FIELDNAMES:
                msg += '{field},\n'.format(field=fn)
            raise osv.except_osv(_('Error!'), msg)
        res = []
        for item in csv_file:
            res.append(item)
        return res

    def _parse_xml_employee_income_wh(self, cr, uid, xml_file, context=None):
        res = []
        try:
            context = context or {}
            xmldoc = libxml2.parseDoc(xml_file)
            cntx = xmldoc.xpathNewContext()
            # TODO: Code in wizard needs to be improved this context is
            # cheating on xml test as there is not strong test on data in XML
            xpath = '/RelacionRetencionesISLR[@RifAgente="%s" ' \
                'and @Periodo="%s"]' \
                % (context.get('company_vat'), context.get('period_code'))
            varlist = cntx.xpathEval(xpath)
            if not varlist:
                return res
            xpath = '/RelacionRetencionesISLR/DetalleRetencion'
            varlist = cntx.xpathEval(xpath)
            for item in varlist:
                values = {}
                for k in FIELDNAMES:
                    attr = item.xpathEval(k) or []
                    values.update({k: attr and attr[0].get_content() or False})
                res.append(values)
        except libxml2.parserError:
            log_msg = 'ERROR: the file is not a XML'
            self.logger.warning(log_msg)
        return res

    def _clear_xml_employee_income_wh(self, cr, uid, context=None):
        context = context or {}
        if context.get('islr_xml_wh_doc_id'):
            obj_ixwl = self.pool.get('islr.xml.wh.line')
            unlink_ids = obj_ixwl.search(
                cr, uid,
                [('islr_xml_wh_doc', '=', context['islr_xml_wh_doc_id']),
                 ('type', '=', 'employee')])
            if unlink_ids:
                obj_ixwl.unlink(cr, uid, unlink_ids, context=context)
        return True

    def _get_xml_employee_income_wh(self, cr, uid, xml_list, context=None):
        """"
                                                 \\\
                                                 ///
                                                 \\\
                                                 ///
                                                 \\\
                                                 ///
        ----------------------------------------#####
        ----------------------------------------#####

        Pro python Marty Alchin, Pag  75, Memoization
        """

        def memoize(func):
            cache = {}

            @functools.wraps(func)
            def wrapper(*args):
                if args in cache:
                    return cache[args]
                result = func(*args)
                cache[args] = result
                return result
            return wrapper

        @memoize
        def find_data(obj, field, operator, value):
            ids = obj.search(cr, uid, [(field, operator, value)])
            if len(ids) == 1:
                return ids[0]
            return False

        context = context or {}
        field_map = {'RifRetenido': 'partner_vat',
                     'NumeroFactura': 'invoice_number',
                     'NumeroControl': 'control_number',
                     'CodigoConcepto': 'concept_code',
                     'FechaOperacion': 'date_ret',
                     'MontoOperacion': 'base',
                     'PorcentajeRetencion': 'porcent_rete',
                     }
        obj_pnr = self.pool.get('res.partner')
        obj_irt = self.pool.get('islr.rates')
        valid = []
        invalid = []
        for item in xml_list:
            data = {}
            for key, data_key in field_map.items():
                data[data_key] = item[key]
            pnr_id = find_data(
                obj_pnr, 'vat', '=', 'VE%s' % data.get('partner_vat'))
            if pnr_id:
                data.update({'partner_id': pnr_id})
            irt_id = find_data(
                obj_irt, 'code', '=', data.get('concept_code'))
            if irt_id:
                irt_brw = obj_irt.browse(cr, uid, irt_id, context=context)
                data.update({'concept_id': irt_brw.concept_id.id,
                             'rate_id': irt_id})

            date_ret = time.strptime(data['date_ret'], '%d/%m/%Y')
            date_ret = time.strftime('%Y-%m-%d', date_ret)

            data.update({
                'wh': float(data['base']) * float(data['porcent_rete']) / 100,
                'period_id': context.get('default_period_id'),
                'date_ret': date_ret,
                'islr_xml_wh_doc': context.get('islr_xml_wh_doc_id'),
                'type': 'employee',
            })
            if pnr_id and irt_id:
                valid.append(data)
            else:
                invalid.append(data)

        return valid, invalid

    # --------------------------------------------------------- function fields

    _columns = {
        'name': fields.char('File name', size=128, readonly=True),
        'type': fields.selection(
            [('csv', 'CSV File'), ('xml', 'XML File')], 'File Type',
            required=True),
        'obj_file': fields.binary('XML file', required=True, filters='*.xml',
                                  help=("XML file name with employee income "
                                        "withholding data")),
    }

    _defaults = {
        'type': lambda *a: 'csv',
    }

    _sql_constraints = [
    ]

    # -------------------------------------------------------------------------

    # ---------------------------------------------------------- public methods

    # -------------------------------------------------------- buttons (object)

    def process_employee_income_wh(self, cr, uid, ids, context=None):
        ids = isinstance(ids, (int, long)) and [ids] or ids
        eiw_brw = self.browse(cr, uid, ids, context={})[0]
        eiw_file = eiw_brw.obj_file
        invalid = []
        xml_file = base64.decodestring(eiw_file)
        if eiw_brw.type == 'xml':
            try:
                unicode(xml_file, 'utf8')
            except UnicodeDecodeError:
                # If we can not convert to UTF-8 maybe the file
                # is codified in ISO-8859-15: We convert it.
                xml_file = unicode(xml_file, 'iso-8859-15').encode('utf-8')
            values = self._parse_xml_employee_income_wh(
                cr, uid, xml_file, context=context)
        elif eiw_brw.type == 'csv':
            values = self._parse_csv_employee_income_wh(
                cr, uid, xml_file, context=context)
        obj_ixwl = self.pool.get('islr.xml.wh.line')
        if values:
            self._clear_xml_employee_income_wh(cr, uid, context=context)
            valid, invalid = self._get_xml_employee_income_wh(
                cr, uid, values, context=context)
            for data in valid:
                obj_ixwl.create(cr, uid, data, context=context)
        if not values or invalid:
            msg = _('Not imported data:\n') if invalid else \
                _('Empty or Invalid XML File '
                  '(you should check both company vat and period too)')
            for item in invalid:
                msg += 'RifRetenido: %s\n' % item['partner_vat']
            raise osv.except_osv(_('Error!'), msg)

        return {'type': 'ir.actions.act_window_close'}

    # ------------------------------------------------------------ on_change...

    # ----------------------------------------------------- create write unlink

    # ---------------------------------------------------------------- Workflow

employee_income_wh()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
