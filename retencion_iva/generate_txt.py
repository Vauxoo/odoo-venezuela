#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Humberto Arocha           <humberto@openerp.com.ve>
#              Maria Gabriela Quilarque  <gabrielaquilarque97@gmail.com>
#              Javier Duran              <javier.duran@netquatro.com>             
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
from osv import osv
from osv import fields
from tools.translate import _
from tools import config
import time
import datetime
from xml.etree.ElementTree import Element, SubElement, ElementTree, tostring
import sys
import base64

class txt_iva(osv.osv):
    _name = "txt.iva"

    def _get_amount_total(self,cr,uid,ids,name,args,context=None):
        res = {}
        for txt in self.browse(cr,uid,ids,context):
            res[txt.id]= 0.0
            for txt_line in txt.txt_ids:
                res[txt.id] += txt_line.amount_withheld
                
        return res

    def _get_amount_total_base(self,cr,uid,ids,name,args,context=None):
        res = {}
        for txt in self.browse(cr,uid,ids,context):
            res[txt.id]= 0.0
            for txt_line in txt.txt_ids:
                res[txt.id] += txt_line.untaxed
                
        return res

    _columns = {
        'company_id': fields.many2one('res.company', 'Compañía', required=True, readonly=True,states={'draft':[('readonly',False)]}),
        'state': fields.selection([
            ('draft','Draft'),
            ('confirmed', 'Confirmed'),
            ('done','Done'),
            ('cancel','Cancelled')
            ],'Estado', select=True, readonly=True, help="Estado del Comprobante"),
        'fiscalyear_id': fields.many2one('account.fiscalyear', 'Año Fiscal', required=True,readonly=True,states={'draft':[('readonly',False)]}),
        'period_id':fields.many2one('account.period','Periodo',required=True,readonly=True,states={'draft':[('readonly',False)]}, domain="[('fiscalyear_id','=',fiscalyear_id)]"),
        'txt_ids':fields.one2many('txt.iva.line','txt_id',domain="[('txt_id','=',False)]", readonly=True,states={'draft':[('readonly',False)]}, help='Lineas del archivo txt exigido por el SENIAT, para retención del IVA'),
        'amount_total_ret':fields.function(_get_amount_total,method=True, digits=(16, 2), readonly=True, string=' Total Monto de Retencion', help="Monto Total Retenido"),
        'amount_total_base':fields.function(_get_amount_total_base,method=True, digits=(16, 2), readonly=True, string='Total Base Imponible', help="Total de la Base Imponible"),
    }
    _rec_rame = 'company_id'

    _defaults = {
        'state': lambda *a: 'draft',
        'company_id': lambda self, cr, uid, context: \
                self.pool.get('res.users').browse(cr, uid, uid,
                    context=context).company_id.id,
    }

    def action_anular(self, cr, uid, ids, context={}):
        return self.write(cr, uid, ids, {'state':'draft'})

    def action_confirm(self, cr, uid, ids, context={}):
        return self.write(cr, uid, ids, {'state':'confirmed'})

    def action_generate_lines_txt(self,cr,uid,ids,context={}):
        voucher_obj = self.pool.get('account.retention')
        txt_iva_obj = self.pool.get('txt.iva.line')
        
        txt_brw= self.browse(cr,uid,ids[0])
        txt_ids = txt_iva_obj.search(cr,uid,[('txt_id','=',txt_brw.id)])
        if txt_ids:
            txt_iva_obj.unlink(cr,uid,txt_ids)
        
        voucher_ids = voucher_obj.search(cr,uid,[('period_id','=',txt_brw.period_id.id),('state','=','done')])
        for voucher in voucher_obj.browse(cr,uid,voucher_ids):
            for voucher_lines in voucher.retention_line:
                txt_iva_obj.create(cr,uid,
                {'partner_id':voucher.partner_id.id,
                'voucher_id':voucher.id,
                'invoice_id':voucher_lines.invoice_id.id,
                'txt_id': txt_brw.id,
                'untaxed': voucher_lines.base_ret,
                'amount_withheld': voucher_lines.amount_tax_ret,
                })
        return True

    def action_done(self, cr, uid, ids, context={}):
        root = self.generate_txt(cr,uid,ids)
        self._write_attachment(cr,uid,ids,root,context)
        self.write(cr, uid, ids, {'state':'done'})
        return True

    def get_type_document(self,cr,uid,ids,txt_line,context):
        type= '03'
        if txt_line.invoice_id.type in ['out_invoice','in_invoice']:
            type= '01'
        elif txt_line.invoice_id.type in ['out_invoice','in_invoice'] and txt_line.invoice_id.parent_id:
            type= '02'
        return type

    def get_document_affected(self,cr,uid,txt_line,context):
        number=''
        if txt_line.invoice_id.type in ['in_invoice','in_refund'] and txt_line.invoice_id.parent_id:
            print 'entre aqui'
            number = txt_line.invoice_id.parent_id.reference
        elif txt_line.invoice_id.parent_id: 
            print 'entre aqui22'
            number = txt_line.invoice_id.parent_id.number
        print 'NUMBER', number
        return number

    def get_number(self,cr,uid,number,inv_type,long):
        if not number:
            return '0'
        else:
            result= ''
            if inv_type=='inv_ctrl':
                number= number[::-1]
            for i in number:
                if inv_type=='vou_number':
                    if i.isdigit():
                        if len(result)<long:
                            result = i + result
                        else:
                            break
                else:
                    if i.isalnum():
                        if len(result)<long:
                            result = i + result
                        else:
                            break
        return result[::-1].strip()

    def get_document_number(self,cr,uid,ids,txt_line,inv_type,context):
        number=0
        if txt_line.invoice_id.type in ['in_invoice','in_refund']:
            if not txt_line.invoice_id.reference:
                raise osv.except_osv(_('Invalid action !'),_("Imposible realizar archivo txt, debido a que la factura no tiene numero de referencia libre!"))
            else:
                number = self.get_number(cr,uid,txt_line.invoice_id.reference.strip(),inv_type,20)
        elif txt_line.invoice_id.number:
            number = self.get_number(cr,uid,txt_line.invoice_id.number.strip(),inv_type,20)
        return number

    def generate_txt(self, cr,uid,ids,context=None):
        txt_string = ''
        for txt in self.browse(cr,uid,ids,context):
            vat = txt.company_id.partner_id.vat[2:]
            for txt_line in txt.txt_ids:
                period = txt.period_id.name.split('/')
                period2 = period[1]+period[0]
                operation_type= 'C' if txt_line.invoice_id.type in ['out_invoice','out_refund'] else 'V'
                document_type = self.get_type_document(cr,uid,ids,txt_line,context)
                document_number=self.get_document_number(cr,uid,ids,txt_line,'inv_number',context)
                control_number= self.get_number(cr,uid,txt_line.invoice_id.nro_ctrl,'inv_ctrl',20)
                document_affected= self.get_document_affected(cr,uid,txt_line,context)
                voucher_number= self.get_number(cr,uid,txt_line.voucher_id.number,'vou_number',14)
                print 'control_number',control_number
                print 'AT VIRGEN', txt_line.invoice_id.amount_total
                
                at= str(txt_line.invoice_id.amount_total)
                print 'at', at
                print 'amount total',str(txt_line.invoice_id.amount_total)
                
                #~ txt_string= vat+' '+period2.strip()+' '\
                #~ +txt_line.invoice_id.date_invoice+' '+operation_type+' '+document_type+' '\
                #~ +document_number+' '+control_number+' '+str(txt_line.invoice_id.amount_total)+' '
                #~ +str(txt_line.invoice_id.amount_untaxed)+' '
                #~ +str(txt_line.amount_withheld)
                #~ +'\n'+txt_string
                
                txt_string= vat +' '+period2.strip()+' '\
                +txt_line.invoice_id.date_invoice+' '+operation_type+' '+document_type+' '\
                +document_number+' '+control_number+' '+str(txt_line.invoice_id.amount_total)+' '\
                +str(txt_line.invoice_id.amount_untaxed)+' '\
                +str(txt_line.amount_withheld)+' '+document_affected+' '\
                +'\n'+txt_string
                
                print 'TXT', txt_string
        return txt_string
        #~ return u'%s'%(txt_string.decode('utf-8'))
        
        
    def _write_attachment(self, cr,uid,ids,root,context):
        '''
        Codificar el txt, para guardarlo en la bd y poder verlo en el cliente como attachment
        '''
        fecha = time.strftime('%Y_%m_%d')
        name = 'IVA_' + fecha +'.'+ 'txt'
        self.pool.get('ir.attachment').create(cr, uid, {
            'name': name,
            'datas': base64.encodestring(root),
            'datas_fname': name,
            'res_model': 'txt.iva',
            'res_id': ids[0],
            }, context=context
        )
        cr.commit()
        
        
txt_iva()


class txt_iva_line(osv.osv):
    _name = "txt.iva.line"
    
    _columns = {
        'partner_id':fields.many2one('res.partner','Comprador/Vendedor',help="Persona jurídica ó natural que genera la Factura, Nota de Crédito, Nota de Débito o Certificación (vendedor)"),
        'invoice_id':fields.many2one('account.invoice','Factura/ND/NC',help="Fecha de la factura, Nota de Crédito, Nota de Débito o Certificación, Declaración de Importación"),
        'voucher_id':fields.many2one('account.retention','Comprobante de Retencion IVA',help="Comprobante de Retencion de Impuesto al Valor Agregado (IVA)"),
        'amount_withheld':fields.float('Amount Withheld'),
        'untaxed':fields.float('Untaxed'),
        'txt_id':fields.many2one('txt.iva','Documento-Generar txt IVA'),
    }
    _rec_name = 'partner_id'
 
txt_iva_line()







