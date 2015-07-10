# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############################################################################
#    Credits:
#    Coded by: Vauxoo C.A.
#    Planified by: Nhomar Hernandez
#    Audited by: Vauxoo C.A.
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
###############################################################################
import logging

from openerp.osv import fields, osv


class res_partner(osv.osv):
    _inherit = 'res.partner'
    logger = logging.getLogger('res.partner')

    _columns = {
        'consolidate_vat_wh': fields.boolean(
            'Fortnight Consolidate Wh. VAT',
            help='If set then the withholdings vat generate in a same'
            ' fornight will be grouped in one withholding receipt.'),
    }

    _defaults = {
        'wh_iva_rate': lambda *a: 100.0,
    }
