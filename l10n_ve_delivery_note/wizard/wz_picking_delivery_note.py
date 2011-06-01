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
from osv import fields, osv
import tools
from tools.translate import _
from tools import config

class wz_picking_delivery_note(osv.osv_memory):
    _name = "wz.picking.delivery.note"

    def _get_taxes_invoice(self, cursor, user, move_line):
        '''Return taxes ids for the move line'''
        taxes = move_line.product_id.taxes_id

        if move_line.picking_id and move_line.picking_id.address_id and move_line.picking_id.address_id.partner_id:
            return self.pool.get('account.fiscal.position').map_tax(
                cursor,
                user,
                move_line.picking_id.address_id.partner_id.property_account_position,
                taxes
            )
        else:
            return map(lambda x: x.id, taxes)

    def new_open_window(self,cr,uid,ids,list_ids,xml_id,module,context=None):
        '''
        Generate new window at view form or tree
        '''
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
        result = mod_obj._get_id(cr, uid, module, xml_id) 
        id = mod_obj.read(cr, uid, result, ['res_id'])['res_id']
        result = act_obj.read(cr, uid, id)
        result['res_id'] = list_ids
        return result

    def _invoice_hook(self, cursor, user, picking, create_id):
        sale_obj = self.pool.get('sale.order')
        if picking.sale_id:
            sale_obj.write(cursor, user, [picking.sale_id.id], {
                'note_ids': [(4, create_id)],
                })
        return
    
    def create_lines_id(self,cr,uid,ids,stock_brw,create_id,delivery_obj,context=None):
        '''
        Create lines delivery note
        '''
        delivery_ids_obj = self.pool.get('delivery.note.line')
        
        for move_line in stock_brw.move_lines:
            if move_line.price_unit:
                price_unit = move_line.price_unit
            else:
                price_unit = move_line.product_id.list_price
            
            tax_ids = self._get_taxes_invoice(cr, uid, move_line)

            create_lines_id = delivery_ids_obj.create(cr, uid, {
            'name': move_line.name,
            'product_id': move_line.product_id.id,
            'note_id': create_id,
            'uos_id': move_line.product_uom.id,
            'price_unit': price_unit,
            'quantity': move_line.product_uos_qty or move_line.product_qty,
            'note_line_tax_id': [(6, 0, tax_ids)],
            }, context=None)
            
            delivery_obj.button_compute(cr, uid, [create_id], context=context)
            
            if stock_brw.sale_id:
                for line_orden in stock_brw.sale_id.order_line: #lineas de la orden de venta
                    if move_line.product_id==line_orden.product_id: #si es la misma linea
                        #~ delivery_ids_obj.write(cr, uid, create_lines_id, {'concept_id':line_orden.concept_id.id,
                                                                          #~ 'discount':line_orden.discount,})
                        delivery_ids_obj.write(cr, uid, create_lines_id, {'discount':line_orden.discount,})
        return create_lines_id

    def action_create_delivery_note(self, cr, uid, ids, context=None):
        '''
        Create delivery note from of stock picking
        '''
        if context is None:
            context = {}
        delivery_obj = self.pool.get('delivery.note')
        address_obj =self.pool.get('res.partner.address')
    
        picking_id=context["active_id"] 
        stock_obj = self.pool.get('stock.picking')
        stock_brw = stock_obj.browse(cr,uid,picking_id)
        
        partner_brw = stock_brw.address_id.partner_id
        context.update({'delivery_note':True})
        if partner_brw:
            list_invoice = address_obj.search(cr,uid,[('partner_id','=',partner_brw.id),('type','=','invoice')])
            list_contact = address_obj.search(cr,uid,[('partner_id','=',partner_brw.id),('type','=','contact')])
            create_id = delivery_obj.create(cr,uid, {
                    'partner_id': partner_brw.id,
                    'address_shipping_id': stock_brw.address_id.id,
                    'address_invoice_id': list_invoice[0],
                    'picking_id': picking_id,
                    'sale_id': stock_brw.sale_id.id,
                    'invoice_state':stock_brw.invoice_state,
                    'payment_term':partner_brw.property_payment_term.id,},context)
            self.create_lines_id(cr,uid,ids,stock_brw,create_id,delivery_obj,context)
            self._invoice_hook(cr, uid, stock_brw, create_id)
            stock_obj.write(cr, uid, [stock_brw.id], {
                'invoice_state': 'invoiced',
                }, context=context)
            
        return self.new_open_window(cr,uid,ids,[create_id],'action_wizard_delivery_note_form','l10n_ve_delivery_note')
        
wz_picking_delivery_note()






