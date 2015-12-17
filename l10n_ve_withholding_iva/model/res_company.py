# coding: utf-8
###############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############################################################################
#    Credits:
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
from openerp import models, fields


class ResCompany(models.Model):
    _inherit = "res.company"

    consolidate_vat_wh = fields.Boolean(
        string="Fortnight Consolidate Wh. VAT", default=False,
        help="If it set then the withholdings vat generate in a same"
        " fornight will be grouped in one withholding receipt.")
    allow_vat_wh_outdated = fields.Boolean(
        string="Allow outdated vat withholding",
        help="Enables confirm withholding vouchers for previous or future"
        " dates.")
    propagate_invoice_date_to_vat_withholding = fields.Boolean(
        string='Propagate Invoice Date to Vat Withholding', default=False,
        help='Propagate Invoice Date to Vat Withholding. By default is in'
        ' False.')
