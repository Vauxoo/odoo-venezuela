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

import wizard
import osv
import pooler
from tools.translate import _
from tools.misc import UpdateableStr

FORM = UpdateableStr()

_transaction_form = '''<?xml version="1.0"?>
<form string="Factura Original">
    <field name="parent_id"  domain="[('partner_id', '=', %s)]" required="%s"/>
    <separator string="Esta seguro que es la factura original ?" colspan="4"/>
    <field name="sure"/>
</form>'''

_transaction_fields = {
    'parent_id': {'string': 'Factura Original', 'type': 'many2one', 'relation': 'account.invoice'},
    'sure': {'string':'Esta Seguro?', 'type':'boolean'},
   
}



_fields_ini = {
    'partner_id': {'string': 'Razon Social', 'type': 'many2one', 'relation': 'res.partner', 'required': False},
    'type':{
        'string': 'Tipo Documento', 
        'type': 'selection', 
        'selection':[('blank', 'Asignar Factura Original'),('mod', 'Cambiar Factura Original'),('borr', 'Desvincular Factura Original')],
        'default': lambda *a:'blank'},        
}
_form_ini = '''<?xml version="1.0"?>
<form string="Notas Credito/Debito">
    <separator string="Este documento es?" colspan="4"/>
    <field name="partner_id" invisible="True"/>
    <newline/>    
    <field name="type"/>        
</form>'''


def _get_defaults(self, cr, uid, data, context):
    pool = pooler.get_pool(cr.dbname)
    inv_brw = pool.get('account.invoice').browse(cr, uid, data['id'])    
    data['form']['partner_id'] = inv_brw.partner_id.id

    return data['form']


def _set_domain(self, cr, uid, data, context):
    form = data['form']
    obli= True
    invis = False
    if form['type'] == 'borr':
        obli= False
        invis= True
    FORM.string = '''<?xml version="1.0"?>
<form string="Factura">
    <field name="parent_id"  domain="[('partner_id', '=', %s),('id', '!=', %s)]" required="%s" invisible="%s"/>
    <separator string="Esta seguro?" colspan="4"/>
    <field name="sure"/>
</form>''' % (form['partner_id'],data['id'],obli,invis)

    return {}

def _set_parent(self, cr, uid, data, context):
    if not data['form']['sure']:
        raise wizard.except_wizard(_('Error Usuario'), _('Asignar factura original, !Por Favor confirme seleccionando la opcion!'))
    if data['id'] == data['form']['parent_id']:
        raise wizard.except_wizard(_('Error Usuario'), _('Factura actual igual a la original, !La nota de credito o debito no pude ser la misma factura orginal, Por Favor seleccione otra factura original!'))        
    pool = pooler.get_pool(cr.dbname)
    inv_obj = pool.get('account.invoice')
    parent_id = data['form']['parent_id']
    inv_brw = inv_obj.browse(cr, uid, data['id'])
    refun2inv = {'out_refund': 'out_invoice', 'in_refund': 'in_invoice'}
    
    if inv_brw.state == 'draft':
            raise wizard.except_wizard(_('Error Usuario'), _('Factura en estado incorrecto, !Solo puede cambiar facturas en un estado diferente a borrador!'))

    if data['form']['type'] == 'borr':
        inv_obj.write(cr, uid, data['id'], {'parent_id':False}, context=context)
        return {}

    if data['form']['type'] == 'mod':
        inv_obj.write(cr, uid, data['id'], {'parent_id':False}, context=context)
        
    if inv_brw.parent_id and data['form']['type'] == 'blank':
            raise wizard.except_wizard(_('Error Usuario'), _('Nota Credito/Debito Asignada, !Esta nota ya fue asignada a una factura anteriormente!'))

    inv_parent_brw = inv_obj.browse(cr, uid, parent_id)
    if inv_parent_brw.parent_id:
            raise wizard.except_wizard(_('Error Usuario'), _('Factura original incorrecta, !La factura seleccionada no puede poseer una factura padre asignada!'))

    if inv_parent_brw.type in ('in_refund', 'out_refund'):
            raise wizard.except_wizard(_('Error Usuario'), _('Tipo factura original incorrecto, !La factura seleccionada no puede ser una devolucion!'))
            
    if inv_brw.type in ('in_refund', 'out_refund'):
        if refun2inv[inv_brw.type] != inv_parent_brw.type:
            raise wizard.except_wizard(_('Error Usuario'), _('Nota Credito, !si va a realizar una nota de credito, la factura seleccionada debe ser de tipo correcto!'))


    if inv_brw.type in ('in_invoice', 'out_invoice'):
        if inv_brw.type != inv_parent_brw.type:        
            raise wizard.except_wizard(_('Error Usuario'), _('Nota Debito, !si va a realizar una nota de debito, la factura seleccionada debe ser del mismo tipo de la factura actual!'))


    inv_obj.write(cr, uid, data['id'], {'parent_id':parent_id}, context=context)
    return {}

class wiz_nroctrl(wizard.interface):
    states = {
        'init': {
            'actions': [_get_defaults],
            'result': {'type': 'form', 'arch':_form_ini, 'fields':_fields_ini, 'state':[('end','Cancel'),('assign','Siguiente')]}
        },
        'assign': {
            'actions': [_set_domain],
            'result': {'type': 'form', 'arch':FORM, 'fields':_transaction_fields, 'state':[('end','Cancel'),('change','Asignar')]}
        },        
        'change': {
            'actions': [_set_parent],
            'result': {'type': 'state', 'state':'end'}
        }
    }
wiz_nroctrl('account.parent_invoice')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

