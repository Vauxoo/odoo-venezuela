#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Maria Gabriela Quilarque  <gabrielaquilarque97@gmail.com>
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
from report_sxw_ext import report_sxw_ext
from osv import osv

class delivery_note_report(report_sxw_ext.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(delivery_note_report, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_partner_addr': self._get_partner_addr,
        })

    #metodo que retorna el numero de telefono celular, local y fax con espacios.
    def _get_partner_addr(self, phone=None):
        if not phone:
            return []
        phone_end= ""
        list_phone=[]
        list_phone = phone.split(',')
        if len(list_phone)>1:
            for tel in list_phone:
                phone_end = phone_end + ' ' + tel
        else:
            cont = 0
            list_phone= phone.split('/')
            if len(list_phone)==1:
                return list_phone[0]
            else:
                for tel in list_phone:
                    if cont == 0:
                        phone_end = tel
                    else:
                        phone_end = tel + ' /' + phone_end
                    cont = cont + 1
        return phone_end

report_sxw_ext.report_sxw(
    'report.delivery.note.report',
    'delivery.note',
    'addons/delivery_note/report/delivery_note_report.rml',
    parser=delivery_note_report,
    header = False 
)
