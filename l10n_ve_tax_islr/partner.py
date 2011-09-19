# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    nhomar@vauxoo.com & Javier Duran <javier@vauxoo.com>
#
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
#
##############################################################################
from osv import osv
from osv import fields
from tools import config
from tools.translate import _

class res_partner(osv.osv):
    """
    To calc the condition of the partner. And in future make decisions about ISLR    """    
    _inherit = 'res.partner'

    def _default_company(self, cr, uid, context={}):
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        if user.company_id:
            return user.company_id.id
        return self.pool.get('res.company').search(cr, uid, [('parent_id', '=', False)])[0]


    def _valid_get(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        sit = {'pnvc':'PNR','pnxc':'PNNR','pjvc':'PJD','pjxc':'PJND','pjvs':'PJNCD'}
        tper = 'pj'
        tdom = 'v'
        tcon = 'c'
        company_id = self._default_company(cr, uid)
        company = self.pool.get('res.company').browse(cr, uid, company_id, context=context)

        for partner in self.browse(cr, uid, ids, context=context):
            if not partner.vat:
                raise osv.except_osv(_('Error'), _('Not number VAT defined in the partner !'))

            vat_type = partner.vat[2:3].upper()
            if vat_type in ['V','E']:
                tper = 'pn'
            if company.partner_id.country != partner.country:
                tdom = 'x'
            if vat_type in ['J','G'] and partner.no_const:
                tcon = 's'

            kpasw=tper+tdom+tcon
            res[partner.id] = sit[kpasw]
        return res


    _columns = {
        'situation' : fields.function(_valid_get, method=True, string="Situation", type="selection", selection=[
            ('PNR','Persona Natural Residente'),
            ('PNNR','Persona Natural No Residente'),
            ('PJD','Persona Jurídica Domiciliada'),
            ('PJND','Persona Jurídica No Domiciliada'),
            ('PJNCD','Persona Jurídica No Constituida Domiciliada')
        ], readonly=True, select=True, help="The legal partner status on Vzla."),
        'no_const': fields.boolean('Constituted', help="Check this if the partner is not constituted on Vzla."),

    }
    _defaults = {
        'no_const': lambda *a: 0,
    }
res_partner()
