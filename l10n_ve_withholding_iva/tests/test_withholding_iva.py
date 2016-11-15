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
# from datetime import datetime, timedelta
from openerp.tests.common import TransactionCase
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from openerp.exceptions import except_orm, ValidationError
# from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT


class TestIvaWithholding(TransactionCase):
    """ Test of withholding IVA """

    def setUp(self):
        """Seudo-constructor method"""
        super(TestIvaWithholding, self).setUp()
        self.doc_obj = self.env['account.wh.iva']
        self.doc_line_obj = self.env['account.wh.iva.line']
        self.invoice_obj = self.env['account.invoice']
        self.invoice_line_obj = self.env['account.invoice.line']
        self.period_obj = self.env['account.period']
        self.rates_obj = self.env['res.currency.rate']
        self.txt_iva_obj = self.env['txt.iva']
        self.txt_line_obj = self.env['txt.iva.line']
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

    def test_01_validate_process_withholding_iva(self):
        """Test create invoice supplier with data initial and
        Test validate invoice with document withholding iva"""
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
        self.assertNotEqual(invoice.wh_iva_id, self.doc_obj,
                            'Not should be empty the withholding document')
        # Test invoice copy, check wh_iva is False, vat_apply is False
        # and not create document withholding vat
        invoice_c = invoice.copy()
        self.assertEqual(invoice_c.wh_iva, False, 'WH_IVA should be False')
        self.assertEqual(invoice_c.vat_apply, False,
                         'Vat Apply should be False')
        self.assertEqual(invoice_c.wh_iva_id, self.doc_obj,
                         'Withholding document the invoice copy'
                         'should be empty')

        iva_wh = invoice.wh_iva_id
        # Test document withholding vat, check state, line and amounts
        self.assertEqual(iva_wh.state, 'draft',
                         'State of withholding should be in draft')
        self.assertEqual(len(iva_wh.wh_lines), 1, 'Should exist a record')
        self.assertEqual(iva_wh.amount_base_ret, 100.00,
                         'Amount total should be 100.00')
        self.assertEqual(iva_wh.total_tax_ret, 9.00,
                         'Amount total should be 9.00')

        # Set state document withholding iva confirmed and check state
        iva_wh.signal_workflow('wh_iva_confirmed')
        self.assertEqual(iva_wh.state, 'confirmed',
                         'State of withholding should be in confirmed')
        # Set state document withholding iva done and check state
        iva_wh.signal_workflow('wh_iva_done')
        self.assertEqual(iva_wh.state, 'done',
                         'State of withholding should be in done')
        # Check payment in invoice related with withholding iva
        self.assertEqual(len(invoice.payment_ids), 1, 'Should exits a payment')
        self.assertEqual(invoice.residual,
                         invoice.amount_total - iva_wh.total_tax_ret,
                         'Amount residual invoice should be equal amount '
                         'total - amount wh')
        debit = 0
        credit = 0
        for doc_inv in iva_wh.wh_lines:
            for line in doc_inv.move_id.line_id:
                if line.debit > 0:
                    debit += line.debit
                    self.assertEqual(line.account_id.id, invoice.account_id.id,
                                     'Account should be equal to account '
                                     'invoice')
                else:
                    credit += line.credit
                    account = self.tax_general.wh_vat_collected_account_id
                    self.assertEqual(line.account_id.id,
                                     account.id,
                                     'Account should be equal to account '
                                     'tax for withholding')
        self.assertEqual(debit, credit, 'Debit and Credit should be equal')
        self.assertEqual(debit, iva_wh.total_tax_ret,
                         'Amount total withholding should be equal '
                         'journal entries')

    def test_02_withholding_partner_not_agent(self):
        """Test withholding with partner not agent"""
        # Create invoice supplier with partner no agent
        date_now = time.strftime(DEFAULT_SERVER_DATE_FORMAT)
        invoice_dict = {
            'partner_id': self.partner_nwh.id,
            'nro_ctrl': '2000-694351',
            'date_invoice': date_now,
            'date_document': date_now,
            'type': 'in_invoice',
            'reference_type': 'none',
            'name': 'invoice iva supplier',
            'account_id': self.partner_nwh.property_account_payable.id,
        }
        invoice = self.invoice_obj.create(invoice_dict)
        # Create invoice line
        line_dict = {
            'product_id': self.product_ipad.id,
            'quantity': 1,
            'price_unit': 100,
            'name': self.product_ipad.name,
            'invoice_id': invoice.id,
            'invoice_line_tax_id': [(6, 0, [self.tax_general.id])],
        }
        self.invoice_line_obj.create(line_dict)
        # Set state open in invoice
        invoice.signal_workflow('invoice_open')
        # Check state invoice
        iva_wh = invoice.wh_iva_id
        self.assertEqual(invoice.state, 'open', 'State in open')
        # Check document withholding iva created
        self.assertNotEqual(invoice.wh_iva_id, self.doc_obj,
                            'Not should be empty the withholding document')

        self.assertEqual(iva_wh.state, 'draft',
                         'State of withholding should be in draft')
        self.assertEqual(len(iva_wh.wh_lines), 1, 'Should exist a record')
        self.assertEqual(iva_wh.amount_base_ret, 100.00,
                         'Amount total should be 100.00')
        self.assertEqual(iva_wh.total_tax_ret, 12.00,
                         'Amount total should be 12.00')

    def test_03_not_withholding_partner_not_agent(self):
        """Test not withholding with partner not agent"""
        # Create invoice supplier with partner no agent
        date_now = time.strftime(DEFAULT_SERVER_DATE_FORMAT)
        invoice_dict = {
            'partner_id': self.partner_nwh.id,
            'nro_ctrl': '2000-694351',
            'date_invoice': date_now,
            'date_document': date_now,
            'type': 'in_invoice',
            'reference_type': 'none',
            'name': 'invoice iva supplier',
            'account_id': self.partner_nwh.property_account_payable.id,
        }
        invoice = self.invoice_obj.create(invoice_dict)
        # Create invoice line
        line_dict = {
            'product_id': self.product_ipad.id,
            'quantity': 1,
            'price_unit': 100,
            'name': self.product_ipad.name,
            'invoice_id': invoice.id,
            'invoice_line_tax_id': [(6, 0, [self.tax_except.id])],
        }
        self.invoice_line_obj.create(line_dict)
        # Set state open in invoice
        invoice.signal_workflow('invoice_open')
        # Check that no document has been created
        self.assertEqual(invoice.state, 'open', 'State in open')
        self.assertEqual(invoice.wh_iva_id, self.doc_obj,
                         'Should be empty the withholding document')

    def test_04_not_withholding_company_not_agent(self):
        """Test not withholding with company not agent, partner not agent"""
        # Set company no agent withholding
        self.company.write({'wh_iva_agent': False})
        self.assertEqual(self.company.wh_iva_agent, False, 'Should be False')
        # Create invoice supplier with partner no agent
        date_now = time.strftime(DEFAULT_SERVER_DATE_FORMAT)
        invoice_dict = {
            'company_id': self.company.id,
            'partner_id': self.partner_nwh.id,
            'nro_ctrl': '2000-694351',
            'date_invoice': date_now,
            'date_document': date_now,
            'type': 'in_invoice',
            'reference_type': 'none',
            'name': 'invoice iva supplier',
            'account_id': self.partner_nwh.property_account_payable.id,
        }
        invoice = self.invoice_obj.create(invoice_dict)
        # Create invoice line
        line_dict = {
            'product_id': self.product_ipad.id,
            'quantity': 1,
            'price_unit': 100,
            'name': self.product_ipad.name,
            'invoice_id': invoice.id,
            'invoice_line_tax_id': [(6, 0, [self.tax_except.id])],
        }
        self.invoice_line_obj.create(line_dict)
        # Set state open in invoice
        invoice.signal_workflow('invoice_open')
        # Check that no document has been created
        self.assertEqual(invoice.state, 'open', 'State in open')
        self.assertEqual(invoice.wh_iva_id, self.doc_obj,
                         'Should be empty the withholding document')

    def test_05_not_withholding_company_not_agent_partner_agent(self):
        """Test not withholding with company not agent, partner agent"""
        # Set company no agent withholding
        self.company.write({'wh_iva_agent': False})
        self.assertEqual(self.company.wh_iva_agent, False, 'Should be False')
        # Create invoice supplier with partner no agent
        date_now = time.strftime(DEFAULT_SERVER_DATE_FORMAT)
        invoice_dict = {
            'company_id': self.company.id,
            'partner_id': self.partner_amd.id,
            'nro_ctrl': '2000-694351',
            'date_invoice': date_now,
            'date_document': date_now,
            'type': 'in_invoice',
            'reference_type': 'none',
            'name': 'invoice iva supplier',
            'account_id': self.partner_amd.property_account_payable.id,
        }
        invoice = self.invoice_obj.create(invoice_dict)
        # Create invoice line
        line_dict = {
            'product_id': self.product_ipad.id,
            'quantity': 1,
            'price_unit': 100,
            'name': self.product_ipad.name,
            'invoice_id': invoice.id,
            'invoice_line_tax_id': [(6, 0, [self.tax_general.id])],
        }
        self.invoice_line_obj.create(line_dict)
        # Set state open in invoice
        invoice.signal_workflow('invoice_open')
        # Check that no document has been created
        self.assertEqual(invoice.state, 'open', 'State in open')
        self.assertEqual(invoice.wh_iva_id, self.doc_obj,
                         'Should be empty the withholding document')

    def test_06_txt_document_iva(self):
        """Test create document txt vat"""
        # Create document txt iva
        date_now = time.strftime(DEFAULT_SERVER_DATE_FORMAT)
        txt_dict = {
            'date_start': date_now,
            'date_end': date_now,
        }
        txt_iva = self.txt_iva_obj.create(txt_dict)
        # Check state draft txt and txt has no line
        self.assertEqual(txt_iva.state, 'draft', 'State should be draft')
        self.assertEqual(txt_iva.txt_ids, self.txt_line_obj,
                         'Txt not should be lines')
        # Test set state confirm document txt
        with self.assertRaisesRegexp(
            except_orm,
            "('Missing Values !', 'Missing VAT TXT Lines!!!')"
        ):
            txt_iva.action_confirm()
        # Create invoice supplier
        invoice = self._create_invoice('in_invoice')
        self.assertEqual(
            invoice.state, 'draft', 'Initial state should be in "draft"'
        )
        # Create invoice line
        self._create_invoice_line(invoice.id, self.tax_general)
        # Set state open in invoice
        invoice.signal_workflow('invoice_open')
        self.assertEqual(invoice.state, 'open', 'State in open')
        self.assertNotEqual(invoice.wh_iva_id, self.doc_obj,
                            'Not should be empty the withholding document')
        # Check document withholding iva
        iva_wh = invoice.wh_iva_id
        self.assertEqual(iva_wh.state, 'draft',
                         'State of withholding should be in draft')
        # Test create document txt line
        txt_iva.action_generate_lines_txt()
        for txt_line_brw in txt_iva.txt_ids:
            self.assertEqual(txt_line_brw.voucher_id.state, 'done',
                             'Error, only can add withholding documents in '
                             'done state.')
        # Set state confirm in document withholding
        iva_wh.signal_workflow('wh_iva_confirmed')
        self.assertEqual(iva_wh.state, 'confirmed',
                         'State of withholding should be in confirmed')
        # Test create document txt line
        txt_iva.action_generate_lines_txt()
        for txt_line_brw in txt_iva.txt_ids:
            self.assertEqual(txt_line_brw.voucher_id.state, 'done',
                             'Error, only can add withholding documents in '
                             'done state.')
        # Set state done in document withholding
        iva_wh.signal_workflow('wh_iva_done')
        self.assertEqual(iva_wh.state, 'done',
                         'State of withholding should be in done')
        # Create txt line with document withholding in state done
        txt_iva.action_generate_lines_txt()
        # Create second invoice supplier for test txt lines
        invoice_b = self._create_invoice('in_invoice')
        self._create_invoice_line(invoice_b.id, self.tax_general)
        # Set state open in invoice
        invoice_b.signal_workflow('invoice_open')
        self.assertNotEqual(invoice_b.wh_iva_id, self.doc_obj,
                            'Not should be empty the withholding document')
        # Set state confirm and done in document withholding
        # of the second invoice
        iva_wh_b = invoice_b.wh_iva_id
        iva_wh_b.signal_workflow('wh_iva_confirmed')
        iva_wh_b.signal_workflow('wh_iva_done')
        # Create txt lines with document withholding in state done
        txt_iva.action_generate_lines_txt()
        for txt_line_brw in txt_iva.txt_ids:
            self.assertEqual(txt_line_brw.voucher_id.state, 'done',
                             'Error, only can add withholding documents in '
                             'done state.')
        # Check quantity line in txt
        self.assertEqual(len(txt_iva.txt_ids), 2,
                         'Txt not should be lines')
        self.assertEqual(txt_iva.state, 'draft', 'State should be draft')
        # Set state confirm in document txt
        txt_iva.action_confirm()
        self.assertEqual(txt_iva.state, 'confirmed',
                         'State should be confirmed')
        # Updated journal to allow cancel withholding
        iva_wh.journal_id.write({'update_posted': True})
        invoice.journal_id.write({'update_posted': True})
        # Test cancel withholding
        with self.assertRaisesRegexp(
            except_orm,
            r"\bInvalid Procedure\b"
        ):
            iva_wh.cancel_check()
        txt_iva.action_done()
        self.assertEqual(txt_iva.state, 'done',
                         'State of txt iva should be done')
        with self.assertRaisesRegexp(
            except_orm,
            r"\bInvalid Procedure\b"
        ):
            iva_wh.cancel_check()
        self.assertEqual(iva_wh.state, 'done',
                         'State of withholding should be in done')
        txt_iva.action_anular()
        self.assertEqual(txt_iva.state, 'draft',
                         'State should be in draft')
        iva_wh.cancel_check()
        iva_wh.action_cancel()
        self.assertEqual(iva_wh.state, 'cancel',
                         'State of withholding should be in cancel')

    def test_07_withholding_iva_invoice_customer(self):
        """Test process the withholding iva for invoice customer"""
        # Create invoice customer
        invoice = self._create_invoice('out_invoice')
        self.assertEqual(
            invoice.state, 'draft', 'Initial state should be in "draft"'
        )
        # Create invoice line
        self._create_invoice_line(invoice.id, self.tax_s_12)
        # Set state open in invoice
        invoice.signal_workflow('invoice_open')
        # Check that no document has been created
        self.assertEqual(invoice.state, 'open', 'State in open')
        self.assertEqual(invoice.wh_iva_id, self.doc_obj,
                         'Should be empty the withholding document')

    def test_08_withholding_iva_wh_customer(self):
        """Test process the withholding iva for wh customer"""
        # Create document withholding iva customer
        wh_dict = {
            'name': 'AWI SALE XX',
            'partner_id': self.partner_amd.id,
            'account_id': self.partner_amd.property_account_receivable.id,
            'number': 'AWI SALE XX',
            'type': 'out_invoice'
        }
        iva_wh = self.doc_obj.create(wh_dict)
        self.assertEqual(iva_wh.state, 'draft',
                         'State of withholding should be in draft')
        # Test edit partner to partner not agent withholding
        with self.assertRaisesRegexp(
            ValidationError,
            "('ValidateError', 'The partner must be withholding vat agent .')"
        ):
            iva_wh.write({'partner_id': self.partner_nwh.id})
        iva_wh.write({'partner_id': self.partner_amd.id})
        # Create invoice customer
        invoice = self._create_invoice('out_invoice')
        self.assertEqual(
            invoice.state, 'draft', 'Initial state should be in "draft"'
        )
        # Create invoice line
        self._create_invoice_line(invoice.id, self.tax_s_12)
        # Set state open in invoice
        invoice.signal_workflow('invoice_open')
        self.assertEqual(invoice.state, 'open', 'State in open')
        self.assertEqual(invoice.wh_iva_id, self.doc_obj,
                         'Should be empty the withholding document')
        # Test on change for account partner
        res = iva_wh.onchange_partner_id('out_invoice', self.partner_amd.id)
        # Create withholding line
        values = {}
        values['wh_lines'] = [
            (0, 0, {'invoice_id': invoice.id,
                    'name': 'N/A',
                    'wh_iva_rate': iva_wh.partner_id.wh_iva_rate})]
        values['account_id'] = res['value']['account_id']
        iva_wh.write(values)
        self.assertEqual(len(iva_wh.wh_lines), 1,
                         'Should exist at least one record')
        msj_error = "'Error!', 'Must indicate: Accounting date and"
        " (or) Voucher Date'"
        # Trying to confirm document missing information
        with self.assertRaisesRegexp(
            except_orm,
            msj_error
        ):
            iva_wh.confirm_check()

        date_now = time.strftime(DEFAULT_SERVER_DATE_FORMAT)
        period = self.period_obj.find(date_now)
        iva_wh.write({'date_ret': date_now, 'date': date_now,
                      'period_id': period.id})
        with self.assertRaisesRegexp(
            except_orm,
            r"'Invoices with Missing Withheld Taxes!'"
        ):
            iva_wh.confirm_check()

        for line in iva_wh.wh_lines:
            line.load_taxes()
        # iva_wh.confirm_check()
        # Set state confirm in document withholding
        iva_wh.signal_workflow('wh_iva_confirmed')
        self.assertEqual(iva_wh.state, 'confirmed',
                         'State of withholding should be in confirmed')
        # Set state done in document withholding
        iva_wh.signal_workflow('wh_iva_done')
        self.assertEqual(iva_wh.state, 'done',
                         'State of withholding should be in done')
        # Check payment in invoice related with withholding iva
        self.assertEqual(len(invoice.payment_ids), 1, 'Should exits a payment')
        self.assertEqual(invoice.residual,
                         invoice.amount_total - iva_wh.total_tax_ret,
                         'Amount residual invoice should be equal amount '
                         'total - amount wh')
        debit = 0
        credit = 0
        for doc_inv in iva_wh.wh_lines:
            for line in doc_inv.move_id.line_id:
                if line.credit > 0:
                    credit += line.credit
                    self.assertEqual(line.account_id.id, invoice.account_id.id,
                                     'Account should be equal to account '
                                     'invoice')
                else:
                    debit += line.debit
                    account = self.tax_s_12.wh_vat_collected_account_id
                    self.assertEqual(line.account_id.id,
                                     account.id,
                                     'Account should be equal to account '
                                     'tax for withholding')
        self.assertEqual(debit, credit, 'Debit and Credit should be equal')
        self.assertEqual(debit, iva_wh.total_tax_ret,
                         'Amount total withholding should be equal '
                         'journal entries')
