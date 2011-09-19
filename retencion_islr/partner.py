# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Vauxoo C.A. (http://openerp.com.ve/) All Rights Reserved.
#                    Javier Duran <jduran@corvus.com.ve>
# 
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from osv import fields, osv


class res_partner(osv.osv):
    _inherit = 'res.partner'
    _description = "Contribuyente Especial"
    _columns = {
        'property_retencion_islr_payable': fields.property(
            'account.account',
            type='many2one',
            relation='account.account',
            string="Cuenta Retencion Compra ISLR",
            method=True,
            view_load=True,
            domain="[('type', '=', 'other')]",
            help="Esta cuenta sera usada como la cuenta donde se cargaran los montos retenidos de I.V.A.  en vez de la cuenta de reserva predeterminda para el actual partner"),
        'property_retencion_islr_receivable': fields.property(
            'account.account',
            type='many2one',
            relation='account.account',
            string="Cuenta Retencion Venta ISLR",
            method=True,
            view_load=True,
            domain="[('type', '=', 'other')]",
            help="Esta cuenta sera usada como la cuenta donde se cargaran los montos retenidos de I.S.L.R. en vez de la cuenta de reserva predeterminda para el actual partner"),

   }


res_partner()
