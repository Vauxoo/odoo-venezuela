# coding: utf-8
###############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############################################################################
#    Credits:
#    Coded by:       Luis Escobar <luis@vauxoo.com>
#                    Tulio Ruiz <tulio@vauxoo.com>
#                    Katherine Zsoral <katherine.zaoral@vauxoo.com>
#    Planified by: Nhomar Hernandez
###############################################################################
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
###############################################################################
from openerp import api
from openerp.osv import fields, osv
from openerp.tools.translate import _


class AccountInvoice(osv.osv):
    _inherit = "account.invoice"

    _columns = {
        'fb_id': fields.many2one('fiscal.book', 'Fiscal Book',
                                 help='Fiscal Book where this line is '
                                 'related to'),
        'issue_fb_id': fields.many2one('fiscal.book', 'Fiscal Book',
                                       help='Fiscal Book where this invoice '
                                       'needs to be add'),
    }

    def action_cancel(self, cr, uid, ids, context=None):
        """ Verify first in the invoice have a fiscal book associated and if
        the state of the book is in cancel. """
        context = context or {}
        for inv_brw in self.browse(cr, uid, ids, context=context):
            if (not inv_brw.fb_id or
                    (inv_brw.fb_id and inv_brw.fb_id.state == 'cancel')):
                super(AccountInvoice, self).action_cancel(cr, uid, ids,
                                                          context=context)
            else:
                raise osv.except_osv(
                    _("Error!"),
                    _("You can't cancel an invoice that is loaded in a"
                      " processed Fiscal Book (%s). You need to go to"
                      " Fiscal Book and set the book to Cancel. Then you"
                      " could be able to cancel the invoice." % (
                          inv_brw.fb_id.state,)))
        return True

    @api.multi
    def copy(self, default=None):
        """
        Overwrite the copy orm method to blank the fiscal book field when
        a invoice is copy. Also if a invoice have benn remove from a fiscal
        book the issue_fb_id is add, if a duplicate this invoice that info os
        issue will be garbage so I clean it too.
        """
        # NOTE: Use as parameter 'ids' instead of 'id' for fix pylint W0622
        # Redefining built-in 'id'.
        if default is None:
            default = {}
        default = default.copy()
        default.update({'fb_id': False})
        if default.get('issue_fb_id', False):
            default.update({'issue_fb_id': False})
        return super(AccountInvoice, self).copy(default)
