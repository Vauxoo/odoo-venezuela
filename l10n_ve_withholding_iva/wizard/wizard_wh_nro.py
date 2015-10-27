# coding: utf-8
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############################################################################
#    Credits:
#    Coded by: Maria Gabriela Quilarque  <gabrielaquilarque97@gmail.com>
#    Planified by: Nhomar Hernandez
#    Finance by: Helados Gilda, C.A. http://heladosgilda.com.ve
#    Audited by: Humberto Arocha humberto@openerp.com.ve
#############################################################################
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
##############################################################################


from openerp.osv import fields, osv
from openerp.tools.translate import _


class WizardChangeNumberWhIva(osv.osv_memory):
    _name = 'wizard.change.number.wh.iva'
    _description = "Wizard that changes the withholding number"

    def default_get(self, cr, uid, field_list, context=None):
        # NOTE: use field_list argument instead of fields for fix the pylint
        # error W0621 Redefining name 'fields' from outer scope
        context = context or {}
        data = super(WizardChangeNumberWhIva, self).default_get(
            cr, uid, field_list, context)
        if (context.get('active_model') == 'account.wh.iva' and
                context.get('active_id')):
            wh_iva = self.pool.get('account.wh.iva').browse(
                cr, uid, context['active_id'], context=context)
            if wh_iva.number:
                nro = wh_iva.number.split('-')
                per = wh_iva.period_id.code.split('-')
                new_number = '%s-%s-%s' % (per[1], per[2], nro[2])
                data.update({'name': new_number})
        return data

    def set_number(self, cr, uid, ids, context):
        data = self.pool.get('wizard.change.number.wh.iva').read(
            cr, uid, ids)[0]
        if not data['sure']:
            raise osv.except_osv(
                _("Error!"),
                _("Please confirm that you want to do this by checking the"
                  " option"))
        wh_obj = self.pool.get('account.wh.iva')
        number = data['name']

        wh_iva = wh_obj.browse(cr, uid, context['active_id'])
        if wh_iva.state != 'done':
            raise osv.except_osv(
                _("Error!"),
                _('You can\'t change the number when state <> "Done"'))

        wh_obj.write(cr, uid, context['active_id'], {'number': number},
                     context=context)
        return {}

    _columns = {
        'name': fields.char('Withholding number', 32, required=True),
        'sure': fields.boolean('Are you sure?'),
    }
WizardChangeNumberWhIva()
