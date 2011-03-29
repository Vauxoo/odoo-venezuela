#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Humberto Arocha           <humberto@openerp.com.ve>
#              María Gabriela Quilarque  <gabrielaquilarque97@gmail.com>
#              Javier Duran              <javier.duran@netquatro.com>             
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
    "name" : "islr withholding concept",
    "version" : "0.4",
    "author" : "OpenERP Venezuela",
    "category" : "General",
    "website": "http://wiki.openerp.org.ve/",
    "description": '''
                    ISLR withholding automatically
                    
                    Pasos para la primera vez:
                    1.- Crear Conceptos de Retencion con sus tasas.
                    2.- Asignar a los servicios el concepto de retencion asociado.
                    3.- Asignar a la compania que retiene, si es Agente de Retencion o no. En la pestana ISLR dentro de partners.
                    4.- Crear el concepto de retencion para cuando no aplica retencion.
                    
                    Para el correcto funcionamiento:
                     1.- Los periodos deben estar definidos con el formato: 09/2011 (MM/YYYY)
                     2.- Crear las cuentas contables de islr y asignarselas al partner proveedor
                     3.- Crear el journal de tipo islr
                   ''',
    "depends" : [   "base",
                    "account",
                    "product",
                    "purchase",
                    "sale",
                    "retencion_iva",
                    "base_vat_ve",
                ],
    "init_xml" : [],
    "update_xml" : [
            "security/ir.model.access.csv",
            "retencion_islr_sequence.xml",
            "product_view.xml",
            "invoice_view.xml",
            "purchase_view.xml",
            "sale_order_view.xml",
            "partner_view.xml",
            "islr_wh_doc_view.xml",
            "islr_wh_concept_view.xml",
            "islr_xml_wh_report.xml",
            "islr_wh_report.xml",
            "islr_xml_wh.xml",
    ],
    "active": False,
    "installable": True
}
