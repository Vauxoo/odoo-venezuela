# coding: utf-8
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############################################################################
#    Credits:
#    Coded by: Vauxoo C.A.
#    Planified by: Nhomar Hernandez
#    Audited by: Vauxoo C.A.
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
###############################################################################

from openerp.osv import fields, osv


class AccountJournal(osv.osv):
    _inherit = 'account.journal'

    _columns = {
        'type': fields.selection(
            [('sale', 'Sale'), ('sale_refund', 'Sale Refund'),
             ('purchase', 'Purchase'), ('purchase_refund', 'Purchase Refund'),
             ('cash', 'Cash'), ('bank', 'Bank and Cheques'),
             ('general', 'General'),
             ('situation', 'Opening/Closing Situation'),
             ('sale_debit', 'Sale Debit'),
             ('purchase_debit', 'Purchase Debit')],
            'Type', size=32, required=True,
            help="Select 'Sale' for customer invoices journals."
                 " Select 'Purchase' for supplier invoices journals."
                 " Select 'Cash' or 'Bank' for journals that are used in"
                 " customer or supplier payments."
                 " Select 'General' for miscellaneous operations journals."
                 " Select 'Opening/Closing Situation' for entries generated"
                 " for new fiscal years."
                 " Select 'Sale Debit' for customer debit note journals."
                 " Select 'Purchase Debit' for supplier debit note journals.")
    }
