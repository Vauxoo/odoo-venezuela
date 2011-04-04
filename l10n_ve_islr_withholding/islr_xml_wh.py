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

class islr_xml_wh_doc(osv.osv):
    _name = "islr.xml.wh.doc"

    def _get_amount_total(self,cr,uid,ids,name,args,context=None):
        res = {}
        for xml in self.browse(cr,uid,ids,context):
            res[xml.id]= 0.0
            for line in xml.xml_ids:
                res[xml.id] += line.wh
        return res

    def _get_amount_total_base(self,cr,uid,ids,name,args,context=None):
        res = {}
        for xml in self.browse(cr,uid,ids,context):
            res[xml.id]= 0.0
            for line in xml.xml_ids:
                res[xml.id] += line.base
        return res

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
        'amount_total_ret':fields.function(_get_amount_total,method=True, digits=(16, 2), readonly=True, string=' Total Monto de Retencion', help="Monto Total Retenido"),
        'amount_total_base':fields.function(_get_amount_total_base,method=True, digits=(16, 2), readonly=True, string='Total Base Imponible', help="Total de la Base Imponible"),
        'xml_ids':fields.one2many('islr.xml.wh.line','islr_xml_wh_doc','Lineas del Documento XML', readonly=True ,domain="[('period_id','=',period_id), ('islr_xml_wh_doc','=',False)]",states={'draft':[('readonly',False)]}),
    }
    _rec_rame = 'company_id'

    _defaults = {
        'state': lambda *a: 'draft',
        'company_id': lambda self, cr, uid, context: \
                self.pool.get('res.users').browse(cr, uid, uid,
                    context=context).company_id.id,
    }

    def action_anular1(self, cr, uid, ids, context={}):
        return self.write(cr, uid, ids, {'state':'draft'})

    def action_confirm1(self, cr, uid, ids, context={}):
        return self.write(cr, uid, ids, {'state':'confirmed'})

    def action_done1(self, cr, uid, ids, context={}):
        root = self._xml(cr,uid,ids)
        self._write_attachment(cr,uid,ids,root,context)
        self.write(cr, uid, ids, {'state':'done'})
        return True

    def _write_attachment(self, cr,uid,ids,root,context):
        '''
        Codificar el xml, para guardarlo en la bd y poder verlo en el cliente como attachment
        '''
        fecha = time.strftime('%Y_%m_%d')
        name = 'ISLR_' + fecha +'.'+ 'xml'
        self.pool.get('ir.attachment').create(cr, uid, {
            'name': name,
            'datas': base64.encodestring(root),
            'datas_fname': name,
            'res_model': 'islr.xml.wh.doc',
            'res_id': ids[0],
            }, context=context
        )
        cr.commit()


    def indent(self,elem, level=0):
        i = "\n" + level*"  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for elem in elem:
                self.indent(elem, level+1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i


    def _xml(self, cr,uid,ids):
        root = ''
        for id in ids:
            wh_brw = self.browse(cr,uid,id)
            
            period = wh_brw.period_id.name.split('/')
            period2 = period[1]+period[0]

            root = Element("RelacionRetencionesISLR")
            root.attrib['RifAgente'] = wh_brw.company_id.partner_id.vat[2:]
            root.attrib['Periodo'] = period2.strip()
            for line in wh_brw.xml_ids:
                detalle = SubElement(root,"DetalleRetencion")
                SubElement(detalle, "RifRetenido").text = line.partner_vat
                SubElement(detalle, "NumeroFactura").text = line.invoice_number
                SubElement(detalle, "NumeroControl").text = line.control_number
                SubElement(detalle, "CodigoConcepto").text = line.concept_code
                SubElement(detalle, "MontoOperacion").text = str(line.base)
                SubElement(detalle, "PorcentajeRetencion").text = str(line.porcent_rete)
        #~ ElementTree(root).write("/home/gabriela/openerp/Gabriela/5.0/Helados Gilda/islr_withholding/xml.xml")
        self.indent(root)
        return tostring(root,encoding="ISO-8859-1")

islr_xml_wh_doc()


class islr_xml_wh_line(osv.osv):
    _name = "islr.xml.wh.line"
    
    _columns = {
        'concept_id': fields.many2one('islr.wh.concept','Concepto de Retencion',help="Concepto de Retencion asociado a esta Tasa",required=True, ondelete='cascade'),
        'period_id':fields.many2one('account.period','Periodo',required=True),
        'partner_vat': fields.char('RIF', size=10, required=True),
        'invoice_number': fields.char('Num. Factura',size=10,required=True),
        'control_number': fields.char('Num. Control',size=8,required=True),
        'concept_code': fields.char('Codigo de Concepto', size=10, required=True),
        'base': fields.float('Base Imponible', required=True),
        'porcent_rete': fields.float('% Retencion', required=True),
        'wh':fields.float('Monto de Retencion',required=True),
        'rate_id':fields.many2one('islr.rates', 'Tipo de Persona',domain="[('concept_id','=',concept_id)]",required=True),
        'islr_wh_doc_line_id':fields.many2one('islr.wh.doc.line','Documento de ISLR'),
        'account_invoice_line_id':fields.many2one('account.invoice.line','Id de Linea de Factura'),
        'islr_xml_wh_doc': fields.many2one('islr.xml.wh.doc','Documento ISLR XML'),
        'partner_id': fields.many2one('res.partner','Empresa',required=True),
        'sustract': fields.float('Sustraendo'),
    }
    _rec_name = 'partner_id'
    
    _defaults = {
        'invoice_number': lambda *a: '0',
        'control_number': lambda *a: '0',
    }

    def onchange_partner_vat(self, cr, uid, ids, partner_id, context={}):
        partner_brw = self.pool.get('res.partner').browse(cr,uid,partner_id)
        return {'value' : {'partner_vat':partner_brw.vat[2:]}} 
        
        
    def onchange_code_perc(self, cr, uid, ids, rate_id, context={}):
        rate_brw = self.pool.get('islr.rates').browse(cr,uid,rate_id)
        return {'value' : {'porcent_rete':rate_brw.wh_perc,'concept_code':rate_brw.code}} 

islr_xml_wh_line()


class account_invoice_line(osv.osv):
    _inherit = "account.invoice.line"

    _columns = {
        'wh_xml_id':fields.many2one('islr.xml.wh.line','Id XML'),
    }
    _defaults = {
        'wh_xml_id': lambda *a: 0,
    }
account_invoice_line()






