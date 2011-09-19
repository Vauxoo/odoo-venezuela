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

from osv import osv, fields
import time
from tools import config
from tools.translate import _


class account_retencion_islr(osv.osv):
    _inherit = 'account.retencion.islr'


    def _get_period(self, cr, uid, context):
        periods = self.pool.get('account.period').find(cr, uid)
        if periods:
            return periods[0]
        else:
            return False
    _columns = {
        'invoice_line': fields.one2many('account.islr.invoice', 'retencion_id', 'Invoice Lines', readonly=True, states={'draft':[('readonly',False)]}),
        'rate_ids': fields.many2many('concepts.rates.islr', 'account_ret_islr_concep_rates_rel','retencion_id','rate_id', 'Concepts Rates'),
        'base': fields.float('Base', digits=(16,int(config['price_accuracy']))),
        'amount_ret': fields.float('Retention Amount', digits=(16,int(config['price_accuracy']))),

    } 

    _defaults = {
        'period_id': _get_period,
    }

    def button_reset_invoices(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        aii_obj = self.pool.get('account.islr.invoice')
        for id in ids:
            cr.execute("DELETE FROM account_islr_invoice WHERE retencion_id=%s", (id,))
            cr.execute("DELETE FROM account_retencion_islr_line WHERE retention_id=%s", (id,))
            partner = self.browse(cr, uid, id,context=context).partner_id
            if partner.lang:
                context.update({'lang': partner.lang})
#            for invoice in aii_obj.compute(cr, uid, id, context=context):
            invoice = aii_obj.compute(cr, uid, id, context=context)
            aii_obj.create(cr, uid, invoice)
         # Update the stored value (fields.function), so we write to trigger recompute
        self.pool.get('account.retencion.islr').write(cr, uid, ids, {'invoice_line':[]}, context=context)    
#        self.pool.get('account.invoice').write(cr, uid, ids, {}, context=context)
        return True

    def button_compute_ret(self, cr, uid, ids, date_ref=False, context={}):
        ut_obj = self.pool.get('l10n.ut')
        if not date_ref:
            date_ref = time.strftime('%Y-%m-%d')
        ret = self.browse(cr, uid, ids, context)[0]
        for line in ret.islr_line_ids:
            ut = ut_obj.compute(cr, uid, line.invoice_id.amount_untaxed)
            if len(ret.rate_ids) == 3:
                print '3: ',ut
            elif len(ret.rate_ids) == 1:

                print "1: ",ut

            else:
                print 'nada'
                


        return True


    def compute_line(self, cr, uid, ids, bs, context={}):
        ret = self.browse(cr, uid, ids, context)[0]
        if bs:
            res = bs*ret.rate_ids[0].rate*ret.rate_ids[0].base_imp

        return res




account_retencion_islr()




class account_islr_invoice(osv.osv):
    _name = "account.islr.invoice"
    _description = "Invoice total amount"
    _columns = {
        'retencion_id': fields.many2one('account.retencion.islr', 'Total Description', ondelete='cascade', select=True),
        'name': fields.char('Description', size=64),
        'base': fields.float('Base', digits=(16,int(config['price_accuracy']))),
        'amount': fields.float('Retention Amount', digits=(16,int(config['price_accuracy']))),
        'rate': fields.float('Tax Rate', digits=(16,int(config['price_accuracy']))),
    }

    def populate(self, cr, uid, ret_id, invoice_ids, context={}):
        res = []
        for inv_id in invoice_ids: 
            values = {
                'name': 'xxx',
                'retention_id': ret_id,
                'invoice_id': inv_id,
            }
            res.append((0,0,values))
        return res


    def compute(self, cr, uid, ret_id, context={}):
        tax_grouped = {}
        val={}
        ant = 0
        inv_obj = self.pool.get('account.invoice')
        ret_obj = self.pool.get('account.retencion.islr')
        rate_obj = self.pool.get('concepts.rates.islr')
        ret = self.pool.get('account.retencion.islr').browse(cr, uid, ret_id, context)
        cr.execute("select id from account_invoice where partner_id=%s and period_id=%s", (ret.partner_id.id,ret.period_id.id))
        inv_ids = map(lambda x: x[0], cr.fetchall())
        lst_ret = []
        rate_ids = []
        


        invvvv = inv_obj.search(cr, uid,
                [('partner_id', '=', ret.partner_id.id),
                    ('period_id', '=', ret.period_id.id)])

        print 'nhomar said ,era q esto funciona: ',invvvv


        val = {
            'base': 0.0,
            'amount': 0.0,
            'rate': 0.0
        }        
        val['retencion_id'] = ret.id
        val['name'] = ret.name
        for invoice in inv_obj.browse(cr, uid, inv_ids, context):
                for r in invoice.grp_conpt_ids:
                    if r.rate > ant:
                        ant = r.rate
                        grp_ids = invoice.grp_conpt_ids

                val['base'] += invoice.amount_untaxed
                if invoice.ret_islr:
                    val['amount'] += invoice.amount_untaxed
                    lst_ret.append(invoice.id)


        val['rate'] = ant        
        print 'grupo: ',grp_ids
        for r in grp_ids:
            rate_ids.append(r.id)
#        rate_ids = rate_obj.search(cr, uid,[
#                    ('group_id', '=', grp_id)
#                    ], 
#                    order='rate'
#        )
        print 'ratas: ',rate_ids
        inv_nret_ids = [elem for elem in inv_ids if elem not in lst_ret]
        ret_obj.write(cr, uid, [ret_id], {
            'islr_line_ids': self.populate(cr, uid, ret_id, inv_nret_ids, context),
            'rate_ids': [(6,0,rate_ids)],
            'base': val['base'],
            'amount_ret': val['amount'],
        })


        return val

account_islr_invoice()

