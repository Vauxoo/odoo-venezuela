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
import datetime

class sale_order_line(osv.osv):
    _inherit = "sale.order.line"

    _columns = {
        'concept_id': fields.many2one('islr.wh.concept','Concepto de Retencion',help="Concepto de Retencion asociado a esta Tasa",required=False),
    }

    #~ def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,uom=False, qty_uos=0, uos=False, name='', partner_id=False,lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False):
        #~ data = super(sale_order_line, self).product_id_change(cr, uid, ids, pricelist, product, qty,uom, qty_uos, uos, name, partner_id,lang, update_tax, date_order, packaging, fiscal_position, flag)
        #~ if not product:
            #~ return {'value': {'th_weight': 0, 'product_packaging': False,
                #~ 'product_uos_qty': qty}, 'domain': {'product_uom': [],
                   #~ 'product_uos': []}}
        #~ pro = self.pool.get('product.product').browse(cr, uid, product)
        #~ tipo_producto=pro.product_tmpl_id.type
        #~ if (tipo_producto=="product" or tipo_producto=="consu"):
            #~ concepto="p"    
        #~ elif tipo_producto=="service":
            #~ concepto="s"
        #~ data[data.keys()[2]]['concept_retention_iva'] = concepto
        #~ return data
#~ 
    #~ #metodo que agrega al original el concepto en las lineas de retencion de venta, es llamado por action_invoice_create() en sale.order
    #~ def invoice_line_create(self, cr, uid, ids, context={}):
        #~ create_ids = super(sale_order_line, self).invoice_line_create(cr, uid, ids, context)
        #~ invoice_line_brws = self.pool.get('account.invoice.line').browse(cr, uid, create_ids)
        #~ order_line_sale_brws = self.pool.get('sale.order.line').browse(cr, uid, ids)
        #~ 
        #~ for line_invoice in invoice_line_brws: #lineas de la factura
            #~ for line_sale in order_line_sale_brws: #lineas de la orden de venta
                #~ if line_sale.product_id==line_invoice.product_id: #si es la misma linea 
                    #~ self.pool.get('account.invoice.line').write(cr, uid, line_invoice.id, {'concept_retention_iva':line_sale.concept_retention_iva}) 
        #~ return create_ids    

sale_order_line()





