# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


from openerp.osv import osv


class account_invoice_refund(osv.osv_memory):

    """Refunds invoice"""
    _inherit = 'account.invoice.refund'

    def validate_wh(self, cr, uid, ids, context=None):
        """ Method that validate if invoice has non-yet processed VAT withholds.
        return: True: if invoice is does not have wh's or it does have and
                    those ones are validated.
                False: if invoice is does have and those wh's are not yet
                    validated.
        """
        if context is None:
            context = {}
        res = []
        inv_obj = self.pool.get('account.invoice')

        res.append(super(account_invoice_refund, self).validate_wh(
            cr, uid, ids, context=context))
        res.append(inv_obj.validate_wh_iva_done(cr, uid, ids, context=context))
        return all(res)

account_invoice_refund()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
