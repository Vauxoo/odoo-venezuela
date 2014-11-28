# -*- encoding: utf-8 -*-
#############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############Credits#######################################################
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
#############################################################################
{
    "name": "Local Withholding Venezuelan laws",
    "version": "0.2",
    "author": "Vauxoo",
    "website": "http://vauxoo.com",
    "category": 'Generic Modules/Accounting',
    "description": """Management local withholding for Venezuelan tax laws
    """,
    'init_xml': [],
    "depends": ["l10n_ve_withholding"],
    'update_xml': [
        'security/wh_muni_security.xml',
        'security/ir.model.access.csv',
        'view/account_invoice_view.xml',
        'view/partner_view.xml',
        'view/wh_muni_view.xml',
        'data/wh_muni_sequence.xml',
        'report/wh_muni_report.xml',
        'workflow/l10n_ve_wh_muni_wf.xml',
    ],
    'data': [
        'data/wh_muni_sequence.xml',
    ],
    'demo_xml': [
        'demo/demo_accounts.xml',
        'demo/demo_partners.xml',
        'demo/demo_journal.xml',
    ],
    'test': [
        'test/awm_supplier.yml',
        'test/awm_customer.yml'
    ],
    'installable': True,
    'active': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
