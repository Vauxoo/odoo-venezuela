# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010 Vauxoo C.A. (http://openerp.com.ve/) All Rights Reserved.
#                    Javier Duran <javier@vauxoo.com>
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
<form string="Seniat Book">
     <field name="date_start" />
     <field name="date_end" />
     <field name="model" />

</form>
"""

book_field= {
    'date_start': {'string':'Start Date','type':'date','required': True},
    'date_end': {'string':'End Date','type':'date','required': True},
    'model':{'string':"Type of Report", 'type':'selection', 'selection':[('wh_p','Witholding Purchase'),('wh_s','Witholding Sales')]},
}


class wiz_retencion_list(wizard.interface):
    '''
    Wizzard invoice list
    '''

    states = {
        'init' : {
            'actions' : [],
            'result' : {'type' : 'form',
                    'arch' : book_form,
                    'fields' : book_field,
                    'state' : [('end', 'Cancel','gtk-cancel'),('print_report', 'Print Report','gtk-print') ]}
        },
        'print_report' : {
            'actions' : [],
            'result' : {'type' : 'print',
                   'report':'fiscal.reports.whp.whp_seniat',
                    'state' : 'end'}
        },
    }
wiz_retencion_list("fiscal.reports.whp.wh_book")
