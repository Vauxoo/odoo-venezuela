# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Vauxoo C.A. (http://openerp.com.ve/) All Rights Reserved.
#                    Javier Duran <javier@vauxoo.com>
# 
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from osv import osv, fields
from tools.translate import _


class sale_order(osv.osv):
    _inherit = "sale.order"
    
    _sql_constraints = [
        ('o_ref_partner_uniq', 'unique (client_order_ref,partner_id)', 'La orden de compra debe ser unica por Cliente !')
    ]
    


    def test_ocreq(self, cr, uid, ids):
        res = True
        for os in self.browse(cr, uid, ids):
            if not os.partner_id:
                raise osv.except_osv(_('Error, No hay Cliente !'),
                    _('Por favor seleccione un cliente, si desea generar la factura.'))

            valor = os.client_order_ref and os.client_order_ref.strip()
            if os.partner_id.ocreq and not valor:
                raise osv.except_osv(_('Error, No hay Orden de Compra !'),
                    _('Por introduzca el Nro. de la orden de compra del cliente, si desea generar la factura.'))


        return res

    
sale_order()
