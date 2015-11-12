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
from openerp import api
from openerp.osv import fields, osv


class ResPartner(osv.osv):
    _inherit = 'res.partner'

    _columns = {
        'islr_withholding_agent': fields.boolean(
            'Income Withholding Agent?', default=True,
            help="Check if the partner is an agent for income withholding"),
        'spn': fields.boolean(
            'Is it a society of natural persons?',
            help='Indicates whether refers to a society of natural persons'),
        'islr_exempt': fields.boolean(
            'Is it exempt from income withholding?',
            help='Whether the individual is exempt from income withholding'),
        'islr_wh_historical_data_ids': fields.one2many(
            'islr.wh.historical.data', 'partner_id', 'ISLR Historical Data',
            help='Values to be used when computing Rate 2'),
    }

    @api.multi
    def copy(self, default=None):
        """ Initialized id by duplicating
        """
        # NOTE: use ids argument instead of id for fix the pylint error W0622.
        # Redefining built-in 'id'
        if default is None:
            default = {}
        default = default.copy()
        default.update({
            'islr_withholding_agent': 1,
            'spn': 0,
            'islr_exempt': 0,
            'islr_wh_historical_data_ids': [],
        })

        return super(ResPartner, self).copy(default)
