# coding: utf-8
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############################################################################
#    Credits:
#    Coded by: Humberto Arocha           <hbto@vauxoo.com>
#    Planified by: Humberto Arocha & Nhomar Hernandez
#    Audited by: Humberto Arocha           <hbto@vauxoo.com>
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
from openerp.osv import fields, orm


class AccountWhIvaLine(orm.Model):
    _inherit = "account.wh.iva.line"
    _columns = {
        'fb_id': fields.many2one(
            'fiscal.book', 'Fiscal Book',
            help='Fiscal Book where this line is related to'),
    }

    def _update_wh_iva_lines(self, cr, uid, ids, inv_id, fb_id, context=None):
        """
        It relate the fiscal book id to the according withholding iva lines.
        """
        context = context or {}
        inv_obj = self.pool.get('account.invoice')
        inv = inv_obj.browse(cr, uid, inv_id, context=context)
        if inv.wh_iva and inv.wh_iva_id:
            awil_ids = self.search(
                cr, uid, ids, [('invoice_id', '=', inv.id)], context=context)
            self.write(cr, uid, awil_ids, {'fb_id': fb_id}, context=context)
        return True
