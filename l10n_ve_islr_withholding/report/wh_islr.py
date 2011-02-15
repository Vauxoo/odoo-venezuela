# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Netquatro C.A. (http://openerp.netquatro.com/) All Rights Reserved.
#                    Javier Duran <javier.duran@netquatro.com>
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

from report import report_sxw
from osv import osv

class rep_comprobante_islr(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(rep_comprobante_islr, self).__init__(cr, uid, name, context=context)    
        self.localcontext.update({
            'get_company_addr': self._get_company_addr,
        })

    def _get_company_addr(self):
        company_obj = self.pool.get('res.company')
        company_ids = company_obj.search(self.cr,self.uid,[])
        company = company_obj.browse(self.cr, self.uid, company_ids[0])
        addr_com = self._get_partner_addr(company.partner_id.id)
        return addr_com

    #metodo que retorna la direccion fiscal si es de tipo invoice o de tipo delivery
    def _get_partner_addr(self, idp=None):
        if not idp:
            return []
        addr_obj = self.pool.get('res.partner.address')
        res = 'NO HAY DIRECCION FISCAL DEFINIDA'
        addr_ids = addr_obj.search(self.cr,self.uid,[('partner_id','=',idp), ('type','=','invoice')])
        addr_ids2 = addr_obj.search(self.cr,self.uid,[('partner_id','=',idp), ('type','=','delivery')])
        addr_inv={}
        lista=""
        if addr_ids: #si es de tipo invoice la direccion              
            addr = addr_obj.browse(self.cr,self.uid, addr_ids[0])
        if addr_ids2:#si es de tipo delivery la direccion 
            addr = addr_obj.browse(self.cr,self.uid, addr_ids2[0])
            
            
        var =    (addr.street and ('%s '%addr.street.title()) or '')    + \
             (addr.street2 and ('%s '%addr.street2.title()) or '')      +\
             (addr.zip and ('Cod. Postal: %s, '%addr.zip) or '')        +\
             (addr.state_id and ('%s, '%addr.state_id.name.title()) or '')+ \
             (addr.city and ('%s, '%addr.city.title()) or '')+ \
             (addr.country_id and ('%s '%addr.country_id.name.title()) or '')+ \
             (addr.phone and ('\nTelf:%s, '%addr.phone) or '')          +\
             (addr.fax and ('Fax:%s'%addr.fax) or '')
        if addr_ids:
            addr_inv['invoice'] = var
            lista= var
        if addr_ids2:#si es de tipo delivery la direccion 
            addr_inv['delivery'] = var
            lista= var
        if addr_inv:
            respuesta=lista
        else:
            respuesta=res
        return respuesta 

report_sxw.report_sxw(
    'report.voucher.wh.islr11',
    'islr.wh.doc',
    'addons/islr_withholding/report/wh_islr_report.rml',
    parser=rep_comprobante_islr,
    header=False
)
