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
from datetime import datetime, timedelta
from openerp.tests.common import TransactionCase
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.exceptions import except_orm, ValidationError


class TestIslrWithholding(TransactionCase):
    """ Test of withholding ISLR """

    def setUp(self):
        """Seudo-constructor method"""
        super(TestIslrWithholding, self).setUp()
        self.doc_obj = self.env['islr.wh.doc']
        self.doc_line_obj = self.env['islr.wh.doc.line']
        self.invoice_obj = self.env['account.invoice']
        self.invoice_line_obj = self.env['account.invoice.line']
        self.rates_obj = self.env['res.currency.rate']
        self.partner_amd = self.env.ref(
            'l10n_ve_fiscal_requirements.f_req_partner_2')
        self.partner_child = self.env.ref(
            'l10n_ve_fiscal_requirements.f_req_partner_9')
        self.product_ipad = self.env.ref(
            'product.product_product_6_product_template')
        self.concept = self.env.ref(
            'l10n_ve_withholding_islr.islr_wh_concept_pago_contratistas_demo')
        self.concept_no_apply = self.env.ref(
            'l10n_ve_withholding_islr.islr_wh_concept_no_apply_withholding')
        self.concept_wo_account = self.env.ref(
            'l10n_ve_withholding_islr.islr_wh_concept_pago_contratistas')
        self.concept_hprof = self.env.ref(
            'l10n_ve_withholding_islr.islr_wh_concept_hprof_no_mercantiles')
        # self.tax_general = self.env.ref(
        #     'l10n_ve_fiscal_requirements.iva_purchase1')
        self.currency_usd = self.env.ref('base.USD')
        self.company = self.env.ref('base.main_company')
        self.partner = self.env.ref('base.main_partner')

    def _create_invoice(self, type_inv='in_invoice', currency=False):
        """Function create invoice"""
        date_now = time.strftime(DEFAULT_SERVER_DATE_FORMAT)
        invoice_dict = {
            'partner_id': self.partner_amd.id,
            'nro_ctrl': '2000-694351',
            'date_invoice': date_now,
            'date_document': date_now,
            'type': type_inv,
            'reference_type': 'none',
            'name': 'invoice islr',
            'account_id': self.partner_amd.property_account_payable.id,
        }
        if type_inv == 'out_invoice':
            account = self.partner_amd.property_account_receivable.id
            invoice_dict['account_id'] = account
        if currency:
            invoice_dict['currency_id'] = currency
        return self.invoice_obj.create(invoice_dict)

    def _create_invoice_line(self, invoice_id=None, concept=None):
        """Create invoice line"""
        line_dict = {
            'product_id': self.product_ipad.id,
            'quantity': 1,
            'price_unit': 100,
            'name': self.product_ipad.name,
            'concept_id': concept,
            'invoice_id': invoice_id,
            # 'invoice_line_tax_id': [(6, 0, [self.tax_general.id])],
        }
        return self.invoice_line_obj.create(line_dict)

    def test_01_validate_process_withholding_islr(self):
        """Test create invoice supplier with data initial and
        Test validate invoice with document withholding islr"""
        # Update account in concept_hprof_no_mercantiles
        s_account = self.concept.property_retencion_islr_payable
        c_account = self.concept.property_retencion_islr_receivable
        self.concept_hprof.property_retencion_islr_payable = s_account
        self.concept_hprof.property_retencion_islr_receivable = c_account
        # Create invoice supplier
        invoice = self._create_invoice('in_invoice')
        # Check initial state
        self.assertEqual(
            invoice.state, 'draft', 'Initial state should be in "draft"'
        )
        # Create invoice lines
        self._create_invoice_line(invoice.id, self.concept.id)
        self._create_invoice_line(invoice.id, self.concept_hprof.id)
        # self._create_invoice_line(invoice.id, self.concept_no_apply.id)
        # Set state open in invoice
        invoice.signal_workflow('invoice_open')
        self.assertEqual(
            invoice.state, 'open', 'State in open'
        )
        # Check document withholding income created
        self.assertNotEqual(invoice.islr_wh_doc_id, self.doc_obj,
                            'Not should be empty the withholding document')
        # Test invoice copy
        invoice_c = invoice.copy()
        self.assertEqual(invoice_c.status, 'no_pro', 'Status should be no_pro')
        self.assertEqual(
            invoice_c.islr_wh_doc_id,
            self.doc_obj,
            'Withholding document the invoice copy should be empty')

        # Check document withholding income
        islr_wh = invoice.islr_wh_doc_id
        self.assertEqual(islr_wh.state, 'draft',
                         'State of withholding should be in draft')
        self.assertEqual(len(islr_wh.concept_ids), 2,
                         'Should exist two record')
        self.assertEqual(len(islr_wh.invoice_ids), 1, 'Should exist a invoice')
        self.assertEqual(islr_wh.amount_total_ret, 7.00,
                         'Amount total should be 7.00')
        # Check xml_id
        self.assertEqual(len(islr_wh.invoice_ids), 1,
                         'Invoice not incorporated')
        self.assertEqual(len(islr_wh.invoice_ids.islr_xml_id), 2,
                         'xml not created')
        # Confirm document withholding income
        islr_wh.signal_workflow('act_confirm')
        self.assertEqual(islr_wh.state, 'confirmed',
                         'State of withholding should be in confirmed')
        # Done document withholding income
        islr_wh.signal_workflow('act_done')
        self.assertEqual(islr_wh.state, 'done',
                         'State of withholding should be in done')
        # Check payments invoice
        self.assertEqual(len(invoice.payment_ids), 1, 'Should exits a payment')
        self.assertEqual(
            invoice.residual,
            invoice.amount_total - islr_wh.amount_total_ret,
            'Amount residual invoice should be equal amount total - amount wh'
        )
        debit = 0
        credit = 0
        for doc_inv in islr_wh.invoice_ids:
            for line in doc_inv.move_id.line_id:
                if line.debit > 0:
                    debit += line.debit
                    self.assertEqual(
                        line.account_id.id,
                        invoice.account_id.id,
                        'Account should be equal to account invoice'
                    )
                else:
                    credit += line.credit
                    self.assertEqual(
                        line.account_id.id,
                        self.concept.property_retencion_islr_payable.id,
                        'Account should be equal to account concept islr'
                    )
        self.assertEqual(debit, credit, 'Debit and Credit should be equal')
        self.assertEqual(
            debit, islr_wh.amount_total_ret,
            'Amount total withholding should be equal journal entries'
        )

    # def test_02_constraint_account_withholding_islr(self):
    #     '''Test constraint account concept withholding islr'''
    #     invoice = self._create_invoice('in_invoice')
    #     # Check initial state
    #     self._create_invoice_line(invoice.id, self.concept_wo_account.id)
    #     invoice.signal_workflow('invoice_open')
    #     islr_wh = invoice.islr_wh_doc_id
    #     islr_wh.signal_workflow('act_confirm')
    #     with self.assertRaisesRegexp(
    #         except_orm,
    #         "Missing Account in Tax!"
    #     ):
    #         islr_wh.signal_workflow('act_done')

    def test_02_withholding_with_currency(self):
        """Test withholding with multi currency"""
        # Create Rate for currency USD
        datetime_now = datetime.now()
        day = timedelta(days=2)
        datetime_now = datetime_now - day
        datetime_now = datetime_now.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        self.rates_obj.create({'name': datetime_now,
                               'rate': 1.25,
                               'currency_id': self.currency_usd.id})
        # Create invoice
        invoice = self._create_invoice('in_invoice', self.currency_usd.id)
        # Create invoice line
        self._create_invoice_line(invoice.id, self.concept.id)
        # Set state open in invoice
        invoice.signal_workflow('invoice_open')
        islr_wh = invoice.islr_wh_doc_id
        # Check currency in document withholding income
        for concept_id in islr_wh.concept_ids:
            currency_c = concept_id.currency_base_amount /\
                invoice.currency_id.rate_silent
            wh_currency = concept_id.currency_amount /\
                invoice.currency_id.rate_silent
            self.assertEqual(concept_id.base_amount,
                             currency_c,
                             """Amount base should be equal to amount invoice
                             between currency amount""")
            self.assertEqual(concept_id.amount,
                             wh_currency,
                             """Amount base should be equal to amount invoice
                             between currency amount""")

    def test_03_validate_process_withholding_islr_customer(self):
        """Test create invoice customer with data initial and
        Test validate invoice with document withholding islr"""
        # Create invoice customer
        invoice = self._create_invoice('out_invoice')
        # Check initial state
        self.assertEqual(
            invoice.state, 'draft', 'Initial state should be in "draft"'
        )
        # Create invoice lines
        self._create_invoice_line(invoice.id, self.concept.id)
        # Set state open in invoice
        invoice.signal_workflow('invoice_open')
        self.assertEqual(invoice.state, 'open', 'State in open')
        # Check document withholding income no created
        self.assertEqual(invoice.islr_wh_doc_id, self.doc_obj,
                         'Not should be empty the withholding document')
        # Create withholding document manually
        account_p = self.doc_obj.onchange_partner_id('out_invoice',
                                                     self.partner_amd.id)
        islr_wh = self.doc_obj.create({
            'name': 'ISLR MANUAL CUSTOMER',
            'partner_id': self.partner_amd.id,
            'account_id': account_p['value']['account_id'],
            'type': 'out_invoice',
        })
        # Delete invoice auto-loaded
        islr_wh.invoice_ids.unlink()
        self.assertEqual(len(islr_wh.invoice_ids), 0,
                         'There should be lines')
        # Add invoice to document retention
        islr_wh.write({
            'invoice_ids': [(0, 0, {'invoice_id': invoice.id})]
        })
        self.assertEqual(len(islr_wh.invoice_ids), 1,
                         'There should be lines')
        # Try confirm document withholding income
        # Raise error with taxes
        with self.assertRaises(except_orm):
            islr_wh.signal_workflow('act_confirm')
        # Try compute taxes
        # Raise error with withhold date
        with self.assertRaises(except_orm):
            islr_wh.compute_amount_wh()
        # Add date witholding
        date_now = time.strftime(DEFAULT_SERVER_DATE_FORMAT)
        islr_wh.date_uid = date_now
        # Compute the taxes manually
        islr_wh.compute_amount_wh()
        # Confirm document withholding income
        islr_wh.signal_workflow('act_confirm')
        self.assertEqual(islr_wh.state, 'confirmed',
                         'State of withholding should be in confirmed')
        # Done document withholding income
        islr_wh.signal_workflow('act_done')
        self.assertEqual(islr_wh.state, 'done',
                         'State of withholding should be in done')
        # Check payments invoice
        self.assertEqual(len(invoice.payment_ids), 1, 'Should exits a payment')
        self.assertEqual(
            invoice.residual,
            invoice.amount_total - islr_wh.amount_total_ret,
            'Amount residual invoice should be equal amount total - amount wh'
        )

    def test_04_islr_partner_child(self):
        """Test withholding islr with partner child"""
        # Create invoice supplier
        date_now = time.strftime(DEFAULT_SERVER_DATE_FORMAT)
        invoice_dict = {
            'partner_id': self.partner_child.id,
            'nro_ctrl': '2000-694351',
            'date_invoice': date_now,
            'date_document': date_now,
            'type': 'in_invoice',
            'reference_type': 'none',
            'name': 'invoice islr supplier',
            'account_id': self.partner_child.property_account_payable.id,
        }
        invoice = self.invoice_obj.create(invoice_dict)
        # Check initial state
        self.assertEqual(
            invoice.state, 'draft', 'Initial state should be in "draft"')
        # Create invoice lines
        self._create_invoice_line(invoice.id, self.concept.id)
        self._create_invoice_line(invoice.id, self.concept_no_apply.id)
        # Set state open in invoice
        invoice.signal_workflow('invoice_open')
        self.assertEqual(
            invoice.state, 'open', 'State in open'
        )
        # Check document withholding income
        self.assertNotEqual(invoice.islr_wh_doc_id, self.doc_obj,
                            'Not should be empty the withholding document')
        islr_wh = invoice.islr_wh_doc_id

        # Check partner assigned in document withholding islr
        self.assertEqual(invoice.partner_id.parent_id, islr_wh.partner_id,
                         'Partner islr should be equal to partner invoice')

    def test_05_company_automatic_done_wh(self):
        """Test withholding document is automatic set to Done"""
        # Update withholding automatic
        self.company.automatic_income_wh = True
        self.assertTrue(self.company.automatic_income_wh,
                        'Automatic_income_wh is False')
        # Create invoice supplier
        invoice = self._create_invoice('in_invoice')
        # Check initial state
        self.assertEqual(
            invoice.state, 'draft', 'Initial state should be in "draft"'
        )
        # Create invoice lines
        self._create_invoice_line(invoice.id, self.concept.id)
        self._create_invoice_line(invoice.id, self.concept_no_apply.id)
        # Set state open in invoice
        invoice.signal_workflow('invoice_open')
        self.assertEqual(invoice.state, 'open', 'State in open')
        # Check document withholding income created
        self.assertNotEqual(invoice.islr_wh_doc_id, self.doc_obj,
                            'Not should be empty the withholding document')
        # Check state done in document withholding income
        islr_wh = invoice.islr_wh_doc_id
        self.assertEqual(islr_wh.state, 'done', 'State should be done')
        # Check payments invoice
        self.assertEqual(len(invoice.payment_ids), 1, 'Should exits a payment')
        self.assertEqual(
            invoice.residual,
            invoice.amount_total - islr_wh.amount_total_ret,
            'Amount residual invoice should be equal amount total - amount wh'
        )
        debit = 0
        credit = 0
        for doc_inv in islr_wh.invoice_ids:
            for line in doc_inv.move_id.line_id:
                if line.debit > 0:
                    debit += line.debit
                    self.assertEqual(
                        line.account_id.id,
                        invoice.account_id.id,
                        'Account should be equal to account invoice'
                    )
                else:
                    credit += line.credit
                    self.assertEqual(
                        line.account_id.id,
                        self.concept.property_retencion_islr_payable.id,
                        'Account should be equal to account concept islr'
                    )
        self.assertEqual(debit, credit, 'Debit and Credit should be equal')
        self.assertEqual(
            debit, islr_wh.amount_total_ret,
            'Amount total withholding should be equal journal entries')

    def test_06_withholding_society_of_natural_persons(self):
        """Test create withholding income with partner is society
        of natural persons (spn)"""
        # Update partner for assign spn
        self.partner_amd.spn = True
        self.assertTrue(self.partner_amd.spn, 'SPN not is True')
        # # Update account in concept_hprof_no_mercantiles
        # s_account = self.concept.property_retencion_islr_payable
        # c_account = self.concept.property_retencion_islr_receivable
        # self.concept_hprof.property_retencion_islr_payable = s_account
        # self.concept_hprof.property_retencion_islr_receivable = c_account
        # Create invoice supplier
        invoice = self._create_invoice('in_invoice')
        # Check initial state
        self.assertEqual(
            invoice.state, 'draft', 'Initial state should be in "draft"'
        )
        # Create invoice lines
        # self._create_invoice_line(invoice.id, self.concept.id)
        self._create_invoice_line(invoice.id, self.concept_hprof.id)
        # Set state open in invoice
        invoice.signal_workflow('invoice_open')
        self.assertEqual(invoice.state, 'open', 'State in open')
        # Check document withholding income created
        self.assertNotEqual(invoice.islr_wh_doc_id, self.doc_obj,
                            'Not should be empty the withholding document')
        # Obtain correct rate to compare
        correct_rate = False
        for rate in self.concept_hprof.rate_ids:
            if rate.residence and rate.nature:
                correct_rate = rate
        # Check rate
        islr_wh = invoice.islr_wh_doc_id
        self.assertEqual(islr_wh.concept_ids.islr_rates_id, correct_rate,
                         'Rate of concept is incorrect')

    def test_07_partner_exempt_islr(self):
        """Test withholding income with partner exempt"""
        # Set false islr_exempt in partner
        self.partner_amd.islr_exempt = True
        self.assertTrue(self.partner_amd.islr_exempt, "No update islr_exempt")
        # Create invoice supplier
        invoice = self._create_invoice('in_invoice')
        # Check initial state
        self.assertEqual(
            invoice.state, 'draft', 'Initial state should be in "draft"'
        )
        # Create invoice lines
        self._create_invoice_line(invoice.id, self.concept.id)
        # Set state open in invoice
        invoice.signal_workflow('invoice_open')
        self.assertEqual(invoice.state, 'open', 'State in open')
        # Check document withholding income
        islr_wh = invoice.islr_wh_doc_id
        self.assertEqual(islr_wh.state, 'draft', 'State should be draft')
        self.assertEqual(islr_wh.amount_total_ret, 0.0, 'Amount should be 0')
        # Check that the invoice base amount is less than the minimum
        # withholding rate
        vendor, buyer, wh_agent = islr_wh.invoice_ids._get_partners(invoice)
        residence = islr_wh.invoice_ids._get_residence(vendor, buyer)
        nature = islr_wh.invoice_ids._get_nature(vendor)
        rate_min = islr_wh.invoice_ids._get_rate(self.concept.id,
                                                 residence, nature)[1]
        rate_bool = True
        if rate_min > invoice.amount_untaxed:
            rate_bool = False
        self.assertTrue(rate_bool, 'Its not correct')

    def test_08_company_no_income_withholding_agent(self):
        """Test company no income withholding agent"""
        self.partner.islr_withholding_agent = False
        self.assertFalse(self.partner.islr_withholding_agent,
                         'Field not updated')
        # Create invoice supplier
        invoice = self._create_invoice('in_invoice')
        # Check initial state
        self.assertEqual(
            invoice.state, 'draft', 'Initial state should be in "draft"'
        )
        # Create invoice lines
        self._create_invoice_line(invoice.id, self.concept.id)
        # Set state open in invoice
        invoice.signal_workflow('invoice_open')
        self.assertEqual(invoice.state, 'open', 'State in open')
        # Check document withholding income
        self.assertEqual(invoice.islr_wh_doc_id, self.doc_obj,
                         'Error document withholding created')
        # Test Try to create a supplier withholding document manually
        account_p = self.doc_obj.onchange_partner_id('in_invoice',
                                                     self.partner_amd.id)
        with self.assertRaises(ValidationError):
            self.doc_obj.create({
                'name': 'ISLR MANUAL PURCHASE',
                'partner_id': self.partner_amd.id,
                'account_id': account_p['value']['account_id'],
            })

    def test_09_withholding_document_manual(self):
        """Test create withholding document manual"""
        # Create withholding document
        account_p = self.doc_obj.onchange_partner_id('in_invoice',
                                                     self.partner_amd.id)
        islr_wh = self.doc_obj.create({
            'name': 'ISLR MANUAL PURCHASE',
            'partner_id': self.partner_amd.id,
            'account_id': account_p['value']['account_id'],
        })
        # Delete invoice auto-loaded
        islr_wh.invoice_ids.unlink()
        self.assertEqual(len(islr_wh.invoice_ids), 0, 'There should be lines')
        # Test try to confirm withholding document without invoices
        with self.assertRaises(except_orm):
            islr_wh.signal_workflow('act_confirm')
        # Check state it is still draft
        self.assertEqual(islr_wh.state, 'draft',
                         'State of withholding should be in draft')
        # Create invoice supplier
        invoice = self._create_invoice('in_invoice')
        # Check initial state
        self.assertEqual(
            invoice.state, 'draft', 'Initial state should be in "draft"'
        )
        # Create invoice lines
        self._create_invoice_line(invoice.id, self.concept.id)
        # Check invoices can not be added in draft state
        with self.assertRaises(ValidationError):
            islr_wh.write({
                'invoice_ids': [(0, 0, {'invoice_id': invoice.id})]
            })
        # Delete invoice loaded
        islr_wh.invoice_ids.unlink()
        self.assertEqual(len(islr_wh.invoice_ids), 0, 'There should be lines')
        # Set state open in invoice
        invoice.signal_workflow('invoice_open')
        # Test add withholding document
        self.assertEqual(invoice.state, 'open', 'State in open')
        islr_wh.write({
            'invoice_ids': [(0, 0, {'invoice_id': invoice.id})]
        })

    def test_10_withholding_document_duplicate(self):
        """Test create withholding document manual and
        I try to add invoice already approved"""
        # Create withholding document
        account_p = self.doc_obj.onchange_partner_id('in_invoice',
                                                     self.partner_amd.id)
        islr_wh_m = self.doc_obj.create({
            'name': 'ISLR MANUAL PURCHASE',
            'partner_id': self.partner_amd.id,
            'account_id': account_p['value']['account_id'],
        })
        # Delete invoice auto-loaded
        islr_wh_m.invoice_ids.unlink()
        self.assertEqual(len(islr_wh_m.invoice_ids), 0,
                         'There should be lines')
        # Create invoice supplier
        invoice = self._create_invoice('in_invoice')
        # Check initial state
        self.assertEqual(
            invoice.state, 'draft', 'Initial state should be in "draft"'
        )
        # Create invoice lines
        self._create_invoice_line(invoice.id, self.concept.id)
        # Set state open in invoice
        invoice.signal_workflow('invoice_open')
        # Confirm document withholding income
        islr_wh = invoice.islr_wh_doc_id
        islr_wh.signal_workflow('act_confirm')
        self.assertEqual(islr_wh.state, 'confirmed',
                         'State of withholding should be in confirmed')
        # Done document withholding income
        islr_wh.signal_workflow('act_done')
        self.assertEqual(islr_wh.state, 'done',
                         'State of withholding should be in done')
        # Test add invoice approved to withholding document
        self.assertEqual(invoice.state, 'open', 'State in open')
        islr_wh_m.write({
            'invoice_ids': [(0, 0, {'invoice_id': invoice.id})]
        })
