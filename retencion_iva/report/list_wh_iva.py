#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Humberto Arocha           <humberto@openerp.com.ve>
#              Maria Gabriela Quilarque  <gabriela@openerp.com.ve>
#              Javier Duran              <javier@nvauxoo.com>
#    Planified by: Nhomar Hernandez
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

class list_wh_iva(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(list_wh_iva, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'get_type_doc': self._get_type_document,
        })

    def _get_type_document(self,line):
        return self.pool.get('txt.iva').get_type_document(self.cr,self.uid,line)

    #~ def get_type_document(self,cr,uid,txt_line):



report_sxw.report_sxw(
    'report.list_report_wh_vat2',
    'txt.iva',
    'addons/retencion_iva/report/list_wh_iva_report.rml',
    parser=list_wh_iva, 
    header=False
)
