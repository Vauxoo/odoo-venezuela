# -*- coding: utf-8 -*-
###############################################################################
#    Module Written to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############################################################################
#    Credits:
#    Coded by: Edgar Rivero <edgar@vauxoo.com>
#    Audited by: Humberto Arocha <hbto@vauxoo.com>
###############################################################################
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
from openerp.tests.common import TransactionCase
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT


class TestSplitInvoice(TransactionCase):
    """ Test of Split Invoice """

    def setUp(self):
        """Seudo-constructor method"""
        super(TestSplitInvoice, self).setUp()
        self.invoice_obj = self.env['account.invoice']
        self.invoice_line_obj = self.env['account.invoice.line']
        self.invoice_tax_obj = self.env['account.invoice.tax']
        self.period_obj = self.env['account.period']
        self.partner_amd = self.env.ref(
            'base.main_partner')
        self.product_ipad = self.env.ref(
            'product.product_product_6_product_template')
        self.company = self.env.ref(
            'base.main_company')

    def _create_invoice(self, type_inv='in_invoice'):
        """Function create invoice"""
        date_now = time.strftime(DEFAULT_SERVER_DATE_FORMAT)
        invoice_dict = {
            'partner_id': self.partner_amd.id,
            'date_invoice': date_now,
            'type': type_inv,
            'reference_type': 'none',
            'name': 'invoice supplier',
            'account_id': self.partner_amd.property_account_receivable.id,
        }
        if type_inv == 'in_invoice':
            invoice_dict['supplier_invoice_number'] = 'libre-123456'
            account = self.partner_amd.property_account_payable.id
            invoice_dict['account_id'] = account
        return self.invoice_obj.create(invoice_dict)

    def _create_invoice_line(self, invoice_id=None, tax=None):
        """Create invoice line"""
        line_dict = {
            'product_id': self.product_ipad.id,
            'quantity': 1,
            'price_unit': 100,
            'name': self.product_ipad.name,
            'invoice_id': invoice_id,
        }
        if tax:
            line_dict['invoice_line_tax_id'] = [(6, 0, [tax.id])]
        return self.invoice_line_obj.create(line_dict)

    def test_01_split_invoice(self):
        """Test create invoice customer with multiples line"""
        # Set lines_invoice to 3 for configuration split invoice in company
        self.company.write({'lines_invoice': 3})
        self.assertEqual(self.company.lines_invoice, 3, 'Should be 3')
        # Create invoice customer
        invoice = self._create_invoice('out_invoice')
        # Check initial state
        self.assertEqual(
            invoice.state, 'draft', 'Initial state should be in "draft"'
        )
        # Create invoice lines
        self._create_invoice_line(invoice.id)
        self._create_invoice_line(invoice.id)
        self._create_invoice_line(invoice.id)
        self._create_invoice_line(invoice.id)
        self._create_invoice_line(invoice.id)
        self._create_invoice_line(invoice.id)
        # Calculate taxes button
        invoice.button_reset_taxes()
        # Set invoice state open
        invoice.signal_workflow('invoice_open')
        self.assertEqual(invoice.state, 'open', 'State in open')
        # Check the lines are conrrect
        self.assertEqual(self.company.lines_invoice,
                         len(invoice.invoice_line),
                         'Number lines should be equal '
                         'configuration in company')
        # Check amount
        base = 0
        for line in invoice.invoice_line:
            base += line.price_unit * line.quantity
        self.assertEqual(invoice.amount_untaxed, base,
                         'Amount untaxed should be equal total of the lines')
        self.assertEqual(invoice.amount_total, base,
                         'Amount total incorrect')
