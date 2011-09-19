#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Humberto Arocha           <humberto@openerp.com.ve>
#              María Gabriela Quilarque  <gabrielaquilarque97@gmail.com>
#              Javier Duran              <javier@vauxoo.com>
#              Israel Fermín Montilla  <israel@openerp.com.ve>
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

class inherited_invoice(osv.osv):
    _inherit = "account.invoice"
    _columns = {
        'date_document': fields.date("Document Date", 
                                help="Administrative date", 
                                        select=True),
        'date_invoice': fields.date('Fecha Contable', 
                                    states={'open':[('readonly',True)],
                                    'close':[('readonly',True)],
                                    'paid':[('readonly',True)]},
        help="Keep empty to use the current date\n It represent the date when we did account charge, known as Accounting Date too!"),
        'expedient':fields.boolean('Expediente?', help="Seleccionar solo si la factura de compra es un expediente de importación"),
        }
inherited_invoice()
