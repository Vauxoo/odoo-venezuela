#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Javier Duran              <javier@vauxoo.com> 
#                          
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
from tools.translate import _
import time

class invoice_partner(osv.osv_memory):
    _name = "invoice.partner"
    _columns = {
        'partner_id':fields.many2one('res.partner','Partner',required=False, help="Select a partner to compute sale or purchase product"),
        'product_id':fields.many2one('product.product','Product',required=False, help="Select a product to compute sale or purchase product"),        
        'type': fields.selection([
            ('out_invoice','Customer Invoice'),
            ('in_invoice','Supplier Invoice'),
            ('out_refund','Customer Refund'),
            ('in_refund','Supplier Refund'),
            ('out_both','Customer Invoice and Refund'),
            ('in_both','Supplier Invoice and Refund')
            ],'Type', required=True),
        'date_from': fields.date('Start of period', required=True),
        'date_to': fields.date('End of period', required=True),
        'filter': fields.selection([('filter_no', 'No Filters'), ('filter_partner', 'Partners'), ('filter_product', 'Products')], "Filter by", required=True),        
    }
    _defaults= {
        'date_from': lambda *a: time.strftime('%Y-%m-01'),
        'date_to': lambda *a: time.strftime('%Y-%m-%d'),
        'filter': lambda *a: 'filter_no'
    }   


    def onchange_filter(self, cr, uid, ids, filter='filter_no', context=None):
        res = {}
        if filter == 'filter_no':
            res['value'] = {'partner_id': False, 'product_id': False, 'date_from': False ,'date_to': False}
        if filter == 'filter_product':
            res['value'] = {'product_id': False}
        if filter == 'filter_partner':
            res['value'] = {'partner_id': False}
        return res


    def _get_sql_base(self, cr, uid, form, context=None):
        """
        Return sql setence view base
        """
        
        sql = """
            create or replace view report_invoice as (
                select
                        l.id as id,
                        to_char(i.date_invoice, 'YYYY-MM-DD') as name,                
                        l.invoice_id as invoice_id,
                        l.product_id as product_id,
                        p.id as partner_id,
                        u.id as user_id,
                        case when i.type in ('in_refund', 'out_refund')
                            then
                                l.quantity*(-1)
                            else
                                l.quantity
                        end as quantity,                
                        case when i.type in ('in_refund', 'out_refund')
                            then
                                l.price_unit*(-1)
                            else
                                l.price_unit 
                        end as price_unit,
                        case when i.type in ('in_refund', 'out_refund')
                            then
                                l.price_subtotal*(-1)
                            else
                                l.price_subtotal 
                        end as price_subtotal,
                        l.uos_id as uom_id,
                        i.type as type
                    from account_invoice i
                        inner join res_partner p on (p.id=i.partner_id)
                        left join res_users u on (u.id=p.user_id)
                        right join account_invoice_line l on (i.id=l.invoice_id)
                        left join product_uom m on (m.id=l.uos_id)
                        left join product_template t on (t.id=l.product_id)
                        left join product_product d on (d.product_tmpl_id=l.product_id)
                    where l.quantity != 0 and i.state in ('open', 'paid') and i.date_invoice>='%s' and i.date_invoice<='%s'
                    )
                """% (form.date_from,form.date_to)

        return sql


    def _get_sql_associated(self, cr, uid, form, context=None):
        """
        Return sql setence view partner or product associated
        """
        
        type2lst = {
            'out_invoice': ['out_invoice'],
            'in_invoice':  ['in_invoice'],
            'out_refund':  ['out_refund'],
            'in_refund':   ['in_refund'],
            'out_both':    ['out_invoice', 'out_refund'],
            'in_both': ['in_invoice', 'in_refund'],
        }
        if form.filter == 'filter_product':
            cond = ' r.partner_id=%s' % form.partner_id.id
            claus = 'product_id'
            table = 'product'
        if form.filter == 'filter_partner':
            cond = ' r.product_id=%s' % form.product_id.id
            claus = 'partner_id'
            table = 'partner'
        if form.type:
            if len(type2lst[form.type]) == 1:
                where_str = "'%s'" % (type2lst[form.type][0])
                op = '='
            else:
                where_str = tuple(type2lst[form.type])
                op = 'in'
            cond += ' and r.type %s %s' % (op,where_str)

        sql = """
            create or replace view report_invoice_%s as (
            select
                r.%s as id,
                r.%s as %s,
                Sum(r.quantity) as quantity,
                Sum(r.price_subtotal) as price_subtotal
            from report_invoice r
                inner join product_template t on (t.id=r.product_id)
            where %s
            group by r.%s
            order by r.%s

            )
                """% (table,claus,claus,claus,cond,claus,claus)

        return sql



    def action_update_view(self, cr, uid, ids, context=None):
        """
        """
        if context is None:
            context = {}        
        form = self.browse(cr, uid, ids[0], context=context)
        if form.filter == 'filter_no':
            raise osv.except_osv(_('UserError'), _('You must choose a filter !'))            
        sql = self._get_sql_base(cr, uid, form, context)
        cr.execute(sql)
        sql2 = self._get_sql_associated(cr, uid, form, context)        
        cr.execute(sql2)
        if form.filter == 'filter_product':
            xml_id = 'action_invoice_prod_prod_tree'
        if form.filter == 'filter_partner':
            xml_id = 'action_invoice_partner_tree'
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
        if context is None:
            context = {}

        #we get the model
        result = mod_obj._get_id(cr, uid, 'report_invoice', xml_id)
        id = mod_obj.read(cr, uid, result, ['res_id'])['res_id']
        # we read the act window
        result = act_obj.read(cr, uid, id)

        return result

    def check_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        data = {}
        data['form'] = self.read(cr, uid, ids, [])[0]
        if data['form']['filter'] == 'filter_no':
            raise osv.except_osv(_('UserError'), _('You must choose a filter !'))

        form = self.browse(cr, uid, ids[0], context=context)
        sql = self._get_sql_base(cr, uid, form, context)
        cr.execute(sql)
        sql2 = self._get_sql_associated(cr, uid, form, context)        
        cr.execute(sql2)        
        return self._print_report(cr, uid, ids, data, context=context)
    
    def _print_report(self, cr, uid, ids, data, context=None):
        return {'type': 'ir.actions.report.xml', 'report_name': 'inv.prod.wiz.report', 'datas': data}    
invoice_partner()
