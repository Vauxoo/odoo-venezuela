# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
# Credits######################################################
#    Coded by: Humberto Arocha           <humberto@openerp.com.ve>
#              Maria Gabriela Quilarque  <gabriela@vauxoo.com>
#    Planified by: Nhomar Hernandez
#    Finance by: Helados Gilda, C.A. http://heladosgilda.com.ve
#    Audited by: Humberto Arocha humberto@openerp.com.ve
#############################################################################
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
##############################################################################
import time

from openerp.addons import decimal_precision as dp
from openerp.osv import fields, osv


class l10n_ut(osv.osv):

    _name = 'l10n.ut'
    _description = 'Tax Unit'
    _order = 'date desc'
    _columns = {
        'name': fields.char(
            'Reference number', size=64, required=True, readonly=False,
            help="Reference number under the law"),
        'date': fields.date(
            'Date', required=True,
            help="Date on which goes into effect the new Unit Tax Unit"),
        'amount': fields.float(
            'Amount', digits_compute=dp.get_precision('Amount Bs per UT'),
            help="Amount of the tax unit in bs", required=True),
        'user_id': fields.many2one(
            'res.users', 'Salesman',
            readonly=True, states={'draft': [('readonly', False)]},
            help="Vendor user"),
    }
    _defaults = {
        'name': lambda *a: None,
        'user_id': lambda s, cr, u, c: u,
    }

    def get_amount_ut(self, cr, uid, date=False, *args):
        """ Return the value of
        the tributary unit of the specified date or
        if it's empty return the value to current
        date.
        """
        rate = 0
        date = date or time.strftime('%Y-%m-%d')
        cr.execute("""SELECT amount FROM l10n_ut WHERE date <= '%s'
                   ORDER BY date desc LIMIT 1""" % (date))
        if cr.rowcount:
            rate = cr.fetchall()[0][0]
        return rate

    def compute(self, cr, uid, from_amount, date=False, context=None):
        """ Return the number of tributary
        units depending on an amount of money.
        """
        if context is None:
            context = {}
        result = 0.0
        ut = self.get_amount_ut(cr, uid, date=date)
        if ut:
            result = from_amount / ut
        return result

    def compute_ut_to_money(self, cr, uid, amount_ut, date=False,
                            context=None):
        """ Transforms from tax units into money
        """
        if context is None:
            context = {}
        money = 0.0
        ut = self.get_amount_ut(cr, uid, date)
        if ut:
            money = amount_ut * ut
        return money

    def exchange(self, cr, uid, from_amount, from_currency_id, to_currency_id,
                 exchange_date, context=None):
        context = context or {}
        if from_currency_id == to_currency_id:
            return from_amount
        rc_obj = self.pool.get('res.currency')
        context['date'] = exchange_date
        return rc_obj.compute(cr, uid, from_currency_id, to_currency_id,
                              from_amount, context=context)

    def sxc(self, cr, uid, from_currency_id, to_currency_id, exchange_date,
            context=None):
        '''
        This is a clousure that allow to use the exchange rate conversion in a
        short way
        '''
        context = context or {}

        def _xc(from_amount):
            return self.exchange(cr, uid, from_amount, from_currency_id,
                                 to_currency_id, exchange_date,
                                 context=context)
        return _xc
