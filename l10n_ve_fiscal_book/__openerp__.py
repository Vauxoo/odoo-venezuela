# coding: utf-8
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
    "license": "AGPL-3",
    "website": "http://openerp.com.ve",
    "category": "Generic Modules/Accounting",
    "data": [
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
    "installable": True,
}
