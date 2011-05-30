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

class wz_invoice_delivery_note(osv.osv_memory):

    def _get_type(self, cr, uid, context=None):
        delivery_obj = self.pool.get('delivery.note')
        delivery_note_ids=context["active_ids"]
        deliverys = delivery_obj.browse(cr, uid, delivery_note_ids, context=context)
        
        for delivery in deliverys:
            if delivery.invoice_state == 'invoiced':
                raise osv.except_osv(_('UserError'), _('Invoice is already created.'))
            if delivery.invoice_state == 'none':
                raise osv.except_osv(_('UserError'), _('Invoice cannot be created from Delivery Note.'))
            if delivery.state == 'draft':
                raise osv.except_osv(_('UserError'), _('Can not create the invoice status draft.'))
            if delivery.state == 'cancel':
                raise osv.except_osv(_('UserError'), _('Can not create the invoice status cancel.'))
        return False

    _name = "wz.invoice.delivery.note"
    _columns = {
        'journal_id': fields.many2one('account.journal','Destination Journal',required=True),
        'group': fields.boolean('Group by partner'),
        'type': fields.selection([('out_invoice', 'Customer Invoice'),
                ('in_invoice', 'Supplier Invoice'),
                ('out_refund', 'Customer Refund'),
                ('in_refund', 'Supplier Refund'),], 'Type',select=True, required=True,readonly=True),
    }
    _defaults = {
        'journal_id': _get_type,
        'type': lambda *a: 'out_invoice',
    }

    def new_open_window(self,cr,uid,ids,list_ids,xml_id,module,context=None):
        '''
        Generate new window at view form or tree
        '''
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
        result = mod_obj._get_id(cr, uid, module, xml_id) 
        id = mod_obj.read(cr, uid, result, ['res_id'])['res_id']
        result = act_obj.read(cr, uid, id)
        result['res_id'] = list_ids
        return result

    def _create_invoice(self, cr, uid, ids,context=None):
        delivery_note_id=context["active_ids"] 
        wizard_brw = self.browse(cr, uid, ids[0])
        delivery_obj = self.pool.get('delivery.note')
        wizard_deli_obj = self.pool.get('wz.picking.delivery.note')
        
        res = delivery_obj.action_invoice_create(cr, uid, delivery_note_id,
                journal_id=wizard_brw.journal_id.id, group=wizard_brw.group,
                type=wizard_brw.type, context=context)
        invoice_ids = res.values()

        if not invoice_ids:
            raise osv.except_osv(_('Error'), _('Invoice is not created'))
        else:
            if wizard_brw.type == 'out_invoice':
                xml_id = 'action_invoice_tree5'
                
            #~ return self.new_open_window(cr,uid,ids,lista de ids a mostrar en la nueva ventana,vista a mostrar,modulo donde se encuentra la vista)
            return wizard_deli_obj.new_open_window(cr,uid,ids,invoice_ids,xml_id,'account')

wz_invoice_delivery_note()



