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

class islr_rates(osv.osv):
    '''
    Modulo para crear las tasas de los Conceptos de Retencion
    '''
    _name='islr.rates'


    def _get_name(self,cr,uid,ids, field_name, arg, context):
        '''
        Funcion para obtener el nombre de la tasa del concepto de retencion
        '''
        res={}
        for rate in self.browse(cr,uid,ids):
            if rate.nature:
                if rate.residence:
                    name = 'Persona' + ' ' +'Natural' + ' ' +'Residente'
                else:
                    name = 'Persona' + ' ' +'Natural' + ' ' +'No Residente'
            else:
                if rate.residence:
                    name = 'Persona' + ' ' +'Juridica' + ' ' +'Domiciliada'
                else:
                    name = 'Persona' + ' ' +'Juridica' + ' ' +'No Domiciliada'
            res[rate.id]=name
        return res

    _columns={
    'name': fields.function(_get_name, method=True, type='char', string='Tasa del Concepto de Pago', size=256),
    'code':fields.char('Cod. Concepto de Rete', size=3,required=True),
    'base': fields.float('Base Imponible para Calculo de Rete',required=True, help="Porcentaje del monto sobre el cual se va a aplicar la retencion"),
    'minimum': fields.float('Monto Min. en Und. Trib.',required=True, help="Monto minimo, a partir del cual se determina si se va a a retener"),
    'wh_perc': fields.float('Monto Porcentual de Rete',required=True,help="Porcentaje que se aplica a la Base Imponible de Retencion, para arrojar el monto total a retener"),
    'subtract': fields.float('Sustraendo en Unid. Trib.',required=True,help="Cantidad a restar del monto total a retener,..Monto Porcentual de Retencion... Este sustraendo solo se aplicara la primera vez que se realiza la retencion"),
    'residence': fields.boolean('Residenciado',help="Indica si una persona es Residencia o no Residenciada, comparado con la direccion de la Compania"),
    'nature': fields.boolean('Natural',help="Indica si una persona es Natural o Juridica"),
    'concept_id': fields.many2one('islr.wh.concept','Concepto de Retencion',help="Concepto de Retencion asociado a esta Tasa",required=False, ondelete='cascade'),
    }
islr_rates()



