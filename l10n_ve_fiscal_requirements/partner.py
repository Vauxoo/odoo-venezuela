# -*- coding: utf-8 -*-
##############################################################################
#
#    
#    Programmed by: Alexander Olivares <olivaresa@gmail.com>
#
#    This the script to connect with Seniat website 
#    for consult the rif asociated with a partner was taken from:
#    
#    http://siv.cenditel.gob.ve/svn/sigesic/ramas/sigesic-1.1.x/sigesic/apps/comun/seniat.py
#
#    This script was modify by:
#                   Javier Duran <javier@vauxoo.com>
#                   Miguel Delgado <miguel@openerp.com.ve>
#                   Israel Fermín Montilla <israel@openerp.com.ve>
#                   Juan Márquez <jmarquez@tecvemar.com.ve>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import fields, osv
from tools.translate import _
import decimal_precision as dp
import re

class res_partner_address(osv.osv):
    _inherit='res.partner.address'

    '''
    Invoice Address uniqueness check
    '''
    def _check_addr_invoice(self,cr,uid,ids,context={}):
        obj_addr = self.browse(cr,uid,ids[0])
        if obj_addr.partner_id.vat and obj_addr.partner_id.vat[:2].upper() == 'VE':
            if obj_addr.type == 'invoice':
                cr.execute('select id,type from res_partner_address where partner_id=%s and type=%s', (obj_addr.partner_id.id, obj_addr.type))
                res=dict(cr.fetchall())
                if (len(res) == 1):
                    res.pop(ids[0],False)
                if res:
                    return False
        return True


    _constraints = [
        (_check_addr_invoice, _('Error ! The partner already has an invoice address.'), [])
    ]

res_partner_address()


class res_partner(osv.osv):
    _inherit = 'res.partner'
   
    _columns = {
        'seniat_updated': fields.boolean('Seniat Updated', help="This field indicates if partner was updated using SENIAT button"),
        'wh_iva_rate': fields.float(
            string='Rate',
            digits_compute=dp.get_precision('Withhold'),
            help="Withholding vat rate"),
    }

    _default = {
        'seniat_updated': False,
    }

    def name_search(self,cr,uid,name='',args=[],operator='ilike',context=None,limit=80):
	if context is None: 
	    context={}
	ids= []
	if len(name) >= 2:
	    ids = self.search(cr, uid, [('vat',operator,name)] + args, limit=limit, context=context)
	if not ids:
	    ids = self.search(cr,uid,[('name',operator,name)] + args, limit=limit, context=context)
	return self.name_get(cr,uid,ids,context=context)
    
    '''
    Required Invoice Address
    '''
    def _check_partner_invoice_addr(self,cr,uid,ids,context={}):
        partner_obj = self.browse(cr,uid,ids[0])
        if partner_obj.vat and partner_obj.vat[:2].upper() == 'VE':
            if hasattr(partner_obj, 'address'):
                res = [addr for addr in partner_obj.address if addr.type == 'invoice']
                if res:
                    return True
                else:
                    return False
            else:
                return True
        return True

    def _check_vat_uniqueness(self, cr, uid, ids, context={}):
        partner_obj = self.pool.get('res.partner')
        #Check if its possible to use 'browse' in this 'read'
        current_partner = partner_obj.read(cr, uid, ids, ['vat', 'address'])[0]

        if not 'VE' in [a.country_id.code for a in self.pool.get('res.partner.address').browse(cr, uid, current_partner['address'])]:
            return True

        current_vat = current_partner['vat']

        if not current_vat or current_vat.strip()=='':
            return True # Accept empty VAT's
            
        duplicates = partner_obj.read(cr, uid, partner_obj.search(cr, uid, [('vat', '=', current_vat)]), ['vat'])

        return not current_vat in [p['vat'] for p in duplicates if p['id'] != current_partner['id']]

    _constraints = [
        (_check_partner_invoice_addr, _('Error ! The partner does not have an invoice address.'), []),
        (_check_vat_uniqueness, _("Error ! Partner's VAT must be a unique value or empty"), []),
    ]

    def vat_change_fiscal_requirements(self, cr, uid, ids, value, context=None):
        if context is None:
            context={}
        if not value:
            return super(res_partner,self).vat_change(cr, uid, ids, value, context=context)
        res = self.search(cr, uid, [('vat', 'ilike', value)])
        if res:
            rp = self.browse(cr, uid, res[0],context=context)
            return {'warning':  {
                                'title':_('Vat Error !'),
                                'message':_('The VAT [%s] looks like '%value + 
                                            '[%s] which is'%rp.vat.upper()+
                                            ' already being used by: %s'%rp.name.upper())
                                }
                   }
        else:
            return super(res_partner,self).vat_change(cr, uid, ids, value, context=context)

    def check_vat_ve(self, vat, context = None):
        '''
        Check Venezuelan VAT number, locally caled RIF.
        RIF: JXXXXXXXXX RIF CEDULA VENEZOLANO: VXXXXXXXXX CEDULA EXTRANJERO: EXXXXXXXXX
        '''
        
        if context is None:
            context={}
        if re.search(r'^[VJEG][0-9]{9}$', vat):
            context.update({'ci_pas':False})
            return True
        if re.search(r'^([0-9]{1,8}|[D][0-9]{9})$', vat):
            context.update({'ci_pas':True})    
            return True
        return False
        
    def update_rif(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        su_obj = self.pool.get('seniat.url')
        return su_obj.update_rif(cr, uid, ids, context=context)

res_partner()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
