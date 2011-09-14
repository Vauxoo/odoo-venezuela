# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Latinux Inc (http://www.latinux.com/) All Rights Reserved.
#                    Javier Duran <jduran@corvus.com.ve>
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





class account_move(osv.osv):
    _inherit = 'account.move'

    def action_update_period(self, cr, uid, ids, context={}):
        moves = self.browse(cr, uid, ids[0])
        period_ids = self.pool.get('account.period').search(cr,uid,[('date_start','<=',moves.date),('date_stop','>=',moves.date)])
        if len(period_ids):
            period_id = period_ids[0]
            cr.execute('UPDATE account_move_line SET period_id=%s ' \
                        'WHERE move_id =%s', (period_id, ids[0]))

            self.write(cr, uid, ids, {'period_id':period_id})

        return True




account_move()

