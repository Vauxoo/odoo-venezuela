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



class res_partner(osv.osv):
    _inherit = 'res.partner'
    _description = "Direccion Fiscal Obligatoria"


    def _check_partner_invoice_addr(self,cr,uid,ids,context={}):
        partner_obj = self.browse(cr,uid,ids[0])
        res = [addr for addr in partner_obj.address if addr.type == 'invoice']
        if res:
            return True

        return False

    def _check_partner_code(self,cr,uid,ids,context={}):
        partner_brw = self.browse(cr,uid,ids[0])
        if partner_brw.ref:
            part_ids = self.search(cr, uid, [('ref','=',partner_brw.ref)], limit=2, context=context)
            if part_ids:
                res = dict(map(lambda x:(x,True),part_ids))
                res.pop(partner_brw.id,False)
                if res:
                    return False

        return True

    def _check_partner_vat(self,cr,uid,ids,context={}):
        partner_brw = self.browse(cr,uid,ids[0])
        if partner_brw.vat:
            part_ids = self.search(cr, uid, [('vat','=',partner_brw.vat)], limit=2, context=context)
            if part_ids:
                res = dict(map(lambda x:(x,True),part_ids))
                res.pop(partner_brw.id,False)
                if res:
                    return False

        return True


    _constraints = [
        (_check_partner_invoice_addr, 'Error ! No ha definido una direccion fiscal. ', ['address']),
        (_check_partner_code, 'El codigo del partner. ya fue asignado, revise por favor !. ', []),
        (_check_partner_vat, 'El R.I.F. ya fue asignado, revise por favor !. ', []),        
    ]
    

res_partner()

