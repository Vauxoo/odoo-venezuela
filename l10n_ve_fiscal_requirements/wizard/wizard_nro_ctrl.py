# coding: utf-8
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############################################################################
#    Credits:
#    Coded by: Vauxoo C.A.
#    Planified by: Nhomar Hernandez
#    Audited by: Vauxoo C.A.
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
###############################################################################

from openerp.osv import fields, osv
from openerp.tools.translate import _


class WizNroctrl(osv.osv_memory):
    _name = 'wiz.nroctrl'
    _description = "Wizard that changes the invoice control number"

    def set_noctrl(self, cr, uid, ids, context=None):
        """ Change control number of the invoice
        """
        if context is None:
            context = {}
        data = self.pool.get('wiz.nroctrl').read(cr, uid, ids)[0]
        if not data['sure']:
            raise osv.except_osv(
                _("Error!"),
                _("Please confirm that you want to do this by checking the"
                  " option"))
        inv_obj = self.pool.get('account.invoice')
        n_ctrl = data['name']

        inv_obj.write(cr, uid, context.get('active_id'), {'nro_ctrl': n_ctrl},
                      context=context)
        return {}

    _columns = {
        'name': fields.char('Control Number', 32, required=True),
        'sure': fields.boolean('Are you sure?'),
    }
WizNroctrl()
