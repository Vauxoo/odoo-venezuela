# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Netquatro C.A. (http://openerp.netquatro.com/) All Rights Reserved.
#                    Javier Duran <javier.duran@netquatro.com>
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
<form string=" Modificacion del porcentaje de retencion">
    <field name="pret"/>
    <separator string="Esta seguro de cambiar el porcentaje de retencion ?" colspan="4"/>
    <field name="sure"/>
    <image name="gtk-dialog-info" colspan="2"/>
    <label string="Si actualiza los porcentajes de retencion, Usted debera verificar que todos los montos retenidos sean correctos ya que esto seran los utilizados para generar los movimientos contables" colspan="2"/>
</form>'''

_transaction_fields = {
    'pret': {'string':'Retencion Por 100', 'type':'float', 'required':True},
    'sure': {'string':'Esta Seguro?', 'type':'boolean'},
   
}

def _data_save(self, cr, uid, data, context):
    if not data['form']['sure']:
        raise wizard.except_wizard(_('Error Usuario'), _('Actualizar Porcentaje Retencion, !Por Favor seleccione la opcion!'))
    pool = pooler.get_pool(cr.dbname)
    inv_obj = pool.get('account.invoice')
    pxt = data['form']['pret']
    inv_lst = []

    for ret in pool.get('account.retention').browse(cr, uid, data['ids']):
        if ret.state != 'draft':
            raise wizard.except_wizard(_('Error Usuario'), _('Comprobante en estado Incorrecto, !Solo puede cambiar comprobantes en estado borrador!'))            
        if ret.retention_line:
            for line in ret.retention_line:
                inv_lst.append(line.invoice_id.id)

    inv_obj.write(cr, uid, inv_lst, {'p_ret':pxt}, context=context)
    inv_obj.button_compute(cr, uid, inv_lst)
    inv_obj.button_reset_taxes_ret(cr, uid, inv_lst)    

    return {}

class wiz_retencion(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {'type': 'form', 'arch':_transaction_form, 'fields':_transaction_fields, 'state':[('end','Cancel'),('change','Modificar')]}
        },
        'change': {
            'actions': [_data_save],
            'result': {'type': 'state', 'state':'end'}
        }
    }
wiz_retencion('account.retention.pxtaje')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

