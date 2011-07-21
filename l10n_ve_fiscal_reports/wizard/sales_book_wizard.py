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
