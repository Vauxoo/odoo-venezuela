# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
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
import wizard
import pooler
import osv
import netsvc
import time
from tools.translate import _

sur_form = '''<?xml version="1.0"?>
<form string="Debit Note">
    <label string="Are you sure you want to debit this invoice ?" colspan="2"/>
    <newline />
    <field name="date" />
    <field name="period" />
    <field name="description" width="150" />
    <field name="comment"/>
</form>'''

sur_fields = {
    'date': {'string':'Operation date','type':'date', 'required':'False'},
    'period':{'string': 'Force period', 'type': 'many2one',
        'relation': 'account.period', 'required': False},
    'description':{'string':'Description', 'type':'char', 'size': 128, 'required':'False'},
    'comment': {'string': 'Comment', 'type':'char', 'required':True},
    }


class wiz_debit(wizard.interface):

    def _compute_refund(self, cr, uid, data, context):
        form = data['form']
        pool = pooler.get_pool(cr.dbname)
        created_inv = []
        date = False
        period = False
        description = False
        for inv in pool.get('account.invoice').browse(cr, uid, data['ids']):
            if inv.state in ['draft', 'proforma2', 'cancel']:
                raise wizard.except_wizard(_('Error !'), _('Can not make a debit note on a draft/proforma/cancel invoice.'))
            if inv.type not in ['in_invoice', 'out_invoice']:
                raise wizard.except_wizard(_('Error !'), _('Can not make a debit note on a refund invoice.'))

            if form['period'] :
                period = form['period']
            else:
                cr.execute("""SELECT id
                              from account_period where date('%s')
                              between date_start AND  date_stop  limit 1 """%(
                                time.strftime('%Y-%m-%d'),
                              ))
                res = cr.fetchone()
                if res:
                    period = res[0]

            if form['date'] :
                date = form['date']
                if not form['period'] :
                    cr.execute("select name from ir_model_fields where model='account.period' and name='company_id'")
                    result_query = cr.fetchone()
                    if result_query:
                        #in multi company mode
                        cr.execute("""SELECT id
                                      from account_period where date('%s')
                                      between date_start AND  date_stop and company_id = %s limit 1 """%(
                                      form['date'],
                                      pool.get('res.users').browse(cr,uid,uid).company_id.id
                                      ))
                    else:
                        #in mono company mode
                        cr.execute("""SELECT id
                                      from account_period where date('%s')
                                      between date_start AND  date_stop  limit 1 """%(
                                        form['date'],
                                      ))
                    res = cr.fetchone()
                    if res:
                        period = res[0]
            else:
                date = time.strftime('%Y-%m-%d')

            if form['description'] :
                description = form['description']
            else:
                description = inv.name
            
            #we create a new invoice that is the copy of the original

            invoice = pool.get('account.invoice').read(cr, uid, [inv.id],
                ['name', 'type', 'number', 'reference', 'date_invoice',
                    'comment', 'date_due', 'partner_id', 'address_contact_id',
                    'address_invoice_id', 'partner_insite','partner_contact',
                    'partner_ref', 'payment_term', 'account_id', 'currency_id',
                    'invoice_line', 'tax_line', 'journal_id','period_id'
                ]
            )
            invoice = invoice[0]
            del invoice['id']
            invoice_lines = []
            tax_lines = []
            nro_ref = invoice['reference']
            if inv.type == 'out_invoice':
                nro_ref = invoice['number']
            orig = 'FACT:' +(nro_ref or '') + '- DE FECHA:' + (invoice['date_invoice'] or '') + (' TOTAL:' + str(inv.amount_total) or '')

            invoice.update({
                'type': inv.type,
                'date_invoice': date,
                'state': 'draft',
                'number': False,
                'invoice_line': invoice_lines,
                'tax_line': tax_lines,
                'period_id': period,
                'name':description,
                'parent_id':inv.id,
                'origin': orig,
                'comment':form['comment']
                })

            #take the id part of the tuple returned for many2one fields
            for field in ('address_contact_id', 'address_invoice_id', 'partner_id',
                'account_id', 'currency_id', 'payment_term', 'journal_id'):
                invoice[field] = invoice[field] and invoice[field][0]

            # create the new invoice
            inv_id = pool.get('account.invoice').create(cr, uid, invoice,{})
            # we compute due date
            if inv.payment_term.id:
                data = pool.get('account.invoice').onchange_payment_term_date_invoice(cr, uid, [inv_id],inv.payment_term.id,date)
                if 'value' in data and data['value']:
                    pool.get('account.invoice').write(cr, uid, [inv_id],data['value'])
            created_inv.append(inv_id)

        #we get the view id
        mod_obj = pool.get('ir.model.data')
        act_obj = pool.get('ir.actions.act_window')
        if inv.type == 'out_invoice':
            xml_id = 'action_invoice_tree5'
        elif inv.type == 'in_invoice':
            xml_id = 'action_invoice_tree8'
        elif type == 'out_refund':
            xml_id = 'action_invoice_tree10'
        else:
            xml_id = 'action_invoice_tree12'
        #we get the model
        result = mod_obj._get_id(cr, uid, 'account', xml_id)
        id = mod_obj.read(cr, uid, result, ['res_id'])['res_id']
        # we read the act window
        result = act_obj.read(cr, uid, id)
        result['res_id'] = created_inv

        return result

    states = {
        'init': {
            'actions': [],
            'result': {'type':'form', 'arch':sur_form, 'fields':sur_fields, 'state':[('end','Cancel'),('refund','Debit Note')]}
        },
        'refund': {
            'actions': [],
            'result': {'type':'action', 'action':_compute_refund, 'state':'end'},
        },

    }
wiz_debit('account.invoice.debit_note')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

