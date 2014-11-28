# -*- encoding: utf-8 -*-
###############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
#################Credits#######################################################
#    Coded by: Vauxoo C.A.
#    Planified by: Nhomar Hernandez
#    Audited by: Vauxoo C.A.
###############################################################################
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
from openerp.osv import fields, osv


class res_company(osv.osv):
    _inherit = "res.company"
    _columns = {
        "consolidate_vat_wh": fields.boolean("Fortnight Consolidate Wh. VAT",
            help="If it set then the withholdings vat generate in a same"
            " fornight will be grouped in one withholding receipt."),
        "allow_vat_wh_outdated": fields.boolean(
            "Allow outdated vat withholding",
            help="Enables confirm withholding vouchers for previous or future"
            " dates."),
        'propagate_invoice_date_to_vat_withholding': fields.boolean(
            'Propagate Invoice Date to Vat Withholding',
            help='Propagate Invoice Date to Vat Withholding. By default is in'
            ' False.'),
    }

    _defaults = {
        'consolidate_vat_wh': False,
        'propagate_invoice_date_to_vat_withholding': False,
    }
