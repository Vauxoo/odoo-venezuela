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

class stock_inventory_line(osv.osv):
    _inherit = 'stock.inventory.line'
    '''

    '''
    def _get_cost(self,cr,uid,ids,name,args,context={}):
        res = {}
        for id in ids:
            res[id]=self.compute_cost(cr,uid,[id])
        return res
        
    _description = "Inventory"
    _columns = {
        'cost': fields.function(_get_cost,method=True,digits=(16, int(config['price_accuracy'])),string='Costo'),
    }


    def search_date_desc(self, cr, uid, ids, product_id, date):        
        cr.execute('SELECT price FROM product_historic_cost ' \
                    'WHERE product_id=%s AND name <= %s ORDER BY name desc LIMIT 1', (product_id, date))
        res = [x[0] for x in cr.fetchall()]
        if not res:
            res = 0.0
        else:
            res = res[0]
        return res
        
    def search_date_asc(self, cr, uid, ids, product_id, date):        
        cr.execute('SELECT price FROM product_historic_cost ' \
                    'WHERE product_id=%s AND name > %s ORDER BY name asc LIMIT 1', (product_id, date))
        res = [x[0] for x in cr.fetchall()]
        if not res:
            res = 0.0
        else:
            res = res[0]
        return res


    def compute_cost(self,cr,uid,ids,*args):
        prod_obj = self.pool.get('product.product')
        costo= 0.0
        inv_brw = self.browse(cr, uid, ids, context=None)[0]
        date  = inv_brw.inventory_id.date
        costo = self.search_date_desc(cr,uid,ids,inv_brw.product_id.id,date)
        if not costo:
            costo = self.search_date_asc(cr,uid,ids,inv_brw.product_id.id,date)
        costo = costo * inv_brw.product_qty * inv_brw.product_uom.factor_inv * inv_brw.product_id.uom_id.factor
        return costo

stock_inventory_line()




