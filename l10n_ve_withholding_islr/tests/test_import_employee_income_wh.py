#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Written to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############################################################################
#    Credits:
#    Coded by: Humberto Arocha           <hbto@vauxoo.com>
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
#############################################################################

from openerp.tests.common import TransactionCase
import base64

FIELDNAMES = [
    'RifRetenido',
    'NumeroFactura',
    'NumeroControl',
    'FechaOperacion',
    'CodigoConcepto',
    'MontoOperacion',
    'PorcentajeRetencion']


class test_import_csv_employee_income_wh(TransactionCase):
    def setUp(self):
        super(test_import_csv_employee_income_wh, self).setUp()
        ap_obj = self.registry('account.period')
        self.period_id = ap_obj.find(self.cr, self.uid, dt=None,
                                     # exception=False, context=None
                                     )
        self.ixwd_obj = self.registry('islr.xml.wh.doc')
        self.eiw_obj = self.registry('employee.income.wh')
        self.rp_obj = self.registry('res.partner')
        self._create_rp()

    def _create_ixwd(self):
        cr, uid = self.cr, self.uid
        values = dict(
            name='Importing CSV File',
            period_id=self.period_id[0],
            user_id=uid,
        )
        self.ixwd_id = self.ixwd_obj.create(cr, uid, values)

    def _create_rp(self):
        cr, uid = self.cr, self.uid
        values = dict(
            name='Odoo Venezuela',
            vat='VEJ317520881',
        )
        self.rp_id = self.rp_obj.create(cr, uid, values)

    def _create_file(self, filetype='csv'):
        if filetype == 'csv':
            obj_file = ','.join(FIELDNAMES)
            obj_file += '\nJ317520881,0,N/A,13/06/2015,001,10000,1'
        elif filetype == 'xml':
            obj_file = '''<?xml version='1.0' encoding='ISO-8859-1'?>
            <RelacionRetencionesISLR
                Periodo="201506"
                RifAgente="V123456789">
            <DetalleRetencion>
                <RifRetenido>J317520881</RifRetenido>
                <NumeroFactura>0</NumeroFactura>
                <NumeroControl>NA</NumeroControl>
                <FechaOperacion>13/06/2015</FechaOperacion>
                <CodigoConcepto>004</CodigoConcepto>
                <MontoOperacion>1000.0</MontoOperacion>
                <PorcentajeRetencion>5.0</PorcentajeRetencion>
            </DetalleRetencion>
            </RelacionRetencionesISLR>
            '''  # TODO: This File needs generalization
        return base64.encodestring(obj_file)

    def _create_eiw(self, filetype='csv'):
        cr, uid = self.cr, self.uid
        values = dict(
            type=filetype,
            obj_file=self._create_file(filetype),
        )
        self.eiw_id = self.eiw_obj.create(cr, uid, values)

    def _import_csv_xml(self, filetype='csv'):
        self._create_ixwd()
        self._create_eiw(filetype)
        cr, uid = self.cr, self.uid
        ixwd_brw = self.ixwd_obj.browse(cr, uid, self.ixwd_id)
        self.assertEquals(len(ixwd_brw.xml_ids), 0,
                          'There should no record at all')
        # TODO: Code in wizard needs to be improved this context is cheating on
        # xml test as there is not strong test on data in XML
        context = {
            'islr_xml_wh_doc_id': self.ixwd_id,
            'company_vat': 'V123456789',
            'period_code': '201506',
        }
        self.eiw_obj.process_employee_income_wh(cr, uid, self.eiw_id,
                                                context=context)
        ixwd_brw = self.ixwd_obj.browse(cr, uid, self.ixwd_id)
        self.assertEquals(len(ixwd_brw.xml_ids), 1,
                          'There should be only one record')

    def test_import_csv(self):
        self._import_csv_xml('csv')

    def test_import_xml(self):
        self._import_csv_xml('xml')

# EOF
        # context = {
        #     'islr_xml_wh_doc_id': self.ixwd_id,
        #     'company_vat': 'V123456789',
        #     'period_code': '201506',
        # }
