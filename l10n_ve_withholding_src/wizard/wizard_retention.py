# coding: utf-8
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############################################################################
#    Credits:
#    Coded by: Vauxoo C.A.
#    Planified by: Humberto Arocha
#    Audited by: Vauxoo C.A.
#############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or (at
#    your option) any later version.
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


class WizRetention(osv.osv_memory):
    _name = 'wiz.retention'
    _description = "Wizard that changes the retention value"

    def set_retention(self, cr, uid, ids, context=None):
        """ Change value of the retention
        """
        if context is None:
            context = {}
        data = self.pool.get('wiz.retention').read(cr, uid, ids)[0]
        if not data['sure']:
            raise osv.except_osv(
                _("Error!"),
                _("Please confirm that you want to do this by checking the"
                  " option"))

        inv_obj = self.pool.get('account.invoice')
        n_retention = data['name']

        if n_retention and n_retention > 5:
            raise osv.except_osv(_("Error!"), _("Maximum retention is 5%"))
        else:
            inv_obj.write(cr, uid, context.get('active_id'),
                          {'wh_src_rate': n_retention}, context=context)

        return {}

    _columns = {
        'name': fields.float('Retention Value', required=True),
        'sure': fields.boolean('Are you sure?'),
    }

WizRetention()
