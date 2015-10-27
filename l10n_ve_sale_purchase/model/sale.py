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


class SaleOrderLine(osv.osv):
    _inherit = "sale.order.line"

    _columns = {
        'concept_id': fields.many2one(
            'islr.wh.concept', 'Withhold  Concept',
            help="Withhold concept associated with this rate", required=False),
    }

#    def product_id_change(self, cr, uid, ids, pricelist, product,
#                          qty=0,uom=False, qty_uos=0, uos=False, name='',
#                          partner_id=False,lang=False, update_tax=True,
#                          date_order=False, packaging=False,
#                          fiscal_position=False, flag=False):
#        def get_concept():
#            concept_obj = self.pool.get('islr.wh.concept')
#            concept_id = concept_obj.search(
#               cr, uid, [('withholdable','=',False)])
#            return concept_id and concept_id[0] or False
#        res = super(sale_order_line, self).product_id_change(
#           cr, uid, ids, pricelist, product, qty,uom, qty_uos, uos, name,
#           partner_id,lang, update_tax, date_order, packaging,
#           fiscal_position, flag)
#        if not product:
#            concept_id = get_concept()
#            if concept_id:
#                res['value']['concept_id']=concept_id
#            return res
#        prod_brw = self.pool.get('product.product').browse(cr, uid, product)
#        res['value']['concept_id'] = prod_brw.concept_id and \
#           prod_brw.concept_id.id or get_concept()
#        return res
# ethod that adds to the original in concept retention lines for sale, is
# called by action_invoice_create() in sale.order
    def invoice_line_create(self, cr, uid, ids, context=None):
        """ Assing concept_id to the invoice lines
        """
        context = context or {}
        create_ids = super(SaleOrderLine, self).invoice_line_create(
            cr, uid, ids, context)
        invoice_line_brws = self.pool.get('account.invoice.line').browse(
            cr, uid, create_ids)
        order_line_sale_brws = self.pool.get('sale.order.line').browse(cr, uid,
                                                                       ids)
        for line_invoice in invoice_line_brws:  # lineas de la factura
            # lineas de la orden de venta
            for line_sale in order_line_sale_brws:
                # si es la misma linea
                if line_sale.product_id == line_invoice.product_id:
                    self.pool.get('account.invoice.line').write(
                        cr, uid, line_invoice.id,
                        {'concept_id': line_sale.concept_id.id})
        return create_ids
