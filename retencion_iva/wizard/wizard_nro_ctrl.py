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

_transaction_form = '''<?xml version="1.0"?>
<form string="Modificacion del nro. de control">
    <field name="nro_ctrl"/>
    <separator string="Esta seguro de cambiar el Nro Control ?" colspan="4"/>
    <field name="sure"/>
</form>'''

_transaction_fields = {
    'nro_ctrl': {'string':'Nro. Control', 'type':'char', 'size': 32, 'required':True},
    'sure': {'string':'Esta Seguro?', 'type':'boolean'},
   
}

def _set_nroctrl(self, cr, uid, data, context):
    if not data['form']['sure']:
        raise wizard.except_wizard(_('Error Usuario'), _('Actualizar Nro. Control, !Por Favor confirme seleccionando la opcion!'))
    pool = pooler.get_pool(cr.dbname)
    inv_obj = pool.get('account.invoice')
    n_ctrl = data['form']['nro_ctrl']

    invoice = inv_obj.browse(cr, uid, data['id'])
    if invoice.state == 'draft':
            raise wizard.except_wizard(_('Error Usuario'), _('Factura en estado Incorrecto, !Solo puede cambiar facturas en un estado diferente a borrador!'))            

    inv_obj.write(cr, uid, data['id'], {'nro_ctrl':n_ctrl}, context=context)
    return {}

class wiz_nroctrl(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {'type': 'form', 'arch':_transaction_form, 'fields':_transaction_fields, 'state':[('end','Cancel'),('change','Modificar')]}
        },
        'change': {
            'actions': [_set_nroctrl],
            'result': {'type': 'state', 'state':'end'}
        }
    }
wiz_nroctrl('account.retention.nroctrl')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

