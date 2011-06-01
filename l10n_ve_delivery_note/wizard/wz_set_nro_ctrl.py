#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Maria Gabriela Quilarque  <gabrielaquilarque97@gmail.com>
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
import tools
from tools.translate import _
from tools import config

class wz_set_nro_ctrl(osv.osv_memory):

    _name = "wz.set.nro.ctrl"
    _columns = {
        'nro_ctrl': fields.char('Nro. Control',size= 32,required=True),
        'sure': fields.boolean('Esta Seguro?'),
    }

    def _set_nroctrl(self, cr, uid, ids, context=None):
        
        delivery_obj = self.pool.get('delivery.note')
        delivery_note_id=context["active_id"] 
        wizard_brw = self.browse(cr, uid, ids, context=None)
        wizard_deli_obj = self.pool.get('wz.picking.delivery.note')
        
        for wizard in wizard_brw:
            if not wizard.sure:
                raise osv.except_osv(_('Error'), _('Actualizar Nro. Control, !Por Favor confirme seleccionando la opcion!'))
            if wizard.nro_ctrl:
                delivery_obj.write(cr, uid, delivery_note_id, {'nro_ctrl':wizard.nro_ctrl}, context=context)
                
        obj_model = self.pool.get('ir.model.data')
        model_data_ids = obj_model.search(cr,uid,[('model','=','ir.ui.view'),('name','=','delivery_note_form')])
        resource_id = obj_model.read(cr, uid, model_data_ids, fields=['res_id'])[0]['res_id']
        print 'IDDD', delivery_note_id
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'id': delivery_note_id,
            'res_model': 'delivery.note',
            'views': [(resource_id,'form')],
            'type': 'ir.actions.act_window',
            'context': context,
        } 

wz_set_nro_ctrl()






