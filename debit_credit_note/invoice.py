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

import time
from osv import fields, osv



class account_invoice(osv.osv):
    _inherit = 'account.invoice'



    _description = "Debit and Credit Notes"
    _columns = {
        'parent_id':fields.many2one('account.invoice', 'Parent Invoice', select=True, readonly=True, states={'draft':[('readonly',False)]}, help='Al seleccionar este campo, la factura se convertira en una nota de debito'),
        'child_ids':fields.one2many('account.invoice', 'parent_id', 'Debit and Credit Notes', readonly=True, states={'draft':[('readonly',False)]}),
        'name': fields.char('Description', size=128, select=True,readonly=True, states={'draft':[('readonly',False)]}),
    }
    
    def action_number(self, cr, uid, ids, *args):
        cr.execute('SELECT id, type, number, move_id, reference ' \
                'FROM account_invoice ' \
                'WHERE id IN ('+','.join(map(str,ids))+')')
        obj_inv = self.browse(cr, uid, ids)[0]
        for (id, invtype, number, move_id, reference) in cr.fetchall():
            if not number:
                if obj_inv.journal_id.invoice_sequence_id:
                    sid = obj_inv.journal_id.invoice_sequence_id.id
                    number = self.pool.get('ir.sequence').get_id(cr, uid, sid, 'id=%s', {'fiscalyear_id': obj_inv.period_id.fiscalyear_id.id})
                else:
                    if invtype not in ('in_refund','out_refund') and obj_inv.parent_id and obj_inv.parent_id.id:
                        type_dict = {
                                'out_invoice': 'out_debit', # Customer Invoice
                                'in_invoice': 'in_debit',   # Supplier Invoice
                        }
                        number = self.pool.get('ir.sequence').get(cr, uid,
                                'account.invoice.' + type_dict[invtype])
                    else:
                        number = self.pool.get('ir.sequence').get(cr, uid,
                                'account.invoice.' + invtype)
                if invtype in ('in_invoice', 'in_refund'):
                    ref = reference
                else:
                    ref = self._convert_ref(cr, uid, number)
                cr.execute('UPDATE account_invoice SET number=%s ' \
                        'WHERE id=%s', (number, id))
                cr.execute('UPDATE account_move SET ref=%s ' \
                        'WHERE id=%s AND (ref is null OR ref = \'\')',
                        (ref, move_id))
                cr.execute('UPDATE account_move_line SET ref=%s ' \
                        'WHERE move_id=%s AND (ref is null OR ref = \'\')',
                        (ref, move_id))
                cr.execute('UPDATE account_analytic_line SET ref=%s ' \
                        'FROM account_move_line ' \
                        'WHERE account_move_line.move_id = %s ' \
                            'AND account_analytic_line.move_id = account_move_line.id',
                            (ref, move_id))
        return True

account_invoice()





