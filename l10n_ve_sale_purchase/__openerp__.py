# coding: utf-8
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############################################################################
#    Credits:
#    Coded by: Israel Fermín Montilla  <israel@openerp.com.ve>
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
    'name': 'ISLR Sale and Purchase Functionalities',
    'version': '0.3',
    'author': 'Vauxoo',
    "license": "AGPL-3",
    'category': '',
    'website': 'http://openerp.com',
    'depends': ['sale', 'purchase', 'stock', 'l10n_ve_withholding_islr'],
    'data': [
        'view/product_view.xml',
        'view/stock_view.xml',
        'view/purchase_view.xml',
        'view/sale_order_view.xml',
    ],
    'installable': True,
    'test': [
        #        'test/purchase_order.yml',
        #        'test/purchase_picking.yml',
        #        'test/purchase_validation.yml',
        #        'test/sale_order.yml',
        #        'test/sale_validation.yml',
    ],

}
