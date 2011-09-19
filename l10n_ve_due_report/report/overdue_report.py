# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Vauxoo C.A. (http://openerp.com.ve/) All Rights Reserved.
#                    Javier Duran <nhomar@vauxoo.com>
# 
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

import time
from report import report_sxw
from osv import osv
import pooler
import datetime
import locale

class overdue_report_report(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(overdue_report_report, self).__init__(cr, uid, name, context)    
        self.localcontext.update({
        'lines_get': self._lines_get,
        'get_company': self._get_company,
        'get_invoices': self._get_invoices,
        'get_balance': self._check_balance,
        'locale': locale,
        })
###Todos los partners segun Criterio
    def _lines_get(self, data):
        partner_obj = pooler.get_pool(self.cr.dbname).get('res.partner')
        partner_ids = partner_obj.search(self.cr, self.uid, [("customer","=",True)], order='name')
        partner_data = partner_obj.browse(self.cr, self.uid, partner_ids)
        #print "Partners................-----",partner_data
        return partner_data
###Nombre de la Company
    def _get_company(self, data):
        user_obj = pooler.get_pool(self.cr.dbname).get('res.users')
        user_ids = user_obj.search(self.cr, self.uid, [('id','=',self.uid)])
        user_elem = user_obj.browse(self.cr, self.uid, user_ids)[0]
        return user_elem
###Obteniendo facturas
    def _get_invoices(self, data, id_partner, days_min, days_mayor):
        invoice_obj = pooler.get_pool(self.cr.dbname).get('account.invoice')
        inv_ids = invoice_obj.search(self.cr, self.uid, [('partner_id','=',id_partner),('type','in',['out_invoice','out_refund']),('state','<>','draft'),('state','<>','cancel'),('state','<>','proforma2'),('state','<>','proforma')])
        inv_elemts = invoice_obj.browse(self.cr, self.uid, inv_ids)
        total = 0.00
        if inv_elemts:
            total = self.calc_total(data['date_start'],inv_elemts,days_min, days_mayor)
        else:
            total = 0.00
        return total
###############################################################Calculando totales en fecha
    def calc_total(self, date_control, list_invoices, days_minor, days_mayor):
        """
        @days_minor: Cantidad de Dias para verificar menor del rango.
        @days_mayor: Cantidad de Dias para verificar menor del rango.
        @list_invoices: Listado de Facturas.
        @date_control: Fecha de Control.
        """
        if list_invoices:
            total = 0
            for invoices in list_invoices:
                if invoices.date_invoice:
                    if self.check_date(days_minor, days_mayor, date_control, invoices.date_invoice):                
                        if invoices.type == "out_refund":
                            print "INVOICE TYPE OUT_REFUND",invoices.partner_id.name,invoices.type
                            total = total - invoices.residual
                        else:
                            total = total + invoices.residual
                else:
                    print "invoice description pupu -------- ",invoices.description,"id____",invoices.id
                    total = -1.00
        return total
################################################################comparando fechas
    def check_date(self, delta_minor,delta_max,fecha,date_inv):
        """
        @delta_minor: Cantidad de Dias para verificar menor del rango.
        @delta_max: Cantidad de Dias para verificar menor del rango.
        @fecha: Fecha de Control contra la que se comparará todo.
        @date_inv: fecha de lo que se va a comparar.
        """
        date_tocheck_minor = datetime.datetime(*time.strptime(fecha,'%Y-%m-%d')[0:5]) - datetime.timedelta(days=delta_max)
        date_tocheck_max = datetime.datetime(*time.strptime(fecha,'%Y-%m-%d')[0:5]) - datetime.timedelta(days=delta_minor)
        #print "____________fechas_fact_______________",date_inv
        date_invo = datetime.datetime(*time.strptime(date_inv,'%Y-%m-%d')[0:5])
        if date_tocheck_minor <= date_invo <= date_tocheck_max:
            return True
        else:
            return False
    def _check_balance(self, account_id):
        account_obj = pooler.get_pool(self.cr.dbname).get('account.account')
        account_ids = account_obj.search(self.cr, self.uid, [('id','=',account_id)])
#        account_elem = account_obj.browse(self.cr, self.uid, account_ids)[0]
        balance = account_obj.browse(self.cr, self.uid, account_ids)[0].balance
        return balance
    
report_sxw.report_sxw(
    'report.reports.overdue_report',
    'res.partner',
    'addons/l10n_ve_due_report/report/overdue_report.rml',
    parser=overdue_report_report,
)
