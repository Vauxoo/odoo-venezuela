# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Vauxoo C.A. (http://openerp.com.ve/) All Rights Reserved.
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

import wizard
import osv
import pooler
from tools.translate import _
import os

_transaction_form = '''<?xml version="1.0"?>
<form string=" Seleccione el periodo de declaracion">
     <field name="period_id"/>

</form>'''

_transaction_fields = {
    'period_id': {
        'string': 'Periodo',
        'type': 'many2one',
        'relation': 'account.period',
        'required': True
    },
   
}



def _data_save(self, cr, uid, data, context):
    pool = pooler.get_pool(cr.dbname)
    period_obj = pool.get('account.period')
    comp_obj = pool.get('account.retencion.munici')
    form = data['form']

    res = {}
    lst = []
    period = period_obj.browse(cr, uid, form['period_id'])
    comp_ids = comp_obj.search(cr, uid, [('date_ret','>=',period.date_start),('date_ret','<=',period.date_stop)])
    print 'comprobantes: ',comp_ids
    for comprobante in comp_obj.browse(cr, uid, comp_ids):
        res['rif_r'] = comprobante.partner_id.vat
        for line in comprobante.munici_line_ids:            
            res['nro'] = line.invoice_id.number
            res['ctrl'] = line.invoice_id.nro_ctrl
            res['conce'] = line.concepto_id
            res['monto'] = line.amount
            res['ptaje'] = line.retencion_munici

        lst.append(res)

    print 'resultadoxxx: ',res


        
    
#    os.system("python /home/javier/openerp/stable/5.0/base/loc_ve_29122009/retencion_munici/wizard/prueba1.py "+period.name)


    return self._csv_write(cr, uid, lst, context)

class wiz_ret_munici_xml(wizard.interface):

    def _csv_write(self, cr, uid, data, context):
        orden = [
            'rif_r',
            'nro',
            'ctrl',
            'conce',
            'monto',
            'ptaje'

        ]
        print 'data: ',data
        lt = []
        arch = []        
        for d in data:
            print 'd: ',d
            for col in orden:
                print 'col: ',col
                lt.append(d[col])

        print 'lt: ',lt
        arch.append(tuple(lt))
        print 'archxxx: ',arch

        import csv
        cw = csv.writer(open("/home/javier/openerp/stable/5.0/base/loc_ve_29122009/retencion_munici/wizard/out.csv", "wb"))
        cw.writerows(arch)
        return {}


    states = {
        'init': {
            'actions': [],
            'result': {'type': 'form', 'arch':_transaction_form, 'fields':_transaction_fields, 'state':[('end','Cancel'),('change','Realizar')]}
        },
        'change': {
            'actions': [_data_save],
            'result': {'type': 'state', 'state':'end'}
        }
    }
wiz_ret_munici_xml('account.ret.munici.xml.seniat')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

