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
from openerp.exceptions import except_orm


class TestSRCWithholding(TransactionCase):
    """ Test of withholding social responsability commitment"""

    def setUp(self):
        """Seudo-constructor method"""
        super(TestSRCWithholding, self).setUp()
        self.doc_obj = self.env['account.wh.src']
        self.doc_line_obj = self.env['account.wh.src.line']
        self.invoice_obj = self.env['account.invoice']
        self.invoice_line_obj = self.env['account.invoice.line']
        self.period_obj = self.env['account.period']
        self.rates_obj = self.env['res.currency.rate']
        self.partner_amd = self.env.ref(
            'l10n_ve_fiscal_requirements.f_req_partner_2')
        self.partner_nwh = self.env.ref(
            'l10n_ve_fiscal_requirements.f_req_partner_7')
        self.product_ipad = self.env.ref(
            'product.product_product_6_product_template')
        self.tax_general = self.env.ref(
            'l10n_ve_fiscal_requirements.iva_purchase1')
        self.tax_except = self.env.ref(
            'l10n_ve_fiscal_requirements.iva_purchase3')
        self.tax_s_12 = self.env.ref(
            'l10n_ve_fiscal_requirements.iva_sale1')
        self.tax_s_0 = self.env.ref(
            'l10n_ve_fiscal_requirements.iva_sale3')
        self.company = self.env.ref(
            'base.main_partner')

    def _create_invoice(self, type_inv='in_invoice'):
        """Function create invoice"""
        date_now = time.strftime(DEFAULT_SERVER_DATE_FORMAT)
        invoice_dict = {
            'partner_id': self.partner_amd.id,
            'nro_ctrl': '2000-694351',
            'date_invoice': date_now,
            'date_document': date_now,
            'type': type_inv,
            'reference_type': 'none',
            'name': 'invoice iva supplier',
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

    def test_01_validate_process_withholding_src_supplier(self):
        """Test create invoice supplier with data initial and
        Test validate invoice with document withholding SRC"""
        # Create invoice supplier
        invoice = self._create_invoice('in_invoice')
        # Check initial state
        self.assertEqual(
            invoice.state, 'draft', 'Initial state should be in "draft"'
        )
        # Create invoice line with tax general
        self._create_invoice_line(invoice.id, self.tax_general)
        # Set invoice state open
        invoice.signal_workflow('invoice_open')
        self.assertEqual(invoice.state, 'open', 'State in open')
        self.assertEqual(invoice.wh_src_id, self.doc_obj,
                         'Should be empty the withholding document')
        # Create document withholding src
        acc_id = self.doc_obj.onchange_partner_id('in_invoice',
                                                  self.partner_amd.id)
        value = {
            'name': 'Test Account Withholding SRC',
            'type': 'in_invoice',
            'partner_id': self.partner_amd.id,
            'account_id': acc_id['value']['account_id'],
            'number': 'SRC-123456'
        }
        wh_src = self.doc_obj.create(value)
        # Test confirm document withholding SRC
        with self.assertRaisesRegexp(
            except_orm,
            "'Invalid Procedure!', 'No retention lines'"
        ):
            wh_src.action_confirm()
        # Check state withholding municipal
        self.assertEqual(wh_src.state, 'draft', 'State should be draft')
        # Create withholding muncipal SRC
        res = self.doc_line_obj.onchange_invoice_id('in_invoice',
                                                    invoice_id=invoice.id)
        wh_src_rate = res['value']['wh_src_rate']
        amount = res['value']['base_amount']
        wh_amount = res['value']['wh_amount']
        line = {
            'name': 'Test withholding municipal line',
            'invoice_id': invoice.id,
            'wh_src_rate': wh_src_rate,
            'base_amount': amount,
            'wh_id': wh_src.id,
            'wh_amount': wh_amount
        }
        self.doc_line_obj.create(line)
        # Test confirm document withholding SRC
        with self.assertRaisesRegexp(
            except_orm,
            "'Invalid Procedure!', 'Check the amount of withholdings'"
        ):
            wh_src.action_confirm()
        # Update wh_amount
        wh_src.write({'wh_amount': wh_amount})
        # Set state confirmed in withholding SRC
        wh_src.signal_workflow('wh_src_confirmed')
        self.assertEqual(wh_src.state, 'confirmed',
                         'State should be confirmed')
        # Set state done in withholding SRC
        wh_src.signal_workflow('wh_src_done')
        self.assertEqual(wh_src.state, 'done',
                         'State should be done')
        # Check line in withholding SRC
        self.assertEqual(len(wh_src.line_ids), 1, 'Should exist a record')
        # Test invoice copy, check d is False,
        # and not create document withholding SRC
        invoice_c = invoice.copy()
        self.assertEqual(invoice_c.wh_src, False,
                         'WH_SRC should be False')
        self.assertEqual(invoice_c.wh_src_rate, 0.0,
                         'WH_SRC_RATE should be 0.0')
        self.assertEqual(invoice_c.wh_src_id, self.doc_obj,
                         'Withholding document the invoice copy'
                         'should be empty')

        # Check payment in invoice related with withholding SRC
        self.assertEqual(len(invoice.payment_ids), 1, 'Should exits a payment')
        self.assertEqual(invoice.residual,
                         invoice.amount_total - wh_amount,
                         'Amount residual invoice should be equal amount '
                         'total - amount wh')
        debit = 0
        credit = 0
        for doc_inv in wh_src.line_ids:
            for line in doc_inv.move_id.line_id:
                if line.debit > 0:
                    debit += line.debit
                    self.assertEqual(line.account_id.id, invoice.account_id.id,
                                     'Account should be equal to account '
                                     'invoice')
                else:
                    credit += line.credit
                    account = wh_src.company_id.wh_src_collected_account_id
                    self.assertEqual(line.account_id.id,
                                     account.id,
                                     'Account should be equal to account '
                                     'tax for withholding')
        self.assertEqual(debit, credit, 'Debit and Credit should be equal')
        self.assertEqual(debit, wh_amount,
                         'Amount total withholding should be equal '
                         'journal entrie')

    def test_02_validate_process_withholding_src_customer(self):
        """Test create invoice customer with data initial and
        Test validate invoice with document withholding SRC"""
        # Create invoice customer
        invoice = self._create_invoice('out_invoice')
        # Check initial state
        self.assertEqual(
            invoice.state, 'draft', 'Initial state should be in "draft"'
        )
        # Create invoice line with tax general
        self._create_invoice_line(invoice.id, self.tax_s_12)
        # Set invoice state open
        invoice.signal_workflow('invoice_open')
        self.assertEqual(invoice.state, 'open', 'State in open')
        self.assertEqual(invoice.wh_src_id, self.doc_obj,
                         'Should be empty the withholding document')
        # Create document withholding src
        acc_id = self.doc_obj.onchange_partner_id('out_invoice',
                                                  self.partner_amd.id)
        value = {
            'name': 'Test Account Withholding SRC',
            'type': 'out_invoice',
            'partner_id': self.partner_amd.id,
            'account_id': acc_id['value']['account_id'],
            'number': 'SRC-123456'
        }
        wh_src = self.doc_obj.create(value)
        # Test confirm document withholding SRC
        with self.assertRaisesRegexp(
            except_orm,
            "'Invalid Procedure!', 'No retention lines'"
        ):
            wh_src.action_confirm()
        # Check state withholding municipal
        self.assertEqual(wh_src.state, 'draft', 'State should be draft')
        # Create withholding muncipal SRC
        res = self.doc_line_obj.onchange_invoice_id('out_invoice',
                                                    invoice_id=invoice.id)
        wh_src_rate = res['value']['wh_src_rate']
        amount = res['value']['base_amount']
        wh_amount = res['value']['wh_amount']
        line = {
            'name': 'Test withholding municipal line',
            'invoice_id': invoice.id,
            'wh_src_rate': wh_src_rate,
            'base_amount': amount,
            'wh_id': wh_src.id,
            'wh_amount': wh_amount
        }
        self.doc_line_obj.create(line)
        # Test confirm document withholding SRC
        with self.assertRaisesRegexp(
            except_orm,
            "'Invalid Procedure!', 'Check the amount of withholdings'"
        ):
            wh_src.action_confirm()
        # Update wh_amount
        wh_src.write({'wh_amount': wh_amount})
        # Set state confirmed in withholding SRC
        wh_src.signal_workflow('wh_src_confirmed')
        self.assertEqual(wh_src.state, 'confirmed',
                         'State should be confirmed')
        # Set state done in withholding SRC
        wh_src.signal_workflow('wh_src_done')
        self.assertEqual(wh_src.state, 'done',
                         'State should be done')
        # Check line in withholding SRC
        self.assertEqual(len(wh_src.line_ids), 1, 'Should exist a record')
        # Test invoice copy, check d is False,
        # and not create document withholding SRC
        invoice_c = invoice.copy()
        self.assertEqual(invoice_c.wh_src, False,
                         'WH_SRC should be False')
        self.assertEqual(invoice_c.wh_src_rate, 0.0,
                         'WH_SRC_RATE should be 0.0')
        self.assertEqual(invoice_c.wh_src_id, self.doc_obj,
                         'Withholding document the invoice copy'
                         'should be empty')

        # Check payment in invoice related with withholding SRC
        self.assertEqual(len(invoice.payment_ids), 1, 'Should exits a payment')
        self.assertEqual(invoice.residual,
                         invoice.amount_total - wh_amount,
                         'Amount residual invoice should be equal amount '
                         'total - amount wh')
        debit = 0
        credit = 0
        for doc_inv in wh_src.line_ids:
            for line in doc_inv.move_id.line_id:
                if line.debit > 0:
                    debit += line.debit
                    account = wh_src.company_id.wh_src_paid_account_id
                    self.assertEqual(line.account_id.id,
                                     account.id,
                                     'Account should be equal to account '
                                     'src for withholding')
                else:
                    credit += line.credit
                    self.assertEqual(line.account_id.id, invoice.account_id.id,
                                     'Account should be equal to account '
                                     'invoice')
        self.assertEqual(debit, credit, 'Debit and Credit should be equal')
        self.assertEqual(debit, wh_amount,
                         'Amount total withholding should be equal '
                         'journal entrie')
