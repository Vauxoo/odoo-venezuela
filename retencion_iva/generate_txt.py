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

    #~ def _get_amount_total(self,cr,uid,ids,name,args,context=None):
        #~ res = {}
        #~ for txt in self.browse(cr,uid,ids,context):
            #~ res[txt.id]= 0.0
            #~ for doc in txt.voucher_ids:
                #~ for line in doc.retention_line:
                    #~ res[txt.id] += line.amount_base_ret
        #~ return res
#~ 
    #~ def _get_amount_total_base(self,cr,uid,ids,name,args,context=None):
        #~ res = {}
        #~ for voucher in self.browse(cr,uid,ids,context):
            #~ res[voucher.id]= 0.0
            #~ for doc in txt.voucher_ids:
                #~ for line in doc.retention_line:
                    #~ res[voucher.id] += line.total_tax_ret
        #~ return res

    _columns = {
        'company_id': fields.many2one('res.company', 'Compañía', required=True),
        'state': fields.selection([
            ('draft','Draft'),
            ('confirmed', 'Confirmed'),
            ('done','Done'),
            ('cancel','Cancelled')
            ],'Estado', select=True, readonly=True, help="Estado del Comprobante"),
        'fiscalyear_id': fields.many2one('account.fiscalyear', 'Año Fiscal', required=True),
        'period_id':fields.many2one('account.period','Periodo',required=True, domain="[('fiscalyear_id','=',fiscalyear_id)]"),
        'txt_ids':fields.one2many('txt.iva.line','txt_id',help='Lineas del archivo txt exigido por el SENIAT, para retención del IVA')
        #~ 'amount_total_ret':fields.function(_get_amount_total,method=True, digits=(16, 2), readonly=True, string=' Total Monto de Retencion', help="Monto Total Retenido"),
        #~ 'amount_total_base':fields.function(_get_amount_total_base,method=True, digits=(16, 2), readonly=True, string='Total Base Imponible', help="Total de la Base Imponible"),
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
        
        print 'PERIODO ID',txt_brw.period_id.id
        
        voucher_ids = voucher_obj.search(cr,uid,[('period_id','=',txt_brw.period_id.id)])
        
        for voucher in voucher_obj.browse(cr,uid,voucher_ids):
            
            for voucher_lines in voucher.retention_line:
            
                txt_iva_obj.create(cr,uid,
                {'partner_id':voucher.partner_id.id,
                'voucher_id':voucher.id,
                'invoice_id':voucher_lines.invoice_id.id,
                'txt_id': txt_brw.id,
                })
            
            
            print 'NUMERO DE VOUCHER', voucher.number
        
        
        
        return True


    #~ def action_done(self, cr, uid, ids, context={}):
        #~ root = self._xml(cr,uid,ids)
        #~ self._write_attachment(cr,uid,ids,root,context)
        #~ self.write(cr, uid, ids, {'state':'done'})
        #~ return True
#~ 
    #~ def _write_attachment(self, cr,uid,ids,root,context):
        #~ '''
        #~ Codificar el xml, para guardarlo en la bd y poder verlo en el cliente como attachment
        #~ '''
        #~ fecha = time.strftime('%Y_%m_%d')
        #~ name = 'ISLR_' + fecha +'.'+ 'xml'
        #~ self.pool.get('ir.attachment').create(cr, uid, {
            #~ 'name': name,
            #~ 'datas': base64.encodestring(root),
            #~ 'datas_fname': name,
            #~ 'res_model': 'islr.xml.wh.doc',
            #~ 'res_id': ids[0],
            #~ }, context=context
        #~ )
        #~ cr.commit()

#~ 
    #~ def indent(self,elem, level=0):
        #~ i = "\n" + level*"  "
        #~ if len(elem):
            #~ if not elem.text or not elem.text.strip():
                #~ elem.text = i + "  "
            #~ if not elem.tail or not elem.tail.strip():
                #~ elem.tail = i
            #~ for elem in elem:
                #~ self.indent(elem, level+1)
            #~ if not elem.tail or not elem.tail.strip():
                #~ elem.tail = i
        #~ else:
            #~ if level and (not elem.tail or not elem.tail.strip()):
                #~ elem.tail = i
#~ 

    #~ def _xml(self, cr,uid,ids):
        #~ root = ''
        #~ for id in ids:
            #~ wh_brw = self.browse(cr,uid,id)
            #~ 
            #~ period = wh_brw.period_id.name.split('/')
            #~ period2 = period[1]+period[0]
#~ 
            #~ root = Element("RelacionRetencionesISLR")
            #~ root.attrib['RifAgente'] = wh_brw.company_id.partner_id.vat[2:]
            #~ root.attrib['Periodo'] = period2.strip()
            #~ for line in wh_brw.xml_ids:
                #~ detalle = SubElement(root,"DetalleRetencion")
                #~ SubElement(detalle, "RifRetenido").text = line.partner_vat
                #~ SubElement(detalle, "NumeroFactura").text = line.invoice_number
                #~ SubElement(detalle, "NumeroControl").text = line.control_number
                #~ SubElement(detalle, "CodigoConcepto").text = line.concept_code
                #~ SubElement(detalle, "MontoOperacion").text = str(line.base)
                #~ SubElement(detalle, "PorcentajeRetencion").text = str(line.porcent_rete)
        #~ ElementTree(root).write("/home/gabriela/openerp/Gabriela/5.0/Helados Gilda/islr_withholding/xml.xml")
        #~ self.indent(root)
        #~ return tostring(root,encoding="ISO-8859-1")
#~ .
txt_iva()


class txt_iva_line(osv.osv):
    _name = "txt.iva.line"
    
    _columns = {
        'partner_id':fields.many2one('res.partner','Comprador/Vendedor',help="Persona jurídica ó natural que genera la Factura, Nota de Crédito, Nota de Débito o Certificación (vendedor)"),
        'invoice_id':fields.many2one('account.invoice','Factura/ND/NC',help="Fecha de la factura, Nota de Crédito, Nota de Débito o Certificación, Declaración de Importación"),
        'voucher_id':fields.many2one('account.retention','Comprobante de Retencion IVA',help="Comprobante de Retencion de Impuesto al Valor Agregado (IVA)"),
        'txt_id':fields.many2one('txt.iva','Documento-Generar txt IVA'),
    }
    _rec_name = 'partner_id'
 
txt_iva_line()







