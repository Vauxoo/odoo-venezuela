# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    author.name@company.com
#
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
#
#############################################################################
from openerp.osv import osv


class update_info_partner(osv.osv_memory):
    _name = 'update.info.partner'

    def update_info(self, cr, uid, ids, context=None):
        """ OpenERP osv memory wizard : update_info_partner
        """
        context = context or {}
        seniat_url_obj = self.pool.get('seniat.url')
        cr.execute('''SELECT id FROM res_partner WHERE vat ilike 'VE%';''')
        record = cr.fetchall()
        pids = [item[0] for item in record]
        seniat_url_obj.connect_seniat(cr, uid, pids, context=context,
                                      all_rif=True)
        return{}


update_info_partner()
