# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Vauxoo C.A. (http://openerp.com.ve/) All Rights Reserved.
#                    Javier Duran <javier@vauxoo.com>
# 
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

import time
from report import report_sxw

class sale_producto(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(sale_producto, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_sale': self._get_sale,
            'get_lines': self._get_lines
        })

    def _get_sale(self):
        prod_obj = self.pool.get('product.product')
        res = []
        self.cr.execute("""            
                select
                    min(l.id) as id,
                    to_char(s.date_order, 'YYYY-MM-01') as name,
                    s.state,
                    l.product_id,		    
                    sum(l.product_uom_qty*u.factor) as quantity,
                    count(*),
                    sum(l.product_uom_qty*l.price_unit) as price_total,
                    (sum(l.product_uom_qty*l.price_unit)/sum(l.product_uom_qty*u.factor))::decimal(16,2) as price_average,
                    t.name as pname,
                    p.default_code
                from sale_order s
                    right join sale_order_line l on (s.id=l.order_id)
                    left join product_uom u on (u.id=l.product_uom)
                    left join product_template t on (t.id=l.product_id)
                    left join product_product p on (p.product_tmpl_id=l.product_id)
                where l.product_uom_qty != 0
                group by l.product_id, to_char(s.date_order, 'YYYY-MM-01'),s.state,t.name,p.default_code
                order by t.name 
        """)


        for tp in self.cr.fetchall():
            res.append({
                        'id' : tp[0],
                        'name' : tp[1],
                        'state': tp[2],
                        'prod': '['+tp[9]+'] '+tp[8],
                        'cant': tp[4],
                        'linea': tp[5],
                        'ptot': tp[6],
                        'pprom': tp[7],
                        'p_id': tp[3],
                    }
            )


        return res


    def _get_lines(self,sl_group):
        print 'holaXXXXX: ',sl_group
        prod_obj = self.pool.get('product.product')
        result = []

        self.cr.execute(("""            
                select
                    l.id as id,
                    to_char(s.date_order, 'YYYY-MM-DD') as name,
                    s.state,
                    l.product_id,		    
                    l.product_uom_qty*u.factor as quantity,                    
                    l.product_uom_qty*l.price_unit as price_total,
                    ((l.product_uom_qty*l.price_unit)/(l.product_uom_qty*u.factor))::decimal(16,2) as price_average,
                    t.name as pname
                from sale_order s
                    right join sale_order_line l on (s.id=l.order_id)
                    left join product_uom u on (u.id=l.product_uom)
                    left join product_template t on (t.id=l.product_id)
                where l.product_uom_qty != 0
                and l.product_id = %s
                and s.state = '%s'
                order by name 
        """)%(sl_group['p_id'],sl_group['state'])
        )



        for tp in self.cr.fetchall():
            result.append({
                        'id' : tp[0],
                        'name' : tp[1],
                        'state': tp[2],
                        'prod': tp[7],
                        'cant': tp[4],
                        'ptot': tp[5],
                        'pprom': tp[6],
                        'p_id': tp[3],
                    }
            )



        print 'resZZZZZ:',result


        return result



report_sxw.report_sxw(
    'report.sale_product_l10n_ve',
    'account.invoice',
    'addons/l10n_ve_report_sale_ext/report/sale_product.rml',
    parser=sale_producto,
    header=False
)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
