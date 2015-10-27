# coding: utf-8
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############################################################################
#    Credits:
#    Coded by: Humberto Arocha           <humberto@openerp.com.ve>
#              Maria Gabriela Quilarque  <gabrielaquilarque97@gmail.com>
#              Javier Duran              <javier@vauxoo.com>
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


class PurchaseOrderLine(osv.osv):

    _inherit = "purchase.order.line"

    _columns = {
        'concept_id': fields.many2one(
            'islr.wh.concept', 'Withhold  Concept',
            help="Withhold concept associated with this rate", required=False),
    }

    def product_id_change(self, cr, uid, ids, pricelist, product, qty, uom,
                          partner_id, date_order=False, fiscal_position=False,
                          date_planned=False, name=False, price_unit=False,
                          notes=False):
        """ This method loads the withholding concept to a product automatically
        """
        def get_concept():
            concept_obj = self.pool.get('islr.wh.concept')
            concept_id = concept_obj.search(cr, uid,
                                            [('withholdable', '=', False)])
            return concept_id and concept_id[0] or False
        res = super(PurchaseOrderLine, self).product_id_change(
            cr, uid, ids, pricelist, product, qty, uom, partner_id, date_order,
            fiscal_position, date_planned, name, price_unit, notes)
        if not product:
            concept_id = get_concept()
            if concept_id:
                res['value']['concept_id'] = concept_id
            return res
        prod_brw = self.pool.get('product.product').browse(cr, uid, product)
        res['value']['concept_id'] = prod_brw.concept_id and \
            prod_brw.concept_id.id or get_concept()
        return res


class PurchaseOrder(osv.osv):
    _inherit = 'purchase.order'

    def _prepare_inv_line(self, cr, uid, account_id, order_line, context=None):
        """ Update concept_id field to the prepare line
        """
        data = super(PurchaseOrder, self)._prepare_inv_line(
            cr, uid, account_id, order_line, context=context)
        data.update(
            {'concept_id':
             order_line and order_line.concept_id and
             order_line.concept_id.id})
        return data
