# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Vauxoo C.A. (http://openerp.com.ve/) All Rights Reserved.
#                    Javier Duran <javier@vauxoo.com>
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

class pur_sal_wh_book(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(pur_sal_wh_book, self).__init__(cr, uid, name, context)    
        self.localcontext.update({
            'time': time,
            'get_partner_addr': self._get_partner_addr,
            'get_alicuota': self._get_alicuota,
            'get_rif': self._get_rif,
            'get_data':self._get_data,
            'get_exc':self._get_exc,
            'get_month':self._get_month,
            'get_dates':self._get_dates,
            'get_totals':self._get_totals,
        })

    def _get_partner_addr(self, idp=None):
        if not idp:
            return []

        addr_obj = self.pool.get('res.partner.address')
        addr_inv = 'NO HAY DIRECCION FISCAL DEFINIDA'
        addr_ids = addr_obj.search(self.cr,self.uid,[('partner_id','=',idp), ('type','=','invoice')])
        if addr_ids:                
            addr = addr_obj.browse(self.cr,self.uid, addr_ids[0])
            addr_inv = (addr.street or '')+' '+(addr.street2 or '')+' '+(addr.zip or '')+ ' '+(addr.city or '')+ ' '+ (addr.country_id and addr.country_id.name or '')+ ', TELF.:'+(addr.phone or '')
        return addr_inv 


    def _get_alicuota(self, tnom=None):
        if not tnom:
            return []

        tax_obj = self.pool.get('account.tax')
        tax_ids = tax_obj.search(self.cr,self.uid,[('name','=',tnom)])[0]
        tax = tax_obj.browse(self.cr,self.uid, tax_ids)

        return tax.amount*100
    
    def _get_month(self, form):
        months=["Enero","Febrero","Marzo","Abril","Mayo","Junio","Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"]
        res = months[time.strptime(form['date_start'],"%Y-%m-%d")[1]-1]
        return res
    
    def _get_dates(self, form):
        res=[]
        res.append(form['date_start'])
        res.append(form['date_end'])
        return res

    def _get_rif(self, vat=''):
        if not vat:
            return []
        return vat[2:].replace(' ', '')


    def _get_data(self,form):
        d1=form['date_start']
        d2=form['date_end']
        if form['model']=='wh_p':
            book_type='fiscal.reports.whp'           
        else:
            book_type='fiscal.reports.whs'
        data=[]
        fr_obj = self.pool.get(book_type)
        fr_ids = fr_obj.search(self.cr,self.uid,[('ar_date_ret', '<=', d2), ('ar_date_ret', '>=', d1)])
        data = fr_obj.browse(self.cr,self.uid, fr_ids)
        return data

    def _get_exc(self,obj_rl):
        excent=0.0
        for taxes in obj_rl.tax_line:
            if not taxes.tax_amount:
                excent=excent + taxes.base_amount
        return excent
    
    def _get_totals(self,form):
        d1=form['date_start']
        d2=form['date_end']
        if form['model']=='wh_p':
            book_type='fiscal.reports.whp'           
        else:
            book_type='fiscal.reports.whs'
        fr_obj = self.pool.get(book_type)
        fr_ids = fr_obj.search(self.cr,self.uid,[('ar_date_ret', '<=', d2), ('ar_date_ret', '>=', d1)])
        total=[0.0,0.0,0.0,0.0]
        for d in fr_obj.browse(self.cr,self.uid, fr_ids):
            total[0]=total[0]+d.ai_amount_total
            total[1]=total[1]+d.ai_amount_untaxed
            total[2]=total[2]+d.ai_amount_tax
            total[3]=total[3]+d.ar_id.total_tax_ret
        return total
      
report_sxw.report_sxw(
    'report.fiscal.reports.whp.whp_seniat',
    'fiscal.reports.whp',
    'addons/l10n_ve_fiscal_reports/report/witholding_book.rml',
    parser=pur_sal_wh_book,
    header=False
)      
