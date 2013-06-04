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
import tools
from tools.translate import _
from tools import config
import urllib
from xml.dom.minidom import parseString
import netsvc
import re

class seniat_url(osv.osv):
    """
    OpenERP Model : seniat_url
    """
    logger = netsvc.Logger()
    _name = 'seniat.url'
    _description = __doc__
    _columns = {
        'name':fields.char('URL Seniat for Partner Information',size=255, required=True, readonly=False,help='In this field enter the URL from Seniat for search the fiscal information from partner'),
        'url_seniat':fields.char('URL Seniat for Retention Rate',size=255, required=True, readonly=False,help='In this field enter the URL from Seniat for search the retention rate from partner (RIF)'),
        'url_seniat2':fields.char('URL Seniat for Retention Rate',size=255, required=True, readonly=False,help='In this field enter the URL from Seniat for search the retention rate from partner (CI or Passport)'),
    }
    
    #    Update Partner Information 

    def _load_url(self,retries,url):
        str_error= '404 Not Found'
        while retries > 0:
            try:
                s = urllib.urlopen(url)
                r = s.read()
                ok = not('404 Not Found' in r)
                if ok:
                    self.logger.notifyChannel("info", netsvc.LOG_INFO,
            "Url Loaded correctly %s" % url)
                    return r
            except:
                self.logger.notifyChannel("warning", netsvc.LOG_WARNING,
            "Url could not be loaded %s" % str_error)
                pass
            retries -= 1
        return str_error

    def _parse_dom(self,dom,rif,url_seniat,context={}):
        rif_aux = dom.childNodes[0].getAttribute('rif:numeroRif')
        name = dom.childNodes[0].childNodes[0].firstChild.data
        wh_agent = dom.childNodes[0].childNodes[1].firstChild.data.upper()=='SI' and True or False
        vat_subjected = dom.childNodes[0].childNodes[2].firstChild.data.upper()=='SI' and True or False
        wh_rate = dom.childNodes[0].childNodes[3].firstChild.data
        self.logger.notifyChannel("info", netsvc.LOG_INFO,
            "RIF: %s Found" % rif)
        if name.count('(') > 0:
            name = name[:name.index('(')].rstrip()
        if context.get('spf_info'):
            res= {'name': name,
                  'vat_subjected': vat_subjected,
                  'vat': 'VE'+rif_aux,
                  'wh_iva_rate': wh_rate,
                  'wh_iva_agent': wh_agent}
        else:
            res= {'name': name,'vat_subjected': vat_subjected,'vat':'VE'+rif_aux}  
        return res

    def _print_error(self, error, msg):
        raise osv.except_osv(error,msg)

    def _eval_seniat_data(self,xml_data,vat,context={}):
        if context is None:
            context={}
        if not context.get('all_rif'):
            if xml_data.find('450')>=0 and not vat.find('450')>=0:
                self._print_error(_('Vat Error !'),_('Invalid VAT!'))
            elif xml_data.find('452')>=0 and not vat.find('452')>=0:
                self._print_error(_('Vat Error !'),_('Unregistered VAT!'))
            elif xml_data.find("404")>=0 and not vat.find('404')>=0:
                self._print_error(_('No Connection !'),_("Could not connect! Check the URL "))
            else:
                return False
        else:
            if xml_data.find('450')>=0 or xml_data.find('452')>=0 or xml_data.find("404")>=0:
                return True
            else:
                return False

    def _dom_giver(self, url1, url2, url3, vat, context):
        if context.get('ci_pas'):
            xml_data = self._load_url(3,url3 % vat)
            match = re.search(r'No existe el contribuyente solicitado', xml_data)
            vat = '0'*(8-len(vat))+vat
            match2 = re.search(r'[VJEG]'+vat+'[0-9]{1}', xml_data)
            if match:
                return False
            elif match2:
                vat = match2.group(0)
        xml_data = self._load_url(3,url1 % vat)
        
        if not self._eval_seniat_data(xml_data,vat,context):
            dom = parseString(xml_data)
            return self._parse_dom(dom, vat, url2,context=context)
        else:
            return False

    def _update_partner(self, cr, uid, id, context=None):
        rp_obj = self.pool.get('res.partner')
        rp_obj.write(cr, uid, id, {'seniat_updated': True})

    def update_rif(self, cr, uid, ids, context={}):
        aux=[]
        rp_obj = self.pool.get('res.partner')
        addr_obj = self.pool.get('res.partner.address')
        url_obj = self.browse(cr, uid, self.search(cr, uid, []))[0]
        url1 = url_obj.name + '%s'
        url2 = url_obj.url_seniat + '%s'
        url3 = url_obj.url_seniat2 + '%s'
        if context.get('exec_wizard'):
            res = self._dom_giver(url1, url2, url3, context['vat'],context)
            if res:
                self._update_partner(cr, uid, ids, context)
                return res
            else:
                return False
        for partner in rp_obj.browse(cr,uid,ids):
            rp_obj.write(cr, uid, partner.id, {'seniat_updated': False})
            if partner.vat:
                partner_id =partner.id
                code = addr_obj.browse(cr,uid,addr_obj.search(cr,uid,[('partner_id','=',partner_id),('type','=','invoice')]))[0].country_id.code
                if code == 'VE':
                    if rp_obj.check_vat_ve(partner.vat[2:],context):
                        res = self._dom_giver(url1, url2, url3,partner.vat[2:],context)
                        if res:
                            rp_obj.write(cr,uid,partner.id,res)
                            self._update_partner(cr, uid, partner.id, context)
                        else:
                            if not context.get('all_rif'):
                                return False
                                #~ self._print_error(_('Error'),_("Does not exist the contributor requested"))
                    else:
                        if not context.get('all_rif'):
                            return False
                            #~ self._print_error(_('Error'),_("The RIF, CI or passport are not well constructed, please check \n The format of the RIF should be for example J1234567890,CI should be 12345678, and passports must be D123456789"))
                else:
                    if not context.get('all_rif'):
                        return False
                        #~ self._print_error(_('Error'),_("The country in invoice address is not Venezuela, can not establish connection with sSENIAT"))
            else:
                if partner.address:
                    invoices_addr_country = [i.country_id and i.country_id.code or False  for i in partner.address if i.type == 'invoice']
                    if invoices_addr_country:
                        country = [j for j in invoices_addr_country if j]
                        if country and 'VE' in country and not context.get('all_rif',False):
                                self._print_error(_('Vat Error !'),_('The field vat is empty'))
        return True

    def connect_seniat(self, cr, uid, ids, context={}, all_rif=False):
        ctx = context.copy()
        if all_rif:
            ctx.update({'all_rif': True})
        self.update_rif(cr, uid, ids, context=ctx)
        return True

seniat_url()
