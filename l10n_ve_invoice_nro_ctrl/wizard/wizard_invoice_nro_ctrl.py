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

class wizard_invoice_nro_ctrl(osv.osv_memory):

    _name = "wizard.invoice.nro.ctrl"
    _columns = {
        'nro_ctrl': fields.char('Control Number',size= 32,required=True,help="New control number of the invoice damaged."),
        'sure': fields.boolean('Are You Sure?'),
    }

    def action_invoice_create(self, cr, uid, ids, wizard_brw,invoice_id,context=None):

        invoice_line_obj = self.pool.get('account.invoice.line')
        invoice_obj = self.pool.get('account.invoice')
        inv_brw = invoice_obj.browse(cr,uid,invoice_id,context)
        invoice={}
        invoice_line ={}

        address_invoice_id = self.pool.get('res.partner.address').search(cr,uid,[('partner_id','=',inv_brw.company_id.partner_id.id),('type','=','invoice')])

        invoice.update({
            'company_id': inv_brw.company_id.id,
            'date_invoice': inv_brw.date_invoice,
            'number': inv_brw.number,
            'journal_id': inv_brw.company_id.journal_id.id,
            'partner_id': inv_brw.company_id.partner_id.id,
            'address_invoice_id' : address_invoice_id[0],
            'nro_ctrl': wizard_brw.nro_ctrl,
            'account_id': inv_brw.company_id.account_id.id,
            'currency_id': inv_brw.company_id.currency_id.id,
            'name': 'PAPELANULADO_NRO_CTRL_'+wizard_brw.nro_ctrl,
            'state':'paid',
            })
        inv_id = invoice_obj.create(cr, uid, invoice,{})
        tax_id=self.pool.get('account.invoice.tax').create(cr,uid,{'name':'SDCF',
                         'amount':0.00,
                         'tax_amount':0.00,
                         'base':0.00,
                         'account_id':inv_brw.company_id.account_id.id,
                         'invoice_id':inv_id},{})
        invoice_line.update({
            'name': 'PAPELANULADO_NRO_CTRL_'+wizard_brw.nro_ctrl,
            'account_id': inv_brw.company_id.account_id.id,
            'price_unit': 0,
            'quantity': 0,
            'invoice_id': inv_id,
            })
        for inv_line in inv_brw.invoice_line:
            if inv_line.concept_id or False:
                invoice_line.update({
                'concept_id':inv_line.concept_id.id,
                })
            break
        invoice_line_id = invoice_line_obj.create(cr, uid, invoice_line, {})
        return inv_id

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

    def create_invoice(self, cr, uid, ids, context=None):
        wizard_brw = self.browse(cr, uid, ids, context=None)
        wizard_deli_obj = self.pool.get('wz.picking.delivery.note')
        inv_id = context['active_id']
        invoice_obj = self.pool.get('account.invoice')
        inv_brw = invoice_obj.browse(cr,uid,inv_id,context)

        for wizard in wizard_brw:
            if not wizard.sure:
                raise osv.except_osv(_('Error'), _('!Por Favor confirme seleccionando la opcion!'))
            if inv_brw.company_id.journal_id and inv_brw.company_id.account_id:
                inv_id = self.action_invoice_create(cr,uid,ids,wizard,inv_id,context)
            else:
                raise osv.except_osv(_('Error'), _('Debe especificar la cuenta contable y el diario por defecto a utilizar para crear una factura dañada en el formulario de la compañia'))
        return self.new_open_window(cr,uid,ids,[inv_id],'action_invoice_tree1','account')

wizard_invoice_nro_ctrl()

