# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010 Vauxoo C.A. (http://openerp.com.ve/) All Rights Reserved.
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

from osv import fields, osv
import pooler



class one2many_mod(fields.one2many):
    def get(self, cr, obj, ids, name, user=None, offset=0, context=None, values=None):
        if not context:
            context = {}
        res = {}
        pool = pooler.get_pool(cr.dbname)
        for obj in obj.browse(cr, user, ids, context=context):
            res[obj.id] = []
            obj_addr = pool.get('res.partner.address')
            addr_ids = obj_addr.search(cr, user, [('type', '=', 'invoice'),('partner_id', '=', obj.id)])
            res[obj.id] = addr_ids
            
        return res


class res_partner(osv.osv):
    _inherit = 'res.partner'
    _description = "Partner Generico"
    _columns = {
        'gene': fields.boolean('Es partner generico', help="Indica si el partner es un partner de proposito general"),
        'adr_inv_ids': one2many_mod('res.partner.address', 'partner_id', 'Direccion Fiscal'),

    }


res_partner()

