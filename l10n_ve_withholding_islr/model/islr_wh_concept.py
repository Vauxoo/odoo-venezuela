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
from openerp.osv import fields, osv


class IslrWhConcept(osv.osv):

    """ Model to create the withholding concepts
    """
    _name = 'islr.wh.concept'
    _description = 'Income Withholding Concept'

    _columns = {
        'name': fields.char(
            'Withholding Concept', translate=True, size=256, required=True,
            help="Name of Withholding Concept, Example: Honorarios"
                 " Profesionales, Comisiones a..."),
        'withholdable': fields.boolean(
            string='Withhold', default=True,
            help="Check if the concept  withholding is withheld or not."),
        'property_retencion_islr_payable': fields.property(
            type='many2one',
            relation='account.account',
            string="Purchase account withhold income",
            method=True,
            required=False,
            domain="[('type', '=', 'other')]",
            help="This account will be used as the account where the withheld"
                 " amounts shall be charged in full (Purchase) of income tax"
                 " for this concept"),
        'property_retencion_islr_receivable': fields.property(
            type='many2one',
            relation='account.account',
            string="Sale account withhold income",
            method=True,
            required=False,
            domain="[('type', '=', 'other')]",
            help="This account will be used as the account where the withheld"
                 " amounts shall be charged in (Sale) of income tax"),
        'rate_ids': fields.one2many(
            'islr.rates', 'concept_id', 'Rate',
            help="Withholding Concept rate", required=False),
        'user_id': fields.many2one(
            'res.users', string='Salesman', readonly=True,
            states={'draft': [('readonly', False)]},
            default=lambda s: s._uid,
            help="Vendor user"),
    }

IslrWhConcept()
