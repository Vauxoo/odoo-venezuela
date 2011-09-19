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

from osv import fields, osv


class res_partner_address(osv.osv):
    _inherit='res.partner.address'
    _description ='Direccion Fiscal Unica'


    def _check_addr_invoice(self,cr,uid,ids,context={}):
        obj_addr = self.browse(cr,uid,ids[0])

        if obj_addr.type == 'invoice':
            cr.execute('select id,type from res_partner_address where partner_id=%s and type=%s', (obj_addr.partner_id.id, obj_addr.type))
            res=dict(cr.fetchall())
            if (len(res) == 1):
                res.pop(ids[0],False)
            if res:
                return False
        return True


    _constraints = [
        (_check_addr_invoice, 'Error ! Ya posee una direccion fiscal asignada. ', ['type'])
    ]

res_partner_address()

