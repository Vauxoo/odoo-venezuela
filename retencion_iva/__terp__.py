#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Maria Gabriela Quilarque  <gabriela@openerp.com.ve>
#              Javier Duran              <javier@nvauxoo.com>
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
	"name" : "Retenciones al Impuesto del Valor Agregado",
	"version" : "0.4",
	"author" : "Latinux & Netquatro",
	"category" : "Localisation/Venezuela",
	"website": "http://wiki.openerp.org.ve/",
	"description": '''
Administración de las retenciones aplicadas al Impuesto del Valor Agregado:
- Compras
- Ventas
- Verificar pestañas en Partners, Invoices y menús creados.
''',
	"depends" : ["base","account","stock"],
	"init_xml" : [],
	"demo_xml" : [], 
	"update_xml" : [
            "security/ir.model.access.csv",
            "retention_workflow.xml",
            "retention_view.xml", 
            "account_view.xml", 
            "account_invoice_view.xml",
            "partner_view.xml",
            "stock_view.xml", 
            "retention_wizard.xml",
            "retention_sequence.xml",
            "generate_txt_view.xml",
            "txt_wh_report.xml",
    ],
	"active": False,
	"installable": True
}
