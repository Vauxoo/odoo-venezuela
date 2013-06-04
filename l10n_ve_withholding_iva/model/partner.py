#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Vauxoo C.A.           
#    Planified by: Nhomar Hernandez
#    Audited by: Vauxoo C.A.
#############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
################################################################################
from osv import fields, osv
import decimal_precision as dp
from tools.translate import _
import urllib
from xml.dom.minidom import parseString
import netsvc

class res_partner(osv.osv):
    _inherit = 'res.partner'
    logger = netsvc.Logger()
    _columns = {
        'wh_iva_agent': fields.boolean('Wh. Agent', help="Indicate if the partner is a withholding vat agent"),
    }
    _defaults = {
        'wh_iva_rate': lambda *a: 0,
    }
    
    def update_rif(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        su_obj = self.pool.get('seniat.url')
        return su_obj.update_rif(cr, uid, ids, context=context)

res_partner()

class seniat_url(osv.osv):

    _inherit = 'seniat.url'
    
    def _parse_dom(self,dom,rif,url_seniat,context=None):
        su_obj = self.pool.get('seniat.url')
        wh_agent = dom.childNodes[0].childNodes[1].firstChild.data.upper()=='SI' and True or False
        wh_rate = su_obj._buscar_porcentaje(rif,url_seniat)
        self.logger.notifyChannel("info", netsvc.LOG_INFO,
            "RIF: %s Found" % rif)
        data = {'wh_iva_agent':wh_agent,'wh_iva_rate':wh_rate}
        return dict(data.items() + super(seniat_url,self)._parse_dom(dom,rif,url_seniat,context=context).items())
    
seniat_url()
