#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Humberto Arocha           <humberto@openerp.com.ve>
#              Maria Gabriela Quilarque  <gabrielaquilarque97@gmail.com>
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
from osv import osv
from osv import fields
from tools.translate import _
from tools import config
import time

class stock_picking(osv.osv):
    _inherit = 'stock.picking'
    '''
    Funcion que agrega a la invoice_lines el concepto de retencion a partir de una orden de compra u orden de venta, 
    con metodo de facturacion a partir de albaran
    '''
    def action_invoice_create(self, cursor, user, ids, journal_id=False,group=False, type='out_invoice', context=None):
        data = super(stock_picking, self).action_invoice_create(cursor, user, ids, journal_id, group, type, context)
        picking_id=data.keys()[0]
        invoice_id=data[picking_id]
        invoice_brw = self.pool.get('account.invoice').browse(cursor, user, invoice_id)
        picking_brw=self.browse(cursor, user, picking_id)
        
        if type == 'in_invoice' or type == 'in_refund': #ORDENES DE COMPRA
            for line_invoice in invoice_brw.invoice_line: #lineas de la factura
                for line_orden in picking_brw.purchase_id.order_line: #lineas de la orden de compra
                    if line_invoice.product_id==line_orden.product_id: #si es la misma linea
                        self.pool.get('account.invoice.line').write(cursor, user, line_invoice.id, {'concept_id':line_orden.concept_id.id})       
            return data 
        #~ ORDENES DE VENTA
        if type =='out_invoice' or type == 'out_refund':
            for line_invoice in invoice_brw.invoice_line: #lineas de la factura
                for line_orden in picking_brw.sale_id.order_line: #lineas de la orden de venta
                    if line_invoice.product_id==line_orden.product_id: #si es la misma linea
                        self.pool.get('account.invoice.line').write(cursor, user, line_invoice.id, {'concept_id':line_orden.concept_id.id})       
            return data 
    
stock_picking()




