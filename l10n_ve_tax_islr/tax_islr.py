# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    nhomar@vauxoo.com
#
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
#
##############################################################################
from osv import osv
from osv import fields
from tools import config
from tools.translate import _

class group_concept_islr(osv.osv):
    """
    OpenERP Model : group_concept_islr
    """
    
    _name = 'group.concept.islr'
    _description = 'Grouping for concepts in ISLR'
    
    _columns = {
        'name':fields.char('Name', size=200, required=False, readonly=False),
        'code':fields.char('Code Group', size=64, required=False, readonly=False),
        'concept_ids':fields.one2many('concepts.rates.islr', 'group_id', 'Concepts', required=False),
    }
    _defaults = {
        'name': lambda *a: None,
    }
group_concept_islr()

class concepts_rates_islr(osv.osv):
    """
    OpenERP Model : concepts_rates_islr
    """
    
    _name = 'concepts.rates.islr'
    _description = 'concepts_rates_islr List to cals'
    
    _columns = {
        'name':fields.char('Concept', size=270, required=False, readonly=False, help="Name Exactly as described on the law for this Case/Activity"),
        'literal':fields.char('Articulo 9 Num/Lit', size=8, required=False, readonly=False, help="Reference to law"),
        'code':fields.char('Code', size=8, required=False, readonly=False, help="Code to be exported to SENIAT XML file"),
        'rate': fields.float('Tax Rate', digits=(16, int(config['price_accuracy'])), help="Tax Rate to be applied over the untaxed amount after applying 'Untaxed Amount Rate'"),
        'limit': fields.float('Limit', digits=(16, int(config['price_accuracy'])), help="Limit amount in TU to be applied this rate 0.00 to all cases -1 for the bigest limit or amounts in the middle ie: 2000 TU, 3000 TU"),
        'situation':fields.selection([
            ('PNR','Persona Natural Residente'),
            ('PNNR','Persona Natural No Residente'),
            ('PJD','Persona Jurídica Domiciliada'),
            ('PJND','Persona Jurídica No Domiciliada'),
            ('PJNCD','Persona Jurídica No Constituida Domiciliada')
        ],'Situation', select=True, readonly=False),
        
        'subtrahend': fields.float('Subtrahend', digits=(16, int(config['price_accuracy']))),
        'group_id':fields.many2one('group.concept.islr', 'Group', required=False),
        'base_imp': fields.float('Untaxed amount rate', digits=(16, int(config['price_accuracy'])), help="Rate of the untaxed amount over which is going to be aplied the tax Rate"),
        'note': fields.text('Description', help="Description for this case is necesary an example for every case on english and Spanish"),
        'base_imp_min': fields.float('Min. untaxed amount', digits=(16, int(config['price_accuracy'])), help="minimum untaxed amount over which is going to be aplied the tax Rate"),
    }
concepts_rates_islr()


