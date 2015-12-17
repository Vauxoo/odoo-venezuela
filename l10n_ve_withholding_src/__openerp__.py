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
    "name": "Compromiso de Responsabilidad Social",
    "version": "0.3",
    "author": "Vauxoo",
    "license": "AGPL-3",
    "category": "Generic Modules",
    "website": "http://wiki.openerp.org.ve/",
    "depends": [
        "base",
        "account",
        "l10n_ve_withholding",
    ],
    "test": [
        'test/aws_customer.yml',
        'test/aws_supplier.yml',
    ],
    "data": [
        'security/wh_src_security.xml',
        'security/ir.model.access.csv',
        'wizard/wizard_retention_view.xml',
        'view/wh_src_view.xml',
        'view/account_invoice_view.xml',
        'view/company_view.xml',
        'view/partner_view.xml',
        'workflow/l10n_ve_wh_src_wf.xml',
        'report/wh_src_report.xml',

    ],
    'demo': [
        "demo/demo_accounts.xml",
        "demo/demo_company.xml",
        "demo/demo_journals.xml",
    ],

    "installable": True,
}
