# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Latinux Inc (http://www.latinux.com/) All Rights Reserved.
#                    Javier Duran <jduran@corvus.com.ve>
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

from osv import fields, osv


class account_tax(osv.osv):
    _inherit = 'account.tax'
    _description = "Retencion de Impuesto"
    _columns = {
        'ret': fields.boolean('Retenible?', help="Indica si el impuesto es retenible"),
   }



    def _unit_compute(self, cr, uid, taxes, price_unit, address_id=None, product=None, partner=None, pret=0.0):
        taxes = self._applicable(cr, uid, taxes, price_unit, address_id, product, partner)

        res = []
        cur_price_unit=price_unit
        for tax in taxes:
            # we compute the amount for the current tax object and append it to the result

            data = {'id':tax.id,
                            'name':tax.name,
                            'account_collected_id':tax.account_collected_id.id,
                            'account_paid_id':tax.account_paid_id.id,
                            'base_code_id': tax.base_code_id.id,
                            'ref_base_code_id': tax.ref_base_code_id.id,
                            'sequence': tax.sequence,
                            'base_sign': tax.base_sign,
                            'tax_sign': tax.tax_sign,
                            'ref_base_sign': tax.ref_base_sign,
                            'ref_tax_sign': tax.ref_tax_sign,
                            'price_unit': cur_price_unit,
                            'tax_code_id': tax.tax_code_id.id,
                            'ref_tax_code_id': tax.ref_tax_code_id.id,
                            'ret':tax.ret,
            }
            res.append(data)

            if tax.type=='percent':
                amount = cur_price_unit * tax.amount
                data['amount'] = amount
                data['amount_ret'] = 0.0
                if pret:
                    if tax.ret:
                        amount_ret = cur_price_unit * tax.amount*(pret/100.0)
                        data['amount_ret'] = amount_ret
                    


            elif tax.type=='fixed':
                data['amount'] = tax.amount
            elif tax.type=='code':
                address = address_id and self.pool.get('res.partner.address').browse(cr, uid, address_id) or None
                localdict = {'price_unit':cur_price_unit, 'address':address, 'product':product, 'partner':partner}
                exec tax.python_compute in localdict
                amount = localdict['result']
                data['amount'] = amount
            elif tax.type=='balance':
                data['amount'] = cur_price_unit - reduce(lambda x,y: y.get('amount',0.0)+x, res, 0.0)
                data['balance'] = cur_price_unit

            amount2 = data['amount']
            if len(tax.child_ids):
                if tax.child_depend:
                    latest = res.pop()
                amount = amount2
                child_tax = self._unit_compute(cr, uid, tax.child_ids, amount, address_id, product, partner)
                res.extend(child_tax)
                if tax.child_depend:
                    for r in res:
                        for name in ('base','ref_base'):
                            if latest[name+'_code_id'] and latest[name+'_sign'] and not r[name+'_code_id']:
                                r[name+'_code_id'] = latest[name+'_code_id']
                                r[name+'_sign'] = latest[name+'_sign']
                                r['price_unit'] = latest['price_unit']
                                latest[name+'_code_id'] = False
                        for name in ('tax','ref_tax'):
                            if latest[name+'_code_id'] and latest[name+'_sign'] and not r[name+'_code_id']:
                                r[name+'_code_id'] = latest[name+'_code_id']
                                r[name+'_sign'] = latest[name+'_sign']
                                r['amount'] = data['amount']
                                latest[name+'_code_id'] = False
            if tax.include_base_amount:
                cur_price_unit+=amount2
        return res

    def compute(self, cr, uid, taxes, price_unit, quantity, address_id=None, product=None, partner=None, pret=0.0):

        """
        Compute tax values for given PRICE_UNIT, QUANTITY and a buyer/seller ADDRESS_ID.

        RETURN:
            [ tax ]
            tax = {'name':'', 'amount':0.0, 'account_collected_id':1, 'account_paid_id':2}
            one tax for each tax id in IDS and their childs
        """
        res = self._unit_compute(cr, uid, taxes, price_unit, address_id, product, partner, pret)
        total = 0.0
        for r in res:
            if r.get('balance',False):
                r['amount'] = round(r['balance'] * quantity, 2) - total
            else:
                r['amount'] = round(r['amount'] * quantity, 2)
                total += r['amount']
                r['amount_ret'] = round(r['amount_ret'] * quantity, 2)

        return res




account_tax()

class account_journal(osv.osv):
    _inherit = 'account.journal'
    _description = "Journal"
    _columns = {
        'type': fields.selection([('sale', 'Sale'), ('purchase', 'Purchase'), ('cash', 'Cash'), ('general', 'General'), ('situation', 'Situation'), ('retiva', 'Ret IVA'), ('retislrPurchase', 'Ret ISLR Purchase'), ('retislrSale', 'Ret ISLR Sale'), ('retmun', 'Ret Municipal')], 'Type', size=32, required=True),
    }

account_journal()

def _models_retencion_get(self, cr, uid, context={}):
    obj = self.pool.get('ir.model.fields')
    ids = obj.search(cr, uid, [('model','in',['account.retention', 'account.retencion.islr', 'account.retencion.munici'])])
    res = []
    done = {}
    for o in obj.browse(cr, uid, ids, context=context):
        if o.model_id.id not in done:
            res.append( [o.model_id.model, o.model_id.name])
            done[o.model_id.id] = True
    return res


class account_move_line(osv.osv):
    _inherit = 'account.move.line'
    _description = "Entry lines"

    def _document_get(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        model_lst = ['account.retention.line', 'account.retencion.islr.line', 'account.retencion.munici.line']
        obj = self.pool.get('ir.model.fields')
        for aml in self.browse(cr, uid, ids, context=context):
            res[aml.id] = ''
            for model in model_lst:
                record = False
                sql ='''                
                        select
                            l.retention_id as id
                        from %s l
                            inner join account_move m on (m.id=l.move_id)
                            inner join account_move_line u on (m.id=u.move_id)
                        where u.id=%s
                    ''' % (model.replace('.','_'),aml.id)

                cr.execute(sql)
                record = cr.fetchone()
                if record:
                    model_ids = obj.search(cr, uid, [('name','=','retention_id'),('model','=',model)])
                    model_field = obj.browse(cr, uid, model_ids, context=context)[0]
                    doc_str = "%s,%s" % (model_field.relation,record[0])
                    res[aml.id] = doc_str
                    continue

        return res

    _columns = {
        'res_id': fields.function(_document_get, method=True, string='Document', size=128,
            type='reference', selection=_models_retencion_get),
    }


account_move_line()

