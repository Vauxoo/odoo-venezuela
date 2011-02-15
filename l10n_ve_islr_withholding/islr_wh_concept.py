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


class islr_wh_concept(osv.osv):
    '''
    Modulo para crear los Conceptos de Retencion
    '''
    _name='islr.wh.concept'

    _columns={
        'name':fields.char('Concepto de Retencion de  ISLR', size=256,required=True,help="Nombre del Concepto de Pago, ej: Honorarios Profesionales, Comisiones a..."),
        'withholdable': fields.boolean('Retenible',help="Determina si el Concepto es Retenible o No es retenible"),
        'property_retencion_islr_payable': fields.property(
            'account.account',
            type='many2one',
            relation='account.account',
            string="Cuenta Retencion Compra ISLR",
            method=True,
            view_load=True,
            required = True,
            domain="[('type', '=', 'other')]",
            help="Esta cuenta sera usada como la cuenta donde se cargaran los montos retenidos por enterar(Compra) de I.S.L.R para este concepto"),
        'property_retencion_islr_receivable': fields.property(
            'account.account',
            type='many2one',
            relation='account.account',
            string="Cuenta Retencion Venta ISLR",
            method=True,
            view_load=True,
            required = True,
            domain="[('type', '=', 'other')]",
            help="Esta cuenta sera usada como la cuenta donde se cargaran los montos de retencion(Venta) de I.S.L.R."),
        'rate_ids': fields.one2many('islr.rates','concept_id','Tasa',help="Tasa del Concepto de Retencion",required=False),
    }
    _defaults = {
        'withholdable': lambda *a: True,
    }
islr_wh_concept()


