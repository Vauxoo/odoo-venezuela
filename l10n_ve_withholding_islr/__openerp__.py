# coding: utf-8
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############################################################################
#    Credits:
#    Coded by: Humberto Arocha           <humberto@openerp.com.ve>
#              María Gabriela Quilarque  <gabriela@openerp.com.ve>
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

{
    "name": "Automatically Calculation Income Withholding",
    "version": "0.3",
    "author": "Vauxoo",
    "license": "AGPL-3",
    "category": "General",
    "website": "http://wiki.openerp.org.ve/",
    "depends": [
        "account",
        "l10n_ve_withholding",
        "l10n_ve_fiscal_requirements",
        "product",
        "report_webkit",
    ],
    'demo': [
        'demo/l10n_ve_islr_withholding_demo.xml',
    ],
    "data": [
        "view/installer.xml",
        "security/wh_islr_security.xml",
        "security/ir.model.access.csv",
        "data/l10n_ve_islr_withholding_data.xml",
        "data/retencion_islr_sequence.xml",
        "view/wh_islr_view.xml",
        "wizard/income_wh_change_concept.xml",
        "view/invoice_view.xml",
        "view/partner_view.xml",
        "view/res_company_view.xml",
        "report/islr_wh_report.xml",
        "view/islr_wh_doc_view.xml",
        "view/islr_wh_concept_view.xml",
        "view/product_view.xml",
        "view/islr_xml_wh.xml",
        "workflow/islr_wh_workflow.xml",
        "workflow/wh_action_server.xml",
        "wizard/partner_income_wh_print_view.xml",
        "wizard/employee_income_wh.xml",
        "data/partner_income_wh_report_data.xml",
        "report/partner_income_wh_report.xml",
    ],
    'test': [
        'test/supplier_wh_islr_invoice.yml',
        'test/supplier_wh_islr_doc.yml',
        'test/customer_wh_islr_doc.yml',
    ],
    "installable": True,
}
