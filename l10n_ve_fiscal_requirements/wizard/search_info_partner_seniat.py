# coding: utf-8
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    This module is developed by Vauxoo
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
#
##############################################################################
from openerp.osv import fields, osv
from openerp.tools.translate import _


class SearchInfoPartnerSeniat(osv.osv_memory):

    _name = "search.info.partner.seniat"
    _columns = {
        'vat': fields.char(
            'ID Number (Cedula, Passport, VAT Number)', size=64,
            help='The VAT number must be in this format J1234567890, if you'
                 ' are looking for a cedula 12345678 and passport D123456789',
            required=True),
        'name': fields.char('Partner', size=256, help='Partner name'),
        'wh_iva_agent': fields.boolean(
            'Withholding Agent', help='It is withholding agent'),
        'wh_iva_rate': fields.float(
            'Percent of withholding',
            help='What is the percentil of withholding that you must to apply'
                 ' to this supplier if you are withholding agent'),
        'vat_subjected': fields.boolean(
            'Pay VAY',
            help='Pay VAT, in spanish known as : Contribuyente formal'),
    }

    def search_partner_seniat(self, cr, uid, ids, context=None):
        """ Check vat of the partner and update iva rate
        """
        if context is None:
            context = {}
        this = self.browse(cr, uid, ids)[0]
        su_obj = self.pool.get('seniat.url')
        rp_obj = self.pool.get('res.partner')
        vat = this.vat.upper()
        res = {'name': _('The requested contributor does not exist'),
               'vat_subjected': False, 'vat': vat, 'wh_iva_agent': False,
               'wh_iva_rate': 0.0}

        if 'VE' in vat:
            vat = vat[2:]

        if rp_obj.check_vat_ve(vat, context=context):
            res = su_obj._dom_giver(cr, uid, vat, context)
        self.write(cr, uid, ids, res)

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'search.info.partner.seniat',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': this.id,
            'views': [(False, 'form')],
            'target': 'new',
        }
SearchInfoPartnerSeniat()
