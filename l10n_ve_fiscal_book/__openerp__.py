# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2011 Vauxoo C.A. (http://openerp.com.ve/) All Rights Reserved.
#                    Luis Escobar <luis@vauxoo.com>
#                    Tulio Ruiz <tulio@vauxoo.com>
#
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

{
    "name": "Fiscal Report For Venezuela",
    "version": "0.5",
    "depends": ["account", "l10n_ve_withholding_iva",
                "l10n_ve_fiscal_requirements", "l10n_ve_imex"],
    "author": "Vauxoo",
    "description": """
Fiscal Book
===============================================================================
Build all Fiscal Reports for Law in Venezuela.
Add 2 new columns because of:

Según Articulo 77 del Reglamento de la Ley del IVA No.5.363 del 12 de Julio de
1999.
Parágrafo Segundo: El registro de las operaciones contenidas en el reporte
global diario generado por las máquinas fiscales, se reflejarán en el Libro
de Ventas del mismo modo que se establece respecto de los comprobantes que
se emiten a no contibuyentes, indicando el número de registro de la máquina.

.. note::
    * *El libro de ventas no contempla la sección de Ventas por cuenta de
       Terceros.*
""",
    "website": "http://openerp.com.ve",
    "category": "Generic Modules/Accounting",
    "init_xml": [
    ],
    "demo_xml": [
        "demo/book_base_demo.xml",
        "demo/sale_book_demo.xml",
        "demo/purchase_book_demo.xml",
    ],
    "update_xml": [
        "wizard/fiscal_book_wizard_view.xml",
        "view/adjustment_book.xml",
        "view/fiscal_book.xml",
        "report/fiscal_book_report.xml",
        "workflow/fb_workflow.xml",
        "security/fiscal_book_security.xml",
        "security/ir.model.access.csv",
        "wizard/change_invoice_sin_cred_view.xml",
        "view/account_invoice_view.xml",
    ],
    "test": [
        # 'test/purchase.yml',
        # 'test/sale.yml',
    ],
    "active": False,
    "installable": True,
}
