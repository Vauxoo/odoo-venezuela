# coding: utf-8
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############################################################################
#    Credits:
#    Coded by:  Javier Duran              <javier@nvauxoo.com>
#               Maria Gabriela Quilarque  <gabriela@openerp.com.ve>
#               Nhomar Hernandez          <nhomar@vauxoo.com>
#               Humberto Arocha           <hbto@vauxoo.com>
#    Planified by: Nhomar Hernandez
#    Finance by: Helados Gilda, C.A. http://heladosgilda.com.ve
#    Audited by: Humberto Arocha humberto@openerp.com.ve
#############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
##############################################################################
{
    "name": "Management withholding vat based in the Venezuelan tax laws",
    "version": "1.1",
    "author": "Vauxoo",
    "license": "AGPL-3",
    "website": "http://vauxoo.com",
    "category": 'Generic Modules/Accounting',
    "depends": [
                "l10n_ve_withholding"
    ],
    'data': [
        'security/wh_iva_security.xml',
        'security/ir.model.access.csv',
        'report/withholding_vat_report.xml',
        'wizard/wizard_retention_view.xml',
        'wizard/wizard_wh_nro_view.xml',
        'view/generate_txt_view.xml',
        'view/account_invoice_view.xml',
        'view/account_view.xml',
        'view/partner_view.xml',
        'view/res_company_view.xml',
        'view/wh_iva_view.xml',
        "data/l10n_ve_withholding_data.xml",
        'report/txt_wh_report.xml',
        "workflow/wh_iva_workflow.xml",
        "workflow/wh_action_server.xml",
    ],
    'demo': [
        "demo/l10n_ve_withholding_iva_sequences_demo.xml",
        "demo/demo_partners.xml",
        "demo/l10n_ve_withholding_iva_demo.xml",
        "demo/demo_taxes.xml",
        "demo/demo_invoices.xml",
    ],

    'test': [
        # test/purchase_invoice_wh_iva.yml',
        # test/sale_invoice_wh_iva.yml',
        # test/sale_wh_iva.yml',
        # test/purchase_wh_iva.yml',
        # test/purchase_wh_iva_sequence.yml',
        # test/sale_wh_iva_sequence.yml',
        # test/purchase_wh_iva_txt.yml',
    ],
    'installable': True,
}
