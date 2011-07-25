#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Maria Gabriela Quilarque  <gabrielaquilarque97@gmail.com>
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
    "name" : "Delivery Note",
    "version" : "0.4",
    "author" : "Openerp Venezuela",
    "category" : "Generic Modules/Others",
    "website": "http://wiki.openerp.org.ve/",
    "description": '''
                    Generate Delivery Note at wizard from Outgoing Products
                    The Delivery Note is a document used to management delivery of goods or services to a client.
                    Also serves as the basis for quality inspections for delivery
                    
                    Generar Notas de Entrega a través de un wizard desde el Albaran de Salida.
                    La Nota de Entrega es un documento usado para gestionar la entrega demercancias o servicios a un cliente.
                    También sirve como base para efectuar inspecciones de calidad para entregas
                    ''',
    "depends" : ["base",
                 "stock",
                 "sale",
                 "invoice_so",
                 ],
    "init_xml" : [],
    "update_xml" : [
        "wizard/wz_invoice_delivery_note.xml",
        "wizard/wz_picking_delivery_note.xml",
        "wizard/wz_set_nro_ctrl.xml",
        "wizard/wz_generate_lines_txt_view.xml",
        "delivery_note_sequence.xml",
        "stock_view.xml",
        "delivery_note_view.xml",
        "sale_view.xml",
        "delivery_note_report.xml",
        "invoice.xml",
    ],
    "active": False,
    "installable": True
}
