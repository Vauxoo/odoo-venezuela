#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Humberto Arocha           <humberto@openerp.com.ve>
#              Maria Gabriela Quilarque  <gabrielaquilarque97@gmail.com>
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

class account_invoice_line(osv.osv):
    '''
    Se agrega un campo donde se determina, si una linea ha sido retenida o no.
    '''
    _inherit = "account.invoice.line"
    _columns = {
        'apply_wh': fields.boolean('Retenido',help="Indica si una linea ha sido retenida o no, para ir acumulando el monto a retener el proximo mes, de acuerdo a las lineas que no han sido retenidas."),
        'concept_id': fields.many2one('islr.wh.concept','Concepto de Retencion',help="Concepto de Retencion asociado a esta Tasa",required=False),
    }
    _defaults = {
        'apply_wh': lambda *a: False,
    }

    def product_id_change(self, cr, uid, ids, product, uom=0, qty=0, name='', type='out_invoice', partner_id=False, fposition_id=False, price_unit=False, address_invoice_id=False, context=None):
        '''
        onchange para que aparezca el concepto de retencion asociado al producto de una vez en la linea de la factura
        '''
        data = super(account_invoice_line, self).product_id_change(cr, uid, ids, product, uom, qty, name, type, partner_id, fposition_id, price_unit, address_invoice_id, context)
        
        if product:
            pro = self.pool.get('product.product').browse(cr, uid, product, context=context)
            data[data.keys()[1]]['concept_id'] = pro.concept_id.id
        return data

account_invoice_line()


