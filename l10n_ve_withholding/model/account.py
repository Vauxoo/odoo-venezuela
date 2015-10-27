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

import time

from openerp.osv import fields, osv
from openerp.tools.translate import _

__TYPES__ = [
    ('sale', 'Sale'),
    ('sale_refund', 'Sale Refund'),
    ('purchase', 'Purchase'),
    ('purchase_refund', 'Purchase Refund'),
    ('cash', 'Cash'),
    ('bank', 'Bank and Cheques'),
    ('general', 'General'),
    ('situation', 'Opening/Closing Situation'),
    ('sale_debit', 'Sale Debit'),
    ('purchase_debit', 'Purchase Debit'),
    ('iva_sale', 'Sale Wh VAT'),
    ('iva_purchase', 'Purchase Wh VAT'),
    ('islr_purchase', 'Purchase Wh Income'),
    ('islr_sale', 'Sale Wh Income'),
    ('mun_sale', 'Sale Wh County'),
    ('mun_purchase', 'Purchase Wh County'),
    ('src_sale', 'Sale Wh src'),
    ('src_purchase', 'Purchase Wh src')]


class AccountJournal(osv.osv):
    _inherit = 'account.journal'

    _columns = {
        'type': fields.selection(
            __TYPES__, 'Type', size=32, required=True,
            help="Select 'Sale' for customer invoices journals."
                 " Select 'Purchase' for supplier invoices journals."
                 " Select 'Cash' or 'Bank' for journals that are used in"
                 " customer or supplier payments."
                 " Select 'General' for miscellaneous operations journals."
                 " Select 'Opening/Closing Situation' for entries generated"
                 " for new fiscal years."
                 " Select 'Sale Debit' for customer debit note journals."
                 " Select 'Purchase Debit' for supplier debit note journals."
                 " Select 'Sale Wh VAT' for customer vat withholding journals."
                 " Select 'Purchase Wh VAT' for supplier vat withholding"
                 " journals."
                 " Select 'Sale Wh Income' for customer income withholding"
                 " journals."
                 " Select 'Purchase Wh Income' for supplier income withholding"
                 " journals."
                 " Select 'Sale Wh County' for customer municipal withholding"
                 " journals."
                 " Select 'Purchase Wh County' for supplier municipal"
                 " withholding journals."
                 " Select 'Sale Wh SRC' for customer social withholding"
                 " journals."
                 " Select 'Purchase Wh SRC' for supplier social withholding"
                 " journals.")
    }

AccountJournal()


class AccountPeriod(osv.osv):
    _inherit = "account.period"

    def _find_fortnight(self, cr, uid, date=None, context=None):
        """ This Function returns a tuple composed of
            *) period for the asked dt (int)
            *) fortnight for the asked dt (boolean):
                -) False: for the 1st. fortnight
                -) True: for the 2nd. fortnight.
            Example:
            (3,True) => a period whose id is 3 in the second fortnight
        """
        if context is None:
            context = {}
        if not date:
            date = time.strftime('%Y-%m-%d')
        period_ids = self.find(cr, uid, date, context=context)
        do = [('special', '=', False), ('id', 'in', period_ids)]
        # Due to the fact that demo data for periods sets 'special' as True on
        # them, this little hack is necesary if this issue is solved we should
        # ask directly for the refer to this bug for more information
        # https://bugs.launchpad.net/openobject-addons/+bug/924200
        demo_enabled = self.pool.get('ir.module.module').search(
            cr, uid, [('name', '=', 'base'), ('demo', '=', True)])
        domain = demo_enabled and [do[1]] or do
        # End of hack, dear future me I am really sorry for this....
        period_ids = self.search(cr, uid, domain, context=context)
        if not period_ids:
            raise osv.except_osv(
                _('Error looking Fortnight !'),
                _('There is no "Special" period defined for this date: %s.')
                % date)

        fortnight = (False if time.strptime(date, '%Y-%m-%d').tm_mday <= 15
                     else True)
        return (period_ids[0], fortnight)

    def find_fortnight(self, cr, uid, date=None, context=None):
        """
        Get the period and the fortnoght that correspond to the given dt date.
        @return a tuple( int(period_id), str(fortnight) )
        """
        # TODO: fix this workaround in version 8.0 [hbto notes]
        context = context or {}
        period, fortnight = self._find_fortnight(cr, uid, date=date,
                                                 context=context)
        return period, str(fortnight)
