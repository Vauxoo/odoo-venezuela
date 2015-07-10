# -*- encoding: utf-8 -*-
###############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (c) 2013 Vauxoo C.A. (http://openerp.com.ve/)
#    All Rights Reserved
###############################################################################
#    Credits:
#    Coded by:  Juan Marzquez (Tecvemar, c.a.) <jmarquez@tecvemar.com.ve>
#               Katherine Zaoral               <katherine.zaoral@vauxoo.com>
#    Planified by:
#                Juan Marquez                  <jmarquez@tecvemar.com.ve>
#                Humberto Arocha               <hbto@vauxoo.com>
#    Audited by: Humberto Arocha               <hbto@vauxoo.com>
###############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
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
    "name": "Imex",
    "version": "0.2",
    "depends": ["base",
                "account",
                "decimal_precision",
                "l10n_ve_fiscal_requirements"
                ],
    "author": "Tecvemar/Vauxoo",
    "description": """
Imex
===============================================================
This modules handles the openerp venezuela localization import
and export transactions. It specify the customs form model for
import declaration SENIAT Official FORM (Forma 99086).
""",
    "website": "http://vauxoo.com",
    "category": "Generic Modules/Accounting",
    "init_xml": [],
    "demo_xml": [],
    "update_xml": [
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
        'view/customs_form_config.xml',
        'view/customs_form.xml',
        'view/customs_form_menus.xml',
        'view/invoice.xml',
        'workflow/customs_form.xml',
    ],
    "active": False,
    "installable": True,
}
