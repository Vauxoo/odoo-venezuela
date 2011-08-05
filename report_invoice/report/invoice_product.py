#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Humberto Arocha           <humberto@openerp.com.ve>
#              María Gabriela Quilarque  <gabrielaquilarque97@gmail.com>
#              Nhomar Hernandez          <nhomar@openerp.com.ve>
#    Planified by: Humberto Arocha
#    Finance by: Helados Gilda, C.A. http://heladosgilda.com.ve
#    Audited by: Humberto Arocha humberto@openerp.com.ve
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

import time
import pooler
from report import report_sxw
from tools.translate import _

class product_invoice(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(product_invoice, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_start_date':self._get_start_date,
            'get_end_date':self._get_end_date,
            'get_header_data':self._get_header_data,
            'get_lines':self._get_lines,
            'get_filter': self._get_filter,
            'get_name': self._get_name,
            'get_header_title':self._get_header_title,
            'get_big_header':self._get_big_header            
                    })

    def _get_start_date(self, data):
        if data.get('form', False) and data['form'].get('date_from', False):
            return data['form']['date_from']
        return ''

    def _get_end_date(self, data):
        if data.get('form', False) and data['form'].get('date_to', False):
            return data['form']['date_to']
        return ''

    def _get_header_data(self, data):
        header_name = ''
        if data['form']['filter'] == 'filter_product':
            if data.get('form', False) and data['form'].get('partner_id', False):
                partner_brw = pooler.get_pool(self.cr.dbname).get('res.partner').browse(self.cr, self.uid, data['form']['partner_id'])
                header_name = partner_brw.name
        if data['form']['filter'] == 'filter_partner':
            if data.get('form', False) and data['form'].get('product_id', False):
                product_brw = pooler.get_pool(self.cr.dbname).get('product.product').browse(self.cr, self.uid, data['form']['product_id'])
                header_name = '[%s]%s'%(product_brw.default_code,product_brw.name)
        return header_name

    def _get_lines(self, data):
        if data['form']['filter'] == 'filter_product':
            filter_str = 'product'
        if data['form']['filter'] == 'filter_partner':
            filter_str = 'partner'
            
        model ='report.invoice.%s' % (filter_str,)
        ids = pooler.get_pool(self.cr.dbname).get(model).search(self.cr, self.uid, [])
        return pooler.get_pool(self.cr.dbname).get(model).browse(self.cr, self.uid, ids)

    def _get_filter(self, data):
        if data.get('form', False) and data['form'].get('filter', False):
            if data['form']['filter'] == 'filter_product':
                return _('PRODUCTS')
            elif data['form']['filter'] == 'filter_partner':
                return _('PARTNER')
        return _('NO FILTER')

    def _get_name(self, data, line):
        line_name = ''
        if data['form']['filter'] == 'filter_product':
            line_name = '[%s]%s'%(line.product_id.default_code,line.product_id.name)
        if data['form']['filter'] == 'filter_partner':
            line_name = line.partner_id.name
                
        return line_name

    def _get_header_title(self, data):
        if data.get('form', False) and data['form'].get('filter', False):
            if data['form']['filter'] == 'filter_product':
                return _('CUSTOMER/SUPPLIER')
            elif data['form']['filter'] == 'filter_partner':
                return _('PRODUCT')
        return _('NO FILTER')

    def _get_big_header(self, data):
        if data.get('form', False) and data['form'].get('type', False):
            if data['form']['type'] in ('out_invoice', 'out_both'):
                return _('SALES')
            if data['form']['type'] in ('in_invoice', 'in_both'):
                return _('PURCHASES')
            if data['form']['type'] == 'out_refund':
                return _('SALES REFUND')          
            elif data['form']['type'] == 'in_refund':
                return _('PURCHASES REFUND')
        return _('NO TYPE')    
    
report_sxw.report_sxw(
    'report.inv.prod.wiz.report',
    'report.invoice.partner',
    'addons/report_invoice/report/invoice_product.rml',
    parser=product_invoice,
    header = 'internal'
)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
