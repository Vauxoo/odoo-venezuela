# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Humberto Arocha           <humberto@openerp.com.ve>
#              Maria Gabriela Quilarque  <gabriela@vauxoo.com>
#              Javier Duran              <javier@vauxoo.com>
#    Planified by: Nhomar Hernandez
#    Finance by: Helados Gilda, C.A. http://heladosgilda.com.ve
#    Audited by: Humberto Arocha humberto@openerp.com.ve
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
##############################################################################
from openerp.osv import osv, fields


class stock_picking(osv.osv):
    _inherit = 'stock.picking'

    def action_invoice_create(self, cursor, user, ids, journal_id=False, group=False, type='out_invoice', context=None):
        """ Function that adds the concept of retention to the invoice_lines from
        a purchase order or sales order with billing method from picking list
        """
        if context is None:
            context = {}
        data = super(stock_picking, self).action_invoice_create(cursor, user, ids, journal_id, group, type, context)
        picking_id = data.keys()[0]
        invoice_id = data[picking_id]
        invoice_brw = self.pool.get('account.invoice').browse(cursor, user, invoice_id)
        invoice_line_obj = self.pool.get('account.invoice.line')
        for l in invoice_brw.invoice_line:
            invoice_line_obj.write(cursor, user, l.id, {'concept_id':
                l.product_id and l.product_id.concept_id and l.product_id.concept_id.id or False})
        return data

    _columns = {
        'nro_ctrl': fields.char('Invoice ref.', size=32, readonly=True, states={'draft': [('readonly', False)]}, help="Invoice reference"),
    }
