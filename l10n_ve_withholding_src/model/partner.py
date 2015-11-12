# coding: utf-8
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############################################################################
#    Credits:
#    Coded by: Humberto Arocha <hbto@vauxoo.com>
#    Planified by: Humberto Arocha / Nhomar Hernandez
#    Audited by: Vauxoo C.A.
#############################################################################
#    Copyright (c) 2009 Latinux Inc (http://www.latinux.com/) All Rights
#    Reserved.  This program is free software: you can redistribute it and/or
#    modify it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
###############################################################################

from openerp.addons import decimal_precision as dp
from openerp.osv import fields, osv


class ResPartner(osv.osv):
    _inherit = 'res.partner'
    _columns = {
        'wh_src_agent': fields.boolean(
            'SRC Wh. Agent',
            help="Indicate if the partner is a SRC withholding agent"),
        'wh_src_rate': fields.float(
            string='SRC Rate', digits_compute=dp.get_precision('Withhold'),
            default=0,
            help="SRC Withholding rate"),
    }
