# coding: utf-8
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############################################################################
#    Credits:
#    Coded by: javier@vauxoo.com
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
{
    "name": "Management withholdings Venezuelan laws",
    "version": "0.2",
    "author": "Vauxoo",
    "license": "AGPL-3",
    "website": "http://vauxoo.com",
    "category": 'Generic Modules/Accounting',
    "depends": ["l10n_ve_fiscal_requirements"],
    'data': [
        'security/withholding_security.xml',
        'security/ir.model.access.csv',
        'data/l10n_ve_withholding_data.xml',
        'view/l10n_ve_withholding_view.xml',
        # 'workflow/wh_action_server.xml', # Discontinued in v8 migration
    ],
    'test': [
        'test/account_supplier_invoice.yml',
        'test/wh_pay_invoice.yml',
    ],
    'installable': True,
}
