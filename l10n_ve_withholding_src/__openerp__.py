# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Humberto Arocha <hbto@vauxoo.com>
#    Planified by: Humberto Arocha / Nhomar Hernandez
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
    "name" : "Compromiso de Responsabilidad Social",
    "version" : "0.2",
    "author" : "Vauxoo",
    "category" : "Generic Modules",
    "website": "http://wiki.openerp.org.ve/",
    "description": '''Administración de la Aplicacion del Compromiso de Responsabilidad Social
que se establece en el Reglamento de Ley de Contrataciones Públicas, (Gaceta Oficial Nº 39.181 del 19 de mayo de 2009) Decreto Nº 6.708.

**Artículo 34**

    Supuesto cuantitativo de procedencia.

    El Compromiso de Responsabilidad Social será requerido en todas las ofertas presentadas en las modalidades de selección de Contratistas
    previstas en la Ley de Contrataciones Públicas, así como; en los procedimientos excluidos de la aplicación de éstas, cuyo monto total,
    incluidos los tributos, superen las dos mil quinientas unidades tributarias (2.500 U.T).

**Artículo 35**

    Rango y normativa interna para el suministro de bienes, prestación de servicios o ejecución de obras, se establece para el Compromiso de Responsabilidad Social un valor mínimo del uno por ciento (1%) y un valor máximo del cinco por ciento (5%) del monto del contrato suscrito, el cual asumirán los Contratistas beneficiarios de la adjudicación del mismo. Los órganos o entes contratantes deberán fijar los porcentajes a ser aplicados a cada condición del Compromiso de Responsabilidad Social, así como, establecer categorías o escalas proporcionales con base en los montos de los contratos a ser suscritos.
''',
    "depends" : [
                "base",
                "account",
                "l10n_ve_withholding",
                ],
    "init_xml" : [],
    "demo_xml" : [
        'demo/demo_journals.xml',
        'demo/demo_accounts.xml',
        'demo/demo_company.xml',
    ],
    "test": [
        'test/aws_customer.yml',
        'test/aws_supplier.yml',
    ],
    "update_xml" : [
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
    "active": False,
    "installable": True,
}
