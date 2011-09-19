# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010 Vauxoo C.A. (http://openerp.com.ve/) All Rights Reserved.
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

import wizard
import osv
import pooler
from tools.translate import _
import tools
import time
import datetime
from mx.DateTime import *





class wiz_caja(wizard.interface):
    def _get_all(self, cr, uid, context, model):
        pool = pooler.get_pool(cr.dbname)
        obj = pool.get(model)
        ids = obj.search(cr, uid, [])
        if model != 'res.currency':
            res = [(o.id, o.name) for o in obj.browse(cr, uid, ids, context=context)]
            res.append((-1, ''))
        else:
            res = [(o.id, tools.ustr(o.name) + ' (' + tools.ustr(o.code) + ')') for o in obj.browse(cr, uid, ids, context=context)]    
        res.sort(key=lambda x: x[1])
        return res

    def _get_states(self, cr, uid, context):
        return self._get_all(cr, uid, context, 'res.country.state')

    def _get_countries(self, cr, uid, context):
        return self._get_all(cr, uid, context, 'res.country')

    def _get_currency(self, cr, uid, context):
        pool = pooler.get_pool(cr.dbname)
        user = pool.get('res.users').browse(cr, uid, [uid])[0]
        if user.company_id:
            return user.company_id.currency_id.id
        else:
            return pool.get('res.currency').search(cr, uid, [('rate','=',1.0)])[0]


    def _get_property(self, cr, uid, context, prop):
        pool = pooler.get_pool(cr.dbname)
        ccp_obj = pool.get('caj.chic.property')
        prp_id = False
        prop_ids = ccp_obj.search(cr, uid, [('name','=',prop)])
        if prop_ids:
            caj_cp = ccp_obj.browse(cr, uid, prop_ids[0])
            prop_str = "%s" % caj_cp.value
            lst_val = prop_str.split(',')
            prp_id = lst_val[1]
        return prp_id


    form_ini = '''<?xml version="1.0"?>
    <form string="Pago caja chica">
        <separator string="Proveedor Generico" colspan="4"/>
        <field name="partner_id" domain="[('gene','=',True)]" attrs="{'invisible':[('new_partner','=',True)]}"/>
        <newline/>
        <field name="new_partner"/>
        <field name="state" invisible="True"/>        
    </form>'''

    fields_ini = {
        'partner_id': {'string': 'Razon Social', 'type': 'many2one', 'relation': 'res.partner', 'required': False},
        'new_partner': {'string':'Agregar Proveedor', 'type':'boolean'},
        'state':{
            'string': 'Opcion', 
            'type': 'selection', 
            'selection':[('new', 'Nuevo Partner'),('old', 'Partner existente')],
            'default': lambda *a:'new'},        

    }
    
    wiz_form = '''<?xml version="1.0"?>
    <form string="Pago caja chica">
        <separator string="Proveedor Generico" colspan="4"/>
        <field name="partner_id" domain="[('gene','=',True)]" attrs="{'invisible':[('new_partner','=',True)]}"/>        
        <newline/>
        <field name="new_partner" attrs="{'invisible':[('state','=','old')]}" readonly='True'/>
        <field name="state" invisible="True"/>
        <newline/>
        <group attrs="{'invisible':[('new_partner','=',False)]}" colspan="4">
            <group attrs="{'invisible':[('new_partner','=',False)]}" colspan="4">
                <separator string="Datos del Proveedor" colspan="4"/>
                <field name="name" attrs="{'required':[('new_partner','=',True)], 'readonly':[('state','=','old')]}"/>
                <field name="vat" attrs="{'required':[('new_partner','=',True)], 'readonly':[('state','=','old')]}"/>
                <newline/>
                <field name="street" align="0.0" attrs="{'required':[('new_partner','=',True)], 'readonly':[('state','=','old')]}"/>
                <field name="street2" align="0.0" attrs="{'required':[('new_partner','=',True)], 'readonly':[('state','=','old')]}"/>
                <field name="zip" align="0.0" attrs="{'required':[('new_partner','=',True)], 'readonly':[('state','=','old')]}"/>
                <field name="city" align="0.0" attrs="{'required':[('new_partner','=',True)], 'readonly':[('state','=','old')]}"/>
                <field name="country_id" align="0.0" attrs="{'required':[('new_partner','=',True)], 'readonly':[('state','=','old')]}"/>
                <field name="state_id" align="0.0" attrs="{'required':[('new_partner','=',True)], 'readonly':[('state','=','old')]}"/>                
                <field name="email" align="0.0" attrs="{'readonly':[('state','=','old')]}"/>
                <field name="phone" align="0.0" attrs="{'required':[('new_partner','=',True)], 'readonly':[('state','=','old')]}"/>            
                <field name="dat_p_check" attrs="{'invisible':[('state','=','old')]}"/>
            </group>
            <group attrs="{'invisible':[('dat_p_check','=',False)]}" colspan="4">
                <separator string="Datos Contables Proveedor" colspan="4"/>
                <field name="part_check"/>
                <newline/>
                <field name="acc_payable" attrs="{'required':[('new_partner','=',True)], 'readonly':[('part_check','=',False)]}"/>
                <field name="acc_receivable" attrs="{'required':[('new_partner','=',True)], 'readonly':[('part_check','=',False)]}"/>
                <field name="dat_pc_check" />
            </group>
            <group attrs="{'invisible':[('dat_pc_check','=',False)]}" colspan="4">
                <separator string="Datos Contables Factura" colspan="4"/>
                <field name="inv_check"/>
                <newline/>
                <field name="date" attrs="{'required':[('new_partner','=',True)]}"/>
                <field name="journal_id" attrs="{'required':[('new_partner','=',True)], 'readonly':[('inv_check','=',False)]}"/>
                <field name="period_id" attrs="{'required':[('new_partner','=',True)], 'readonly':[('inv_check','=',False)]}"/>
                <field name="currency_id" attrs="{'required':[('new_partner','=',True)], 'readonly':[('inv_check','=',False)]}"/>
                <field name="description" width="64" attrs="{'required':[('new_partner','=',True)], 'readonly':[('inv_check','=',False)]}"/>
                <field name="reference" width="64" attrs="{'required':[('new_partner','=',True)], 'readonly':[('inv_check','=',False)]}"/>
                <newline/>
                <field name="dat_i_check"/>
            </group>            
        </group>
    </form>'''

    wiz_fields = {
        'partner_id': {'string': 'Razon Social', 'type': 'many2one', 'relation': 'res.partner', 'required': False},
        'new_partner': {'string':'Agregar Proveedor', 'type':'boolean'}, 
        'name': {'string': 'Proveedor', 'type': 'char', 'size': 128},
        'vat': {'string': 'RIF', 'type': 'char', 'size': 32},
        'dat_p_check': {'string':'Datos Correctos', 'type':'boolean'},
        'acc_receivable': {'string':'Cuenta a cobrar', 'type':'many2one', 'relation':'account.account', 'domain':[('type', '=', 'receivable')]},
        'acc_payable': {'string':'Cuenta a pagar', 'type':'many2one', 'relation':'account.account', 'domain':[('type', '=', 'payable')]},
        'part_check': {'string':'Editar', 'type':'boolean'},
        'dat_pc_check': {'string':'Datos Correctos', 'type':'boolean'},    
        'street':{'string': 'Urb/Sector', 'type': 'char', 'size': 128},
        'street2':{'string': 'Calle/Edif', 'type': 'char', 'size': 128},
        'zip':{'string': 'Codigo Postal', 'type': 'char', 'size': 24},
        'city':{'string': 'Ciudad', 'type': 'char', 'size': 128},
        'state_id':{'string': 'Estado', 'type': 'selection', 'selection':_get_states},
        'country_id':{'string': 'Pais', 'type': 'selection', 'selection':_get_countries},
        'email':{'string': 'E-mail', 'type': 'char', 'size': 64},
        'phone':{'string': 'Telefono', 'type': 'char', 'size': 64},
        'inv_check': {'string':'Editar', 'type':'boolean'},
        'journal_id': {'string': 'Diario', 'type': 'many2one', 'relation': 'account.journal', 'required': False},
        'period_id': {'string': 'Periodo', 'type': 'many2one', 'relation': 'account.period', 'required': False},
        'date': {'string':'Fecha factura','type':'date', 'required':'False'},
        'description':{'string':'Descripcion', 'type':'char', 'size': 64, 'required':False},
        'dat_i_check': {'string':'Datos Correctos', 'type':'boolean'},
        'currency_id': {'string': 'Moneda', 'type': 'many2one', 'relation': 'res.currency', 'required': False},
        'state':{
            'string': 'Opcion', 
            'type': 'selection', 
            'selection':[('new', 'Nuevo Partner'),('old', 'Partner existente')]
        },
        'reference':{'string': 'Nro. Factura', 'type': 'char', 'size': 64}

    }

    def _get_defaults(self, cr, uid, data, context):
        pool = pooler.get_pool(cr.dbname)
        data['form']['currency_id'] = self._get_currency(cr, uid, context)
        data['form']['journal_id'] = self._get_property(cr, uid, context,'property_diario_caja_chica')
        data['form']['acc_receivable'] = self._get_property(cr, uid, context,'property_acc_receivable_caja_chica')
        data['form']['acc_payable'] = self._get_property(cr, uid, context,'property_acc_payable_caja_chica')     
        comp = pool.get('account.voucher').browse(cr, uid, data['id'])
        data['form']['period_id'] = comp.period_id.id
        data['form']['date'] = comp.date
        return data['form']
   
   
    def _get_defaults2(self, cr, uid, data, context):
        return data['form']   

    def _check_opt(self, cr, uid, data, context):
        form = data['form']
        pool = pooler.get_pool(cr.dbname)
        partner_obj = pool.get('res.partner')
        addr_obj = pool.get('res.partner.address')
        partner_id = form.get('partner_id',False)
        
        if partner_id:
            partner = partner_obj.browse(cr, uid, partner_id)
            data['form']['acc_payable'] = partner.property_account_payable.id
            data['form']['acc_receivable'] = partner.property_account_receivable.id
            data['form']['name'] = partner.name
            data['form']['vat'] = partner.vat
            data['form']['state'] = 'old'
            data['form']['new_partner'] = True
            data['form']['dat_p_check'] = True
            address_contact_id, address_invoice_id = \
            partner_obj.address_get(cr, uid, [partner.id], ['contact', 'invoice']).values()            
            add_id = address_invoice_id or address_contact_id
            if add_id:
                address = addr_obj.browse(cr, uid, add_id)
                data['form']['street'] = address.street
                data['form']['street2'] = address.street2
                data['form']['zip'] = address.zip
                data['form']['city'] = address.city
                data['form']['country_id'] = address.country_id.id
                data['form']['state_id'] = address.state_id.id
                data['form']['email'] = address.email
                data['form']['phone'] = address.phone
                
        return data['form']
    

    def _data_check(self, cr, uid, data, context):
        form = data['form']
        if not (form['dat_p_check'] and form['dat_pc_check'] and form['dat_i_check']):
            raise wizard.except_wizard(_('Error Usuario'), _('Confirme, !Por favor confirme que los datos estan correctos!'))
                
        return {}


    def _data_save(self, cr, uid, data, context):
        form = data['form']
        created_inv = []
        pool = pooler.get_pool(cr.dbname)
        pid = form.get('partner_id',False)
        if not pid:
            pid = self._action_partner_create(cr, uid, data, context)
        inv_id = self._action_invoice_create(cr, uid, data, context, pid)
        created_inv.append(inv_id)
        #we get the view id
        mod_obj = pool.get('ir.model.data')
        act_obj = pool.get('ir.actions.act_window')
        xml_id = 'act_inv_caj_chi_tree8'
        #we get the model
        result = mod_obj._get_id(cr, uid, 'l10n_ve_caja_chica', xml_id)
        id = mod_obj.read(cr, uid, result, ['res_id'])['res_id']
        # we read the act window
        result = act_obj.read(cr, uid, id)
        result['res_id'] = created_inv        
        return result



    def _action_partner_create(self, cr, uid, data, context):
        pool = pooler.get_pool(cr.dbname)
        partner_obj = pool.get('res.partner')
        form = data['form']
        addr_lst = []             

        addr_vals = {
            'name': form['name'][:64],
            'street': form['street'],
            'street2': form['street2'],
            'zip': form['zip'],
            'city': form['city'],
            'country_id': form['country_id'],
            'state_id': form['state_id'],
            'email': form['email'],
            'phone': form['phone'],
            'type':'invoice'
            }
        addr_lst.append((0,0,addr_vals))        
        partner_vals = {
            'name': form['name'],
            'property_account_receivable': form['acc_receivable'],
            'property_account_payable': form['acc_payable'],
            'vat': form['vat'],
            'gene': True,            
            'adr_inv_ids': addr_lst,
            'supplier': True,
            'customer': False
            }        
        p_id = partner_obj.create(cr, uid, partner_vals)

        return p_id



    def _action_invoice_create(self, cr, uid, data, context, partner_id):
        pool = pooler.get_pool(cr.dbname)
        partner_obj = pool.get('res.partner')
        invoice_obj = pool.get('account.invoice')        
        form = data['form']
        
        if form['period_id'] :
            period = form['period_id']

        if form['date'] :
            date = form['date']
            if not form['period_id'] :
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
  
    

        payment_term_id = False
        fiscal_pos_id = False
        partner = partner_obj.browse(cr, uid, partner_id)
        account_id = form['acc_payable']
        address_contact_id, address_invoice_id = \
            partner_obj.address_get(cr, uid, [partner.id], ['contact', 'invoice']).values()


        comment = ''
        invoice_vals = {
            'name': form['description'],
            'origin': '',
            'type': 'in_invoice',
            'account_id': account_id,
            'partner_id': partner.id,
            'address_invoice_id': address_invoice_id,
            'address_contact_id': address_contact_id,
            'comment': comment,
            'payment_term': payment_term_id,                        
            'currency_id': form['currency_id'],
            'journal_id': form['journal_id'],
            'fiscal_position': fiscal_pos_id,
            'caj_chi': True,
            'date_invoice': form['date'],
            'period_id': form['period_id'],
            'reference': form['reference']
            }
            
        
        inv_id = invoice_obj.create(cr, uid, invoice_vals, {'type':'in_invoice'})

        return inv_id


    def _check(self, cr, uid, data, context):
        return 'getdata'

    
    states = {
        'init': {
            'actions': [_get_defaults],
            'result': {'type': 'form', 'arch':form_ini, 'fields':fields_ini, 'state':[('end','Cancel'),('checksel','Aceptar')]}
        },
        'checksel': {
            'actions': [_check_opt],
            'result': {'type':'choice','next_state':_check}
        },        
        'getdata': {
            'actions': [_get_defaults2],
            'result': {'type': 'form', 'arch':wiz_form, 'fields':wiz_fields, 'state':[('end','Cancel'),('change','Siguiente')]}
        },        
        'change': {
            'actions': [_data_check],
            'result': {'type': 'action', 'action':_data_save, 'state':'end'}
        },        
    }
wiz_caja('caja.chica')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

