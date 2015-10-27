# coding: utf-8
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############################################################################
#    Credits:
#    Coded by: Yanina Aular           <yanina.aular@vauxoo.com>
#    Planified by: Humberto Arocha
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

from openerp.osv import fields, osv


class ResCompany(osv.osv):
    _inherit = 'res.company'

    _columns = {
        'automatic_income_wh': fields.boolean(
            'Automatic Income Withhold',
            help='When True, Supplier Income Withholding will be check and '
                 'validate automatically'),
        'propagate_invoice_date_to_income_withholding': fields.boolean(
            'Propagate Invoice Date to Income Withholding',
            help='Propagate Invoice Date to Income Withholding. By default is'
                 ' in False.'),
    }

    defaults = {
        'automatic_income_wh': False,
        'propagate_invoice_date_to_income_withholding': False,
    }
