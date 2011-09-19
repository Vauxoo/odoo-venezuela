# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    This Modules was developed by Vauxoo, C.A. (<http://openerp.com.ve>)
#    Silver partner of Tiny.
#    author Nhomar Hernandez (nhomar@vauxoo.com) &
#           Javier Duran (<javier@vauxoo.com>)
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
#
##############################################################################

from osv import osv
from osv import fields
import time
#import pooler
#import urllib
import base64
#import tools
from tools import config
from tools.translate import _
#import wizard
#from tools.misc import currency
import csv

#class product_template(osv.osv):
#    '''
#    Relation with product
#    '''
#    _description = 'Inheriting Products templates'
#    _inherit = 'product.template'
#    #Do not touch _name it must be same as _inherit
#    _name = 'product.template'
#    _columns = {
#        'list_line_ids': fields.one2many('load.pricelist.lines', 'product_id', 'Partners'),
#    }
#product_template()


class load_pricelist(osv.osv):
    '''
Price agreements from suppliers
    '''
    _name = 'load.pricelist'
    _description = 'load_pricelist'
    _columns = {
        'name':fields.char('Name', size=64, required=False, readonly=False),
        'partner_id':fields.many2one('res.partner', 'Partner Supplier', required=False),
        'file_csv':fields.binary('CSV List', filters=None, help='Load in this order supplier,price,quantity,product_code'),
        'date': fields.date('Valid Since'),
        'price_ids':fields.one2many('load.pricelist.lines', 'pricelist_id', 'Price2Load', required=False),
        'state':fields.selection([
        ('draft','Draft'),
        ('loaded','Loaded'),
        ('review','Review'),
        ('toprocess','To Process'),
        ('done','Done'),
        ],'State', select=True, readonly=False),
    }
    _defaults = {
        'date': lambda *a: time.strftime('%Y-%m-%d'),
        'state': lambda *a: 'draft',
    }



    def product_price_list_import(self, cr, uid, id, file, filename, context={}):
        file2 = base64.decodestring(file)
        file2 = file2.split('\n')
        reader = csv.DictReader(file2, delimiter=',', quotechar='"')
#        print 'archivo: ',list(reader)
        return []

    def _get_csv(self, cr, uid, ids, context={}):
#        result=self.read(cr,uid,ids,['file_csv'])[-1]['file_csv']
        prod_obj = self.pool.get('product.product')
        vals = {}
        obj_pricelst = self.browse(cr, uid, ids)[0]
        if obj_pricelst.file_csv:
            file2 = base64.decodestring(obj_pricelst.file_csv)
            file2 = file2.split('\n')
            reader = csv.DictReader(file2, delimiter=',', quotechar='"')
#            print "Datos de entrada",list(reader)            
#            lst = []

            load_pl = self.price_line_get_item(cr, uid, list(reader), context)
            vals['price_ids'] = load_pl
            print 'lista verificada: ',load_pl
            for line in load_pl:
                res_ids = prod_obj.name_search(cr, uid, line['default_code'])
                print 'productoXXXX:',res_ids
                if not res_ids:
#                    raise osv.except_osv(_('Product Error!'), _('No product with this code  : %s ') % (line['default_code'],) )
                    print 'No product with this code'
                if len(res_ids) > 1:
#                    raise osv.except_osv(_('Product Error!'), _('Product code duplicate : %s ') % (line['default_code'],) )
                    print 'Product code duplicate'
                if len(res_ids) == 1:
                    line.update({'product_id':res_ids[0][0]})
                if not res_ids:
                    res_ids = prod_obj.name_search(cr, uid, line['prod_int_name'])
                    print 'productoNNNNAME:',res_ids
                    if not res_ids:
    #                    raise osv.except_osv(_('Product Error!'), _('No product with this name  : %s ') % (line['prod_int_name],) )
                        print 'No product with this name'
                    if len(res_ids) > 1:
    #                    raise osv.except_osv(_('Product Error!'), _('Product name duplicate : %s ') % (line['prod_int_name'],) )
                        print 'Product name duplicate'
                    if len(res_ids) == 1:
                        line.update({'product_id':res_ids[0][0]})



#            self.write(cr, uid, [obj_pricelst.id], vals, context=context)


#                lineDict = {}               
#                for fields in row.keys():
#                    check = getattr(self, '_check_' + fields, self._check_default)
#                    lineDict[fields] = (row[fields], check(cr, uid, ids, row[fields], context))

