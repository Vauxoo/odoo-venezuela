# -*- encoding: utf-8 -*-
##############################################################################
# Copyright (c) 2011 OpenERP Venezuela (http://openerp.com.ve)
# All Rights Reserved.
# Programmed by: Israel Fermín Montilla  <israel@openerp.com.ve>
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
###############################################################################
from osv import osv
from osv import fields
import sys
from tools.translate import _
import time

class sales_book_wizard(osv.osv_memory):
    """
    Sales book wizard implemented using the osv_memory wizard system
    """
    _name = "sales.book.wizard"


    def _get_account_period(self, cr, uid, dt=None, context=None):
        if not dt:
            dt = time.strftime('%Y-%m-%d')
        ids = self.pool.get('account.period').search(cr, uid, [('date_start','<=',dt),('date_stop','>=',dt)])
        if not ids:
            raise osv.except_osv(_('Error !'), _('No period defined for this date !\nPlease create a fiscal year.'))
        return ids

    def _same_account_period(self, cr, uid, admin_date, account_date, context=None):
        return self._get_account_period(cr, uid, admin_date, context) == self._get_account_period(cr, uid, account_date, context)

    def _do_purchase_report(self, cr, uid, data, context=None):
        """
        This method should be overriden to generate the SENIAT purchase report
        """
        return False

    def _get_needed_data(self, cr, uid, data, context=None):
        if data['type'] == 'sale':
            data_list_view = self._gen_wh_sales_list(cr, data['date_start'], data['date_end'])
            inv_obj = self.pool.get('account.invoice')
            inv_ids = inv_obj.search(cr, uid, [('date_invoice', '>=', data['date_start']), 
                                                ('date_invoice', '<=', data['date_end']),
                                                ('type', '=', 'out_invoice')])
            inv_rd = inv_obj.read(cr, uid, inv_ids, context)
            inv_browse = inv_obj.browse(cr, uid, inv_ids, context)
            control_numbers = range(data['control_start'], data['control_end'] + 1)
            return (data_list_view, inv_rd, control_numbers, inv_browse)
        else: # TODO: when it is purchase
             pass

    def _get_missing_inv_numbers(self, sequence, numbers_found):
        return set(set(sequence) ^ set(numbers_found))

    def _check_retention(self, all_data, retention_number):
        for element in all_data:
            if retention_number in element:
                return True
            return False

    def _do_new_record(self, control, inv_browse):
        invoice = [i for i in inv_browse if i.nro_ctrl == control][0]
        amount = (invoice.amount_tax * invoice.p_ret) / 100
        return (invoice.date_invoice, 
                invoice.date_document, 
                invoice.partner_id.vat, 
                invoice.partner_id.id, 
                invoice.number,
                invoice.nro_ctrl,
                amount,
                invoice.partner_id.name)

    def _do_sale_report(self, cr, uid, data, context=None):
        """
        This method generates the SENIAT sales book report
        """
        data_list, inv_rd, control_numbers, inv_browse = self._get_needed_data(cr, uid, data, context)
        inv_numbers = [int(n['number']) for n in inv_rd]
        missing_numbers = self._get_missing_inv_numbers(control_numbers, inv_numbers)
        for number in missing_numbers:
            inv_rd.append({'number': str(number)})
        for inv in inv_rd:
            if inv.has_key('date_document'):
                if self._same_account_period(cr, uid, inv['date_document'], inv['date_invoice'], context):
                    if inv.has_key('nro_ctrl') and not self._check_retention(data_list, inv['nro_ctrl']):
                        data_list.append(self._do_new_record(inv['nro_ctrl'], inv_browse))
                else:
                    if inv.has_key('nro_ctrl'):
                        data_list.append(self._do_new_record(inv['nro_ctrl'], inv_browse))
        data_list = self._date_sort(data_list)
        return False
    
    # sorting by bubblesort because quicksort exceeds recursion limit
    def _date_sort(self, data):
        _sorted = False
        while _sorted == False:
            for cont in range(0, len(data) - 1):
                _sorted = True
                if data[cont][1] > data[cont + 1][1]:
                    _sorted = False
                    data[cont], data[cont + 1] = (data[cont + 1], data[cont]) # swap
            if _sorted == True:
                break
        return data

    def do_report(self, cr, uid, ids, context=None):
        my_data = self.read(cr, uid, ids)[0]
        if my_data['type'] == 'sale':
            self._do_sale_report(cr, uid, my_data)
        else:
            self._do_purchase_report(cr, uid, my_data)
        return False


    def check_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        data = {}
        data['ids'] = context.get('active_ids', [])
        data['model'] = context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(cr, uid, ids, ['date_start',  'date_end',  'control_start', 'control_end', 'type'])[0]
        return self._print_report(cr, uid, ids, data, context=context)


    def _print_report(self, cr, uid, ids, data, context=None):
        return { 'type': 'ir.actions.report.xml', 'report_name': 'fiscal.reports.purchase.purchase_seniat', 'datas': data}
    _columns = {
            "date_start": fields.date("Start Date", required=True),
            "date_end": fields.date("End Date", required=True),
            "control_start": fields.integer("Control Start"),
            "control_end": fields.integer("Control End"),
            "type": fields.selection([
                        ("sale", _("Sale")),
                        ("purchase", _("Purchase")),
                    ],"Type", required=True,
                ),
        }
    _defaults = {
        'date_start': lambda *a: time.strftime('%Y-%m-%d'),
        'date_end': lambda *a: time.strftime('%Y-%m-%d'),
        'type': lambda *a: 'sale',
    }
sales_book_wizard()
