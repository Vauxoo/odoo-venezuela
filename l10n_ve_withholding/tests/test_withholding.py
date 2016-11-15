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


class TestFiscalRequirements(TransactionCase):
    """ Test of Fiscal Requirements """

    def setUp(self):
        """Seudo-constructor method"""
        super(TestFiscalRequirements, self).setUp()
        self.invoice_obj = self.env['account.invoice']
        self.invoice_line_obj = self.env['account.invoice.line']
        self.period_obj = self.env['account.period']
        self.partner_amd = self.env.ref(
            'l10n_ve_fiscal_requirements.f_req_partner_2')
        self.product_ipad = self.env.ref(
            'product.product_product_6_product_template')
        self.tax_general = self.env.ref(
            'l10n_ve_fiscal_requirements.iva_purchase1')

    def test_01_create_supplier_invoice(self):
        """Test create supplier invoice"""
        # Create invoice supplier
        # date_now = time.strftime(DEFAULT_SERVER_DATE_FORMAT)
        invoice_dict = {
            'partner_id': self.partner_amd.id,
            'type': 'in_invoice',
            'reference_type': 'none',
            'name': 'Invoice Supplier Withholding',
            'account_id': self.partner_amd.property_account_payable.id,
        }
        invoice = self.invoice_obj.create(invoice_dict)
        # Create invoice line with tax general
        line_dict = {
            'product_id': self.product_ipad.id,
            'quantity': 1,
            'price_unit': 100,
            'name': self.product_ipad.name,
            'invoice_id': invoice.id,
            'invoice_line_tax_id': [(6, 0, [self.tax_general.id])]
        }
        self.invoice_line_obj.create(line_dict)
        # Check initial state
        self.assertEqual(
            invoice.state, 'draft', 'Initial state should be in "draft"'
        )
        # Set invoice state open
        invoice.signal_workflow('invoice_open')
        self.assertEqual(invoice.state, 'open', 'State in open')
        # Check tax invoice
        self.assertEqual(len(invoice.tax_line), 1,
                         'This invoice should be has at least one tax')
        self.assertEqual(invoice.tax_line.amount, 12.0,
                         'Tax invoice is incorrect')

    def test_02_computation_fortnights(self):
        """Test the computation of fortnights"""
        # Convert date format server to the format required
        date = str(DEFAULT_SERVER_DATE_FORMAT).split('-')
        dserver1 = '-'.join([x if 'd' not in x else '14' for x in date])
        dserver2 = '-'.join([x if 'd' not in x else '25' for x in date])
        date1 = time.strftime(dserver1)
        date2 = time.strftime(dserver2)
        # Search Fortnight
        first_fortnight = self.period_obj.find_fortnight(date1)
        second_fortnight = self.period_obj.find_fortnight(date2)
        # Check Fortnight
        self.assertEqual(first_fortnight[1], 'False',
                         'There is something wrong with the Fortnight')
        self.assertEqual(second_fortnight[1], 'True',
                         'There is something wrong with the Fortnight')