class account_invoice(osv.osv):

    _inherit = 'account.invoice'

    _columns = {
        'status': fields.selection([
            ('pro','Retencion Procesada, Linea xml generada'),
            ('no_pro','Retencion no Procesada'),
            ('tasa','No supera la tasa, Linea xml generada'),
            ],'Estatus',readonly=True )
    }
    _defaults = {
        'status': lambda *a: "no_pro",
    }

    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default = default.copy()
        default.update({'islr_wh_doc':0,
                        'status': 'no_pro',
        })
        return super(account_invoice, self).copy(cr, uid, id, default, context)

    def _refund_cleanup_lines(self, cr, uid, lines):
        data = super(account_invoice, self)._refund_cleanup_lines(cr, uid, lines)
        list = []
        for x,y,res in data:
            if 'concept_id' in res:
                res['concept_id'] = res.get('concept_id', False) and res['concept_id'][0]
            if 'apply_wh' in res:
                res['apply_wh'] = False
            if 'wh_xml_id' in res:
                res['wh_xml_id'] = 0
            list.append((x,y,res))
        return list

    def _get_partners(self, cr, uid, invoice):
        '''
        Se obtiene: el id del vendedor, el id del comprador de la factura y el campo booleano que determina si el comprador es agente de retencion.
        '''
        if invoice.type == 'in_invoice' or invoice.type == 'in_refund':
            vendor = invoice.partner_id
            buyer = invoice.company_id.partner_id
        else:
            buyer = invoice.partner_id
            vendor = invoice.company_id.partner_id
        return (vendor, buyer, buyer.islr_withholding_agent)

    def _get_concepts(self, cr, uid, invoice):
        '''
        Se obtienen una lista de Conceptos(concept_id), de las lineas en la factura
        '''
        service_list = []
        for invoice_line in invoice.invoice_line:
            if invoice_line.concept_id and invoice_line.concept_id.withholdable:
                service_list.append(invoice_line.concept_id.id)
            else:
                pass
        return list(set(service_list))
        

    def _get_service_wh(self, cr, uid, invoice, concept_list):
        '''
        Obtiene todas las lineas de factura del vendedor, filtrando por el periodo de la factura actual y el estado de la factura = done, open.
        Las lineas son almacenadas en un diccionario, donde la primera clave es la lista de lineas obtenidas, la segunda es el campo que indica si alguna de esas lineas
        fue retenida y el tercer campo es la suma de la base de todas las lineas que no se les ha aplicado retencion.
        La busqueda de las lineas, se realiza buscando lineas que tengan conceptos de retencion igual a los de la factura actual.
        Esto se hace con el fin de verificar:
            1.-Si existe el mismo concepto en otra linea de factura que no se ha retenido porque no ha superado el monto minimo, se toma para realizar la suma y verificar 
               si con el nuevo monto si supera, en consecuencia se realiza la retencion en las facturas asociadas.
            2.-Se verifica si es la primera vez que se realiza retencion sobre ese concepto, de ser la primera vez se debe aplicar el sustraendo. Esto se hace con el 
               segundo campo del diccionario "wh"
        '''
        dict={}
        for key in concept_list:
            dict[key]={'lines':[],'wh':False,'base':0.0}
        inv_obj = self.pool.get('account.invoice')
        inv_lst = inv_obj.search(cr, uid,[('partner_id', '=', invoice.partner_id.id),('period_id','=',invoice.period_id.id),('state','in',['done','open'])]) # Lista de  facturas asociadas al proveedor actual, al periodo actual y al estado de las facturas: donde, open.
        
        inv_line_lst=[]
        for id in inv_lst:
            inv_line_brw = inv_obj.browse(cr, uid, id).invoice_line #lista de lineas de facturas
            for line in inv_line_brw:
                if line.concept_id and  line.concept_id.id in concept_list: # Se verifica si el concepto de la linea en la que estoy buscando coincide con alguno de los conceptos de la factura actual.
                    if not line.apply_wh: # Se verifica si a la linea no se le ha aplicado retencion, de ser asi se almacena el id de la linea y la base.
                        dict[line.concept_id.id]['lines'].append(line.id)
                        dict[line.concept_id.id]['base']+= line.price_subtotal
                    else:  # Si ya se le aplico retencion, no se guarda el id porque no hace falta pero se indica que ya se le aplico retencion.
                        dict[line.concept_id.id]['wh']=True
        #~ dict[key]={'lines':[],'wh':False,'base':0.0}
        return dict

    def _get_country_fiscal(self,cr, uid, partner_id):
        '''
        Se obtiene el pais de el vendedor o comprador, depende del parametro. A partir de de la direccion fiscal.
        '''
        for i in partner_id.address:
            if i.type=='invoice':
                if not i.country_id:
                    raise osv.except_osv(_('Invalid action !'),_("Imposible realizar Comprobante de Retencion ISLR, debido a que el partner '%s' no tiene pais en su facturacion fiscal!") % (partner_id.name))
                    return False
                else:
                    return i.country_id.id
            else:
                raise osv.except_osv(_('Invalid action !'),_("Imposible realizar Comprobante de Retencion ISLR, debido a que el partner '%s' no tiene direccion fiscal asociada!") % (partner_id.name))
                return False
        return False


    def _get_residence(self, cr, uid, vendor, buyer):
        '''
        Se determina si la direccion fiscal del comprador es la misma que la del vendedor, con el fin de luego obtener la tasa asociada.
        Retorna True si es una persona domiciliada o residente. Retorna False si es, no Residente o No Domicialiado.
        '''
        vendor_address = self._get_country_fiscal(cr, uid, vendor)
        buyer_address = self._get_country_fiscal(cr, uid, buyer)
        if vendor_address and buyer_address:
            if vendor_address ==  buyer_address:
                return True
            else:
                return False
        return False

    def _get_nature(self, cr, uid, partner_id):
        '''
        Se obtiene la naturaleza del vendedor a partir del RIF, retorna True si es persona de tipo natural, y False si es juridica.
        '''
        if not partner_id.vat:
            raise osv.except_osv(_('Invalid action !'),_("Imposible realizar Comprobante de Retencion ISLR, debido a que el partner, '%s' no tiene RIF asociado!") % (partner_id.name))
            return False
        else:
            if partner_id.vat[2:3] in 'VvEe':
                return True
            else:
                return False

    def _get_rate(self, cr, uid, concept_id, residence, nature,context):
        '''
        Se obtiene la tasa del concepto de retencion, siempre y cuando exista uno asociado a las especificaciones:
           La naturaleza del vendedor coincida con una tasa.
           La residencia del vendedor coindica con una tasa.
        '''
        ut_obj = self.pool.get('l10n.ut')
        rate_brw_lst = self.pool.get('islr.wh.concept').browse(cr, uid, concept_id).rate_ids
        for rate_brw in rate_brw_lst:
            if rate_brw.nature == nature and rate_brw.residence == residence:
                #~ (base,min,porc,sust,codigo,id_rate,name_rate)
                rate_brw_minimum = ut_obj.compute_ut_to_money(cr, uid, rate_brw.minimum, False, context)#metodo que transforma los UVT en pesos
                rate_brw_subtract = ut_obj.compute_ut_to_money(cr, uid, rate_brw.subtract, False, context)#metodo que transforma los UVT en pesos
                return (rate_brw.base, rate_brw_minimum, rate_brw.wh_perc, rate_brw_subtract,rate_brw.code,rate_brw.id,rate_brw.name)
        return ()
    
    def _get_rate_dict(self, cr, uid, concept_list, residence, nature,context):
        '''
        Devuelve un diccionario con la tasa de cada concepto de retencion.
        '''
        dict = {}
        cont = 0
        for concept_id in concept_list:
            dict[concept_id] = self._get_rate(cr, uid, concept_id, residence, nature,context)
            if dict[concept_id]:
                cont += 1
        if not cont:
            raise osv.except_osv(_('Invalid action !'),_("Imposible realizar Comprobante de Retencion ISLR, debido a que  el Concepto de Retencion asociado a la linea no es de tipo Retenible!"))
        return dict


    def _pop_dict(self,cr,uid,concept_list,dict_rate,wh_dict):
        '''
        Funcion para eliminar del diccionario de conceptos con tasas y del diccionario de lineas de facturas, todos aquellos elementos donde el concepto de retencion no 
        posee una tasa asociada.
        '''
        for concept in concept_list:
            if not dict_rate[concept]:
                dict_rate.pop(concept)
                wh_dict.pop(concept)


    def _get_wh_calc(self,cr,uid,line,dict_rate_concept):
        base = self.pool.get('account.invoice.line').browse(cr,uid,line).price_subtotal
        return (base * (dict_rate_concept[0]/100) * (dict_rate_concept[2]/100), base)


    def _get_number(self,cr,uid,number,long):
        num1 = number[::-1]
        result= ''
        for i in num1:
            if i.isdigit():
                if len(result)<long:
                    result = i + result
                else:
                    break
            else:
                break
        return result.strip()


    def _get_inv_data(self,cr, uid, line):
        '''
        Se obtiene el rif de proveedor, el numero de la factura y el numero de control de la factura. Datos necesarios para el XML, entre otros.
        '''
        inv_brw = self.pool.get('account.invoice.line').browse(cr, uid, line).invoice_id
        vat = inv_brw.partner_id.vat[2:]
        if inv_brw.type == 'in_invoice' or inv_brw.type == 'in_refund':
            #~ number = inv_brw.reference.strip() 
            if not inv_brw.reference:
                raise osv.except_osv(_('Invalid action !'),_("Imposible realizar Comprobante de Retencion ISLR, debido a que la factura numero: '%s' no tiene Numero de Referencia Libre!") % (inv_brw.number))
                number = 0
            else:
                number = self._get_number(cr,uid,inv_brw.reference.strip(),10)
        else:
            if not inv_brw.number:
                number = 0
            else:
                number = self._get_number(cr,uid,inv_brw.number.strip(),10)

        if not inv_brw.nro_ctrl:
            raise osv.except_osv(_('Invalid action !'),_("Imposible realizar Comprobante de Retencion ISLR, debido a que la factura numero: '%s' no tiene Numero de Control Asociado!") % (inv_brw.number))
        else:
            control = self._get_number(cr,uid,inv_brw.nro_ctrl.strip(),8)
        return (vat, number, control)


    def _write_wh_apply(self,cr, uid,line,dict,apply):
        '''
        Si el campo wh_xml_id en la linea de la factura tiene un id de xml asociado:
            Se escribe sobre el campo booleano de la linea de la factura True o False, dependiendo si se retiene o no.
            Se escribe sobre la linea de xmls el valor de la retencion. Esto sucede porque se pudo haber creado la linea xml, pero con retencion 0, porque no aplicaba, si llega a superar en otra factura, se debe sobreescribir el valor al nuevo monto de retencion.
        De lo contrario:
            Se crea una nueva linea de xml.
            Se escribe en la linea de la factura, True o False y se asigna el xml_id que resulta del create.
        '''
        il_ids = self.pool.get('account.invoice.line').browse(cr, uid,line)

        if il_ids.wh_xml_id:
            self.pool.get('account.invoice.line').write(cr, uid, line, {'apply_wh': apply})
            self.pool.get('islr.xml.wh.line').write(cr,uid,il_ids.wh_xml_id.id,{'wh':dict['wh']})
        else:
            self.pool.get('account.invoice.line').write(cr, uid, line, {'apply_wh': apply,'wh_xml_id':self._create_islr_xml_wh_line(cr, uid,line,dict)})

    def _create_islr_xml_wh_line(self,cr, uid, line, dict):
        '''
        Se crea una linea de xml
        '''
        inv_id = self.pool.get('account.invoice.line').browse(cr, uid,line).invoice_id
        return self.pool.get('islr.xml.wh.line').create(cr, uid, {'name': dict['name_rate'],
        'concept_id': dict['concept'], 
        'period_id':  inv_id.period_id.id,
        'partner_vat':dict['vat'],
        'invoice_number': dict['number'],
        'control_number': dict['control'],
        'concept_code':dict['code'],
        'base': dict['subtotal'],
        'porcent_rete':dict['perc'],
        'wh':dict['wh'],
        'rate_id': dict['rate_id'],
        'account_invoice_line_id': line,
        'partner_id': inv_id.partner_id.id,
        })

    def _get_wh(self,cr, uid, subtract,concept, wh_dict, dict_rate, apply):
        '''
        Retorna un diccionario, con todos los valores de la retencion de una linea de factura.
        '''
        res= {}
        if apply: # Si se va a aplicar retencion.
            for line in wh_dict[concept]['lines']:
                wh_calc, subtotal = self._get_wh_calc(cr,uid,line,dict_rate[concept]) # Obtengo el monto de retencion y el monto base sobre el cual se retiene
                if subtract >= wh_calc:
                    wh = 0.0
                    subtract -= wh_calc
                else:
                    wh = wh_calc - subtract
                    subtract_write= subtract
                    subtract=0.0
                res[line]={ 'vat': self._get_inv_data(cr, uid, line)[0],
                            'number': self._get_inv_data(cr, uid, line)[1],
                            'control': self._get_inv_data(cr, uid, line)[2],
                            'concept': concept, 
                            'code':dict_rate[concept][4],
                            'subtotal': subtotal, 
                            'perc':dict_rate[concept][2],
                            'wh':wh,
                            'apply':apply,
                            'rate_id':dict_rate[concept][5],
                            'name_rate': dict_rate[concept][6]}
                self._write_wh_apply(cr,uid,line,res[line],apply)
                inv_id = self.pool.get('account.invoice.line').browse(cr, uid,line).invoice_id.id
                self.pool.get('account.invoice').write(cr, uid, inv_id, {'status': 'pro'})
            return res
        else: # Si no aplica retencion
            for line in wh_dict[concept]['lines']:
                subtotal = self._get_wh_calc(cr,uid,line,dict_rate[concept])[1]
                res[line]={ 'vat': self._get_inv_data(cr, uid, line)[0],
                            'number': self._get_inv_data(cr, uid, line)[1],
                            'control': self._get_inv_data(cr, uid, line)[2],
                            'concept': concept, 
                            'code':dict_rate[concept][4],
                            'subtotal': subtotal, 
                            'perc':dict_rate[concept][2],
                            'wh':0.0,
                            'apply':apply,
                            'rate_id':dict_rate[concept][5],
                            'name_rate': dict_rate[concept][6]}
                self._write_wh_apply(cr,uid,line,res[line],apply)
                inv_id = self.pool.get('account.invoice.line').browse(cr, uid,line).invoice_id.id
                self.pool.get('account.invoice').write(cr, uid, inv_id, {'status': 'tasa'})
            return res


    def _get_wh_apply(self,cr,uid,dict_rate,wh_dict):
        '''
        Retorna el diccionario completo con todos los datos para realizar la retencion, cada elemento es una linea de la factura.
        '''
        res = {}
        for concept in wh_dict:
            if not wh_dict[concept]['wh']:  #Si nunca se ha aplicado retencion con este concepto.
                if wh_dict[concept]['base'] >= dict_rate[concept][1]: # Si el monto base que suman todas las lineas de la factura es mayor o igual al monto minimo de la tasa.
                    subtract = dict_rate[concept][3]  # Obtengo el sustraendo a aplicar. Existe sustraendo porque es la primera vez.
                    res.update(self._get_wh(cr, uid, subtract,concept, wh_dict, dict_rate, True))# El True sirve para asignar al campo booleano de la linea de la factura True, para asi marcar de una vez que ya fue retenida, para una posterior busqueda.
                else: # Si el monto base no supera el monto minimo de la tasa(de igual forma se deb declarar asi no supere.)
                    subtract = 0.0
                    res.update(self._get_wh(cr, uid, subtract,concept, wh_dict, dict_rate, False))
            else: #Si ya se aplico alguna vez la retencion, se aplica rete de una vez, sobre la base sin chequear monto minimo.(Dentro de este periodo)
                subtract = 0.0
                res.update(self._get_wh(cr, uid, subtract,concept, wh_dict, dict_rate, True))# El True sirve para indicar que la linea si se va a retener.
        return res


    def _get_amount(self,cr,uid,dict):
        '''
        Funcion para obtener, la suma del monto retenido por concepto.
        '''
        dict_concept = {}
        for key in dict:
            x = dict[key]['concept']
            y = dict[key]['wh']
            if not dict_concept.get(x,False):
                dict_concept[x] = y
            else:
                dict_concept[x]+= y
        return dict_concept


    def _get_dict_concepts(self,cr,uid,dict):
        '''
        Funcion para obtener, el dicccionario agrupado por concepto:  
        {1:[{64: {'control': '', 'perc': 0.050000000000000003, 'concept': 1, 'number': False, 'wh': 0.0, 'code': u'A', 'rate_id': 1, 'apply': True, 'subtotal': 500.0, 'vat': u'J123456789'}}, 
            {65: {'control': '', 'perc': 0.050000000000000003, 'concept': 1, 'number': False, 'wh': 0.0, 'code': u'A', 'rate_id': 1, 'apply': True, 'subtotal': 300.0, 'vat': u'J123456789'}}
           ], 
         2:[{63: {'control': '', 'perc': 0.029999999999999999, 'concept': 2, 'number': False, 'wh': 0.0, 'code': u'002', 'rate_id': 2, 'apply': True, 'subtotal': 1000.0, 'vat': u'J123456789'}}
            ]}
        '''
        dict_concepts = {}
        for key in dict:
            x = dict[key]['concept']
            y = dict[key]
            if not dict_concepts.get(x,False):
                if dict[key]['apply']:
                    dict_concepts[x]=[]
                    dict_concepts[x].append({key:y})
            else:
                if dict[key]['apply']:
                    dict_concepts[x].append({key:y})
        return dict_concepts


    def get_journal(self,cr,uid,inv_brw):
        '''
        Funcion para asignar el diario correspondiente de acuerdo a cada tipo de retencion(compra, venta)
        los tipos de diario son creados en retencion_iva
        '''
        journal_id = None
        journal_obj = self.pool.get('account.journal')
        if inv_brw.type == 'out_invoice' or inv_brw.type =='out_refund':
            journal_id = journal_obj.search(cr, uid, [('type', '=', 'retislrSale')], limit=1)
            tipo1 = 'Venta'
            tipo2 = 'retislrSale'
        else:
            journal_id = journal_obj.search(cr, uid, [('type', '=', 'retislrPurchase')], limit=1)
            tipo = 'Compra'
            tipo2 = 'retislrPurchase'
        if not journal_id:
            raise osv.except_osv(_('Invalid action !'),_("Imposible realizar Comprobante de Retencion ISLR, debido a que el diario de ISLR para la '%s' no ha sido creado con el tipo 's%'") % (tipo,tipo2))
        
        return journal_id[0] or None
        
    def _create_islr_wh_doc(self,cr,uid,inv_brw,dict):
        '''
        Funcion para crear en el modelo islr_wh_doc
        '''
        islr_wh_doc_id=0 
        wh_doc_obj = self.pool.get('islr.wh.doc')
        inv_obj =self.pool.get('account.invoice.line')
        inv_brw = inv_brw.invoice_id
    
        islr_wh_doc_id = wh_doc_obj.create(cr,uid,{'name': wh_doc_obj.retencion_seq_get(cr, uid),
                                                   'partner_id': inv_brw.partner_id.id,
                                                   'invoice_id': inv_brw.id,
                                                   'period_id': inv_brw.period_id.id,
                                                   'account_id': inv_brw.account_id.id,
                                                   'type': inv_brw.type,
                                                   'journal_id': self.get_journal(cr,uid,inv_brw)
                                                   })
        return islr_wh_doc_id


    def _create_doc_line(self,cr,uid, inv_brw,key2,islr_wh_doc_id,dict,dictc):
        '''
        Funcion para crear en el modelo islr_wh_doc_line
        '''
        doc_line_obj = self.pool.get('islr.wh.doc.line')
        rate_obj = self.pool.get('islr.rates')
        dict_concept = self._get_amount(cr,uid,dict)
        inv_line_id = dictc[key2][0].keys()[0]
        rate_id = dictc[key2][0][inv_line_id]['rate_id']
        
        #~ line_idd = dictc[key2][0].keys()
        #~ print 'LINEEEE IDD22222', line_idd[0]
        #~ inv_idd= self.pool.get('account.invoice.line').browse(cr, uid,line_idd[0]).invoice_id.id
        #~ print 'IDDDD INVOICEEEE', inv_idd        
        
        
        islr_wh_doc_line_id = doc_line_obj.create(cr,uid,{'islr_wh_doc_id':islr_wh_doc_id,
                                                'concept_id':key2,
                                                'islr_rates_id':rate_id,
                                                'invoice_id': inv_brw.invoice_id.id,
                                                'retencion_islr': rate_obj.browse(cr,uid,rate_id).wh_perc,
                                                'amount':dict_concept[key2],
                                                #~ 'invoice_id':inv_idd,
                                                })
        return islr_wh_doc_line_id


    def _create_doc_invoices(self,cr,uid,key,islr_wh_doc_id):
        '''
        Funcion para crear en el modelo islr_wh_doc_invoices
        '''
        doc_inv_obj = self.pool.get('islr.wh.doc.invoices')
        inv_id = key
        islr_wh_doc_invoices_id = doc_inv_obj.create(cr,uid,{'invoice_id':inv_id,'islr_wh_doc_id':islr_wh_doc_id})


    def _write_wh_xml(self,cr,uid,key,islr_wh_doc_line_id):
        '''
        Funcion para escribir en el modelo xml_wh_line
        '''
        inv_obj =self.pool.get('account.invoice.line')
        xml_obj = self.pool.get('islr.xml.wh.line')
        xml_id = inv_obj.browse(cr,uid,key).wh_xml_id.id
        xml_obj.write(cr, uid, xml_id, {'islr_wh_doc_line_id':islr_wh_doc_line_id})


    def _get_inv_id(self,cr,uid,dict):
        '''
        Funcion para obtener el objeto_browse de la factura
        '''
        inv_brw = False
        inv_obj =self.pool.get('account.invoice.line')
        line_ids = []
        inv_id1 = 0
        for key in dict:
            if dict[key]['apply']:
                line_ids.append(key)
        if line_ids:
            line_ids.sort()
            inv_id1 = line_ids[-1]
            inv_brw = inv_obj.browse(cr,uid,inv_id1)
        return inv_brw


    def _logic_create(self,cr,uid,dict):
        '''
        Manejo de toda la logica para la generarion de lineas en los modelos.
        '''
        dictc = self._get_dict_concepts(cr,uid,dict)
        inv_brw = self._get_inv_id(cr,uid,dict)
        inv_obj =self.pool.get('account.invoice.line')
        
        if inv_brw:
            if dictc:
                islr_wh_doc_id = self._create_islr_wh_doc(cr,uid,inv_brw,dict)
            else:
                pass
            key_lst = []
            if islr_wh_doc_id:
                for key2 in dictc:
                    inv_line_id = dictc[key2][0].keys()[0]
                    islr_wh_doc_line_id = self._create_doc_line(cr,uid,inv_brw,key2,islr_wh_doc_id,dict,dictc)
                    for line in dictc[key2]:
                        inv_line_id2 = dictc[key2][0].keys()[0]
                        for key in line:
                            key_lst.append(inv_obj.browse(cr,uid,key).invoice_id.id)
                            self._write_wh_xml(cr,uid,key,islr_wh_doc_line_id)
                for key in set(key_lst):
                    self._create_doc_invoices(cr,uid,key,islr_wh_doc_id)
                        
                self.pool.get('account.invoice').write(cr,uid,inv_brw.invoice_id.id,{'islr_wh_doc_id':islr_wh_doc_id})
            else:
                pass
        else:
            pass


    def action_ret_islr(self, cr, uid, ids, context={}):
        invoices_brw = self.browse(cr, uid, ids, context=None)
        wh_doc_list = []
        for invoice in invoices_brw:
            wh_doc_list = self.pool.get('islr.wh.doc.invoices').search(cr,uid,[('invoice_id','=',invoice.id)])  
            if wh_doc_list: #Chequear que la factura no haya sido retenida.
                raise osv.except_osv(_('Invalid action !'),_("La Retencion a la factura '%s' ya fue realizada!") % (invoice.number))
            else: # 1.- Si la factura no ha sido retenida
                wh_dict={}
                dict_rate={}
                dict_completo={}
                vendor, buyer, apply_wh = self._get_partners(cr,uid,invoice) # Se obtiene el (vendedor, el comprador, si el comprador es agente de retencion)
                concept_list = self._get_concepts(cr,uid,invoice)# Se obtiene la lista de conceptos de las lineas de la factura actual.
                if concept_list:  # 2.- Si existe algun concepto de retencion en las lineas de la factura.
                    if apply_wh:  # 3.- Si el comprador es agente de retencion
                        wh_dict = self._get_service_wh(cr, uid, invoice, concept_list) # Se obtiene un dic con la lista de lineas de factura, si se aplico retencion alguna vez, el monto base total de las lineas.
                        residence = self._get_residence(cr, uid, vendor, buyer) # Retorna el tipo de residencia del vendedor
                        nature = self._get_nature(cr, uid, vendor) # Retorna la naturaleza del vendedor.
                        dict_rate = self._get_rate_dict(cr, uid, concept_list, residence, nature,context) # Retorna las tasas por cada concepto
                        self._pop_dict(cr,uid,concept_list,dict_rate,wh_dict) # Borra los conceptos y las lineas de factura que no tengan tasa asociada.
                        dict_completo = self._get_wh_apply(cr,uid,dict_rate,wh_dict) # Retorna el dict con todos los datos de la retencion por linea de factura.
                        self._logic_create(cr,uid,dict_completo)# Se escribe y crea en todos los modelos asociados al islr.
                    else:
                        raise osv.except_osv(_('Invalid action !'),_("Imposible realizar Comprobante de Retencion ISLR, debido a que el comprador '%s' no es agente de Retencion!") % (buyer.name))
                else:
                    raise osv.except_osv(_('Invalid action !'),_("Imposible realizar Comprobante de Retencion ISLR, debido a que las lineas de la factura no tienen Concepto de Retencion!"))
account_invoice()









