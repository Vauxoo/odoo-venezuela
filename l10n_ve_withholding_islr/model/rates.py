# coding: utf-8
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############################################################################
#    Credits:
#    Coded by: Humberto Arocha           <humberto@openerp.com.ve>
#              Maria Gabriela Quilarque  <gabrielaquilarque97@gmail.com>
#              Javier Duran              <javier@vauxoo.com>
#    Planified by: Nhomar Hernandez
#    Finance by: Helados Gilda, C.A. http://heladosgilda.com.ve
#    Audited by: Humberto Arocha humberto@openerp.com.ve
#############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
##############################################################################
from openerp.addons import decimal_precision as dp
from openerp.osv import fields, osv


class IslrRates(osv.osv):

    """ The module to create the rates of the withholding concepts
    """
    _name = 'islr.rates'
    _description = 'Rates'

    def _get_name(self, cr, uid, ids, field_name, arg, context):
        """ Get the name of the withholding concept rate
        """
        res = {}
        for rate in self.browse(cr, uid, ids):
            if rate.nature:
                if rate.residence:
                    name = 'Persona' + ' ' + 'Natural' + ' ' + 'Residente'
                else:
                    name = 'Persona' + ' ' + 'Natural' + ' ' + 'No Residente'
            else:
                if rate.residence:
                    name = 'Persona' + ' ' + 'Juridica' + ' ' + 'Domiciliada'
                else:
                    name = 'Persona' + ' ' + 'Juridica' + ' ' + \
                        'No Domiciliada'
            res[rate.id] = name
        return res

    _columns = {
        'name': fields.function(
            _get_name, method=True, type='char', string='Rate', size=256,
            help="Name retention rate of withhold concept"),
        'code': fields.char(
            'Concept Code', size=3, required=True, help="Concept code"),
        'base': fields.float(
            'Without Tax Amount', required=True,
            help="Percentage of the amount on which to apply the withholding",
            digits_compute=dp.get_precision('Withhold ISLR')),
        'minimum': fields.float(
            'Min. Amount', required=True,
            digits_compute=dp.get_precision('Withhold ISLR'),
            help="Minimum amount, from which it will determine whether you"
                 " withholded"),
        'wh_perc': fields.float(
            'Percentage Amount', required=True,
            digits_compute=dp.get_precision('Withhold ISLR'),
            help="The percentage to apply to taxable withold income throw the"
                 " amount to withhold"),
        'subtract': fields.float(
            'Subtrahend in Tax Units', required=True,
            digits_compute=dp.get_precision('Withhold ISLR'),
            help="Amount to subtract from the total amount to withhold,"
                 " Amount Percentage withhold ..... This subtrahend only"
                 " applied the first time you perform withhold"),
        'residence': fields.boolean(
            'Residence',
            help="Indicates whether a person is resident, compared with the"
                 " direction of the Company"),
        'nature': fields.boolean(
            'Nature', help="Indicates whether a person is nature or legal"),
        'concept_id': fields.many2one(
            'islr.wh.concept', 'Withhold  Concept', required=False,
            ondelete='cascade',
            help="Withhold concept associated with this rate"),
        'rate2': fields.boolean(
            'Rate 2', help='Rate Used for Foreign Entities'),
    }
IslrRates()
