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
from openerp.tools.translate import _


class ProductTemplate(osv.osv):

    _inherit = "product.template"

    _columns = {
        'concept_id': fields.many2one(
            'islr.wh.concept', 'Withhold  Concept', required=False,
            help="Concept Income Withholding to apply to the service"),
    }


class ProductProduct(osv.osv):

    _inherit = "product.product"

    def onchange_product_type(self, cr, uid, ids, prd_type, context=None):
        """ Add a default concept for products that are not service type,
        Returns false if the product type is not a service, and if the
        product is service, returns the first concept except 'No apply
        withholding'
        @param prd_type: product type new
        """
        concept_id = False
        if prd_type != 'service':
            concept_obj = self.pool.get('islr.wh.concept')

            concept_id = concept_obj.search(cr, uid,
                                            [('withholdable', '=', False)])
            concept_id = concept_id and concept_id[0] or False
            if not concept_id:
                raise osv.except_osv(
                    _('Invalid action !'),
                    _("Must create the concept of income withholding"))

        return {'value': {'concept_id': concept_id or False}}
