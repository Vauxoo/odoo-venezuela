#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Vauxoo C.A.           
#    Planified by: Nhomar Hernandez
#    Audited by: Vauxoo C.A.
#############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
################################################################################
{
    "name" : "Fiscal requirements Venezuelan laws",
    "version" : "0.2",
    "author" : "Vauxoo",
    "website" : "http://vauxoo.com",
    "category": 'Generic Modules/Accounting',
    "description": """
 - Invoice Control Number.
 - Tax*except concept, necesary rule by Venezuelan Laws.
 - Required address invoice.
 - Unique billing address (invoice), necesary rule by Venezuelan Laws.
 - VAT verification for Venezuela rules.
 - If you have internet conexion you will be able of update your partner information from SENIAT Automatically on install wizard.
 - Damaged "Legal free forms" declaration.
 - Tax Units configuration.
 - When a partner is updated by using the SENIAT Update Button, its name changes to readonly to avoid manual changes.
 - Add field Parent in the invoice of customers and suppliers, for link the invoice  that generated debit or credit note.

  -  Add wizard for generate debit note from invoice and done accounting entry.
  -  Add wizard to assign, modify or unlink source invoice (parent invoice) to another one.
  -  Automatically unreconciles paid invoices when making a refund of type modify or cancel.
  -  Validate automatically the withholding of debit notes.
  -  Add a field on taxes configuration form for indicating the type of tax according to venezuelan laws
  
For damaged invoices (Free form formats), you must go to the company and, under the configuration section,
create the corresponding journal and account.
TODO : Include this on wizard configuration.

If you install this module with invoice data on the database, the concept_id will be 
Empty for all those invoices, so, when you try to modify them you have to add a value on
that field

This module should also install a menu item under the accounting configuration menu.

We now have a configuration wizard after this module install.
""",
    'init_xml': [
        'data/l10n_ut_data.xml',
        'data/seniat_url_data.xml',
    ],
    "depends" : ["base_vat", "account", "account_accountant","account_voucher"],
    'update_xml': [
        'installer_view.xml',
        'security/ir.model.access.csv',
        'wizard/wizard_nro_ctrl_view.xml',
        'view/account_invoice_view.xml',
        'view/res_company_view.xml',
        'view/l10n_ut_view.xml',
        'view/partner_view.xml',
        'view/account_inv_refund_nctrl_view.xml',
        'wizard/wizard_invoice_nro_ctrl_view.xml',
        'wizard/wizard_url_seniat_view.xml',
        'wizard/update_info_partner.xml',
        'wizard/account_invoice_debit_view.xml',
        'wizard/account_invoice_parent_view.xml',
        'wizard/search_info_partner_seniat.xml',
        'account_invoice_view.xml',
        'view/account_tax_view.xml',
    ],
    'demo_xml': [
        'demo/demo_partners.xml',
    ],
    'test': [],
    'installable': True,
    'active': False,
}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
