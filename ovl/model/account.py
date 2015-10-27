# coding: utf-8
###############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://www.vauxoo.com>).
#    All Rights Reserved
###############################################################################
#    Credits:
#    Coded by: Katherine Zaoral <kathy@vauxoo.com>
#    Planified by: Humberto Arocha <hbto@vauxoo.com>
#    Audited by: Humberto Arocha <hbto@vauxoo.com>
###############################################################################
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

from openerp.osv import osv
from openerp.tools.translate import _


class AccountInvoice(osv.Model):

    _inherit = 'account.invoice'

    def show_entries(self, cur, uid, ids, context=None):
        """
        This method is used in a button name journal entries that it is in the
        wh tag in the account invoice form view. This method will search for
        the corresponding account.move.line associated for the current invoice
        and will show then in a tree view.
        """
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        aml_obj = self.pool.get('account.move.line')
        for brw in self.browse(cur, uid, ids, context=context):
            domain = [('invoice', '=', brw.id)]
            aml_ids = aml_obj.search(cur, uid, domain, context=context)
            aml_ids.extend([aml_brw.id for aml_brw in brw.move_lines])
            aml_ids = list(set(aml_ids))

            am_brws = list()
            aml_brws = aml_obj.browse(cur, uid, aml_ids, context=context)
            for aml in aml_brws:
                am_brws.append(aml.move_id)
            am_brws = set(am_brws)
            aml_ids = list()
            for am_brw in am_brws:
                aml_ids += [aml_brw.id for aml_brw in am_brw.line_id]

        return {
            'domain': str([('id', 'in', aml_ids)]),
            'name': _('Journal Entries'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.move.line',
            'view_id': False,
            'type': 'ir.actions.act_window'
        }