#                self.move_line_get_item(cr, uid, row, context)
#                lst.append(lineDict)
#            print 'lista',lst

            print 'lista despues: ',load_pl
                    
        else:
            reader = {}
            print "Datos de entrada",list(reader)
        return list(reader)


    def price_line_get_item(self, cr, uid, lines, context=None):
        pricelines_obj = self.pool.get('load.pricelist.lines')
        vals = {}
        for line in lines:
            for field in line.keys():
                if not pricelines_obj._columns.has_key(field):
                    raise osv.except_osv(_('Field Error!'), _('You have not Fields : %s ') % (field,) )

        return lines
#        return map(lambda x: (0,0,x), lines)



    def _check_default_code(self, cr, uid, ids, code, context):
        warnings = ''
        flag = False
        cr.execute("SELECT p.id FROM product_product p WHERE p.default_code = '%s'" % (code,))
        res = cr.fetchall()
        if not res:
            warnings = 'codigo no existe, producto nuevo'
        if len(res) > 1:
            warnings = 'codigo duplicado'
        if len(res)==1:
            return (res[0][0], True)
        return (warnings, flag)


    def _check_default(self, cr, uid, ids, code, context):
        flag = True
        warnings = 'valor de chequeo por defecto'
        return (warnings, flag)


    def action_create_data(self, cr, uid, ids, context={}):
        res = {}
        prod_obj = self.pool.get('product.product')
#        prod_supp_obj = self.pool.get('product.supplierinfo')
#        part_info_obj = self.pool.get('pricelist.partnerinfo')


        for load_plst in self.browse(cr, uid, ids):
            supp_id = load_plst.partner_id.id
            print 'arcivvvv: ',load_plst
            for line in load_plst.price_ids:
                seller = {}
                sql= "select id from product_supplierinfo where product_id=%s and name=%s" % (line.product_id.id, supp_id,)
                print 'lineaaaaaa: ',sql
                cr.execute("select id from product_supplierinfo where product_id=%s and name=%s", (line.product_id.id, supp_id,))
                record = cr.fetchone()
                if record:
                    supp_info_id = record[0]
                print 'suplier_info: ',record
                seller['pricelist_ids'] = self.partnerinfo_line_get_item(cr, uid, line)
                seller.update(self.supplierinfo_line_get_item(cr, uid, line))
                res['seller_ids'] = [(1,supp_info_id,seller)]
                print 'supplierinfo',res
                prod_obj.write(cr, uid, [line.product_id.id], res)
                
        return True

           
    def partnerinfo_line_get_item(self, cr, uid, plist):
        res = {
            'date': plist.pricelist_id.date,
            'min_quantity': plist.min_quantity,
            'price': plist.price
        }
        return [(0,0,res)]

    def supplierinfo_line_get_item(self, cr, uid, plist):
        res = {
            'name': plist.pricelist_id.partner_id.id,
            'product_code': plist.product_code,
            'product_name': plist.product_name,
            'qty': plist.qty

        }
        return res

 
load_pricelist()

class load_pricelist_lines(osv.osv):
    '''
Pricelist from supplier
This is recorded and imported before put on right place for control of changes
    '''
    _name = 'load.pricelist.lines'
    _description = 'Pricelist from supplier'
    _columns = {
        'name':fields.char("Element's Identifier", size=64, required=False, readonly=False),
        'product_id': fields.many2one('product.product', 'Product', ondelete='set null'),
        'default_code' : fields.char('Code', size=64, help="The internal code of the product"),
        'prod_int_name':fields.char('Product name', size=128, required=False, help="The internal name of the product"),
        'product_code': fields.char('Partner Product Code', size=64, help="Code of the product for this partner."),
        'product_name':fields.char('Product Sup Name', size=128, required=False, help="Name of the product for this partner."),
        'qty' : fields.float('Minimal Quantity', required=False, help="The minimal quantity to purchase for this supplier, expressed in the default unit of measure."),
        'min_quantity':fields.float('Quantity'),
        'price': fields.float('Cost by Quantity', digits=(16, int(config['price_accuracy'])),  help="The cost by quantity."),
        'list_price': fields.float('Sugested Price', digits=(16, int(config['price_accuracy'])), help="Base price for computing the customer price. Sometimes called the catalog price."),
        'pricelist_id':fields.many2one('load.pricelist', 'Load ID', required=False),
        'imported':fields.boolean('Imported', required=False),
        'note': fields.text('Notes'),
    }
load_pricelist_lines()

class res_partner_list(osv.osv):
    '''
    Adding relation with Partners
    '''
    _name = 'res.partner'
    _description = 'Partners'
    _inherit = 'res.partner'
    _columns = {
    'loadpl_ids':fields.one2many('load.pricelistl', 'partner_id', 'Partner', required=False),   
    }
res_partner_list()
