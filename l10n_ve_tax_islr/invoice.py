# -*- encoding: utf-8 -*-
##############################################################################
#
#Copyright (c) 2010 Vauxoo C.A. (http://openerp.com.ve/) All Rights Reserved.
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



class account_invoice(osv.osv):
    _inherit = 'account.invoice'    

    def _get_concept_ids(self, cr, uid, ids, field_name, arg, context={}):
        result = {}
        rate_obj = self.pool.get('concepts.rates.islr')
        for inv in self.browse(cr, uid, ids, context):
            result[inv.id] = []
            ant = 0
            for line in inv.invoice_line:
                grp_ids = []
                if line.product_id.type=='service':
                    grp_ids = rate_obj.search(cr, uid, [('group_id','=',line.product_id.grp_id.id),('situation','=',inv.partner_id.situation)])
                    rates = rate_obj.browse(cr, uid, grp_ids, context=context)
                    ant_grp = False
                    for r in rates:                        
                        if r.rate > ant:
                            if r.group_id.id != ant_grp:
                                result[inv.id] = grp_ids
                                ant_grp = r.group_id.id
                            ant = r.rate
                            
        return result

    _columns = {
        'grp_conpt_ids': fields.function(_get_concept_ids, method=True, type='one2many', relation="concepts.rates.islr", string='ISLR Group', help="Reglamento de retenciones e Impuestos sobre la renta - Decreto No. 1808 de GO No. 36203 fecha 12-05-1997"),

    }


account_invoice()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

