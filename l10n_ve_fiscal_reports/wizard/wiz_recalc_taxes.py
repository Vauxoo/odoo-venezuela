# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010 Vauxoo C.A. (http://openerp.com.ve/) All Rights Reserved.
#                    Javier Duran <javier@vauxoo.com>
#                    Nhomar Hernandez <nhomar@vauxoo.com>
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

'''
Fiscal Report For Venezuela
'''

from osv import fields
from osv import osv
import time
import ir
from mx import DateTime
import datetime
import pooler
from tools import config
import wizard
import netsvc


book_form= """<?xml version="1.0"?>
<form string="Recompute taxes on Invoices">
<group colspan="6" cols="2">
    <label align="0.7" colspan="6" string="Please Select date range of invoices to be recalculated, this method allow group same taxes on invoices."/>
     <field name="date_start" />
     <newline/>
     <field name="date_end" />
</group>
</form>
"""

book_field= {
    'date_start': {'string':'Start Date','type':'date','required': True},
    'date_end': {'string':'End Date','type':'date','required': True},
}


class wiz_invoice_recalc(wizard.interface):
    '''
    Wizzard recalc taxes for error in the behaviour of group taxes
    '''
    def _recalc_taxes(self, cr, uid, data, context):
        d1=data['form']['date_start']
        d2=data['form']['date_end']
        invoice_obj = pooler.get_pool(cr.dbname).get('account.invoice')
        invoices = invoice_obj.search(cr, uid, [('date_invoice', '<=', d2), ('date_invoice', '>=', d1)])
        for inv in invoice_obj.browse(cr,uid,invoices):
            invoice_obj.button_compute(cr,uid,[inv.id],{},set_total=True)
            print "RECALCULADA.........",inv.id
        return True
    
    states = {
        'init' : {
            'actions' : [],
            'result' : {'type' : 'form',
                    'arch' : book_form,
                    'fields' : book_field,
                    'state' : [('end', 'Cancel','gtk-cancel'),('compute_taxes', 'Execute Update','gtk-print') ]}
        },
        'compute_taxes' : {
            'actions' : [],
            'result' : {'type' : 'action',
                        'action': _recalc_taxes,
                    'state' : 'end'}
        },
    }
wiz_invoice_recalc("fiscal.recalc.taxes")
