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
from openerp.exceptions import ValidationError
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT


class TestFiscalRequirements(TransactionCase):
    """ Test of Fiscal Requirements """

    def setUp(self):
        """Seudo-constructor method"""
        super(TestFiscalRequirements, self).setUp()
        self.partner_obj = self.env['res.partner']
        self.invoice_obj = self.env['account.invoice']
        self.invoice_line_obj = self.env['account.invoice.line']
        self.period_obj = self.env['account.period']
        self.move_obj = self.env['account.move']
        self.w_ncontrol = self.env['wiz.nroctrl']
        self.winv_numctrl = self.env['wizard.invoice.nro.ctrl']
        self.inv_debit = self.env['account.invoice.debit']
        self.inv_refund = self.env['account.invoice.refund']
        self.tax_unit = self.env['l10n.ut']
        self.rates_obj = self.env['res.currency.rate']
        self.seniat_srch = self.env['search.info.partner.seniat']
        self.partner_amd = self.env.ref(
            'l10n_ve_fiscal_requirements.f_req_partner_2')
        self.partner_nwh = self.env.ref(
            'l10n_ve_fiscal_requirements.f_req_partner_7')
        self.comercial = self.env.ref(
            'l10n_ve_fiscal_requirements.f_req_partner_10')
        self.parent_com = self.env.ref(
            'base.res_partner_23')
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
        self.a_sale = self.env.ref(
            'account.a_sale')
        self.main_partner = self.env.ref(
            'base.main_partner')
        self.company = self.env.ref(
            'base.main_company')
        self.currency_usd = self.env.ref('base.USD')
        self.currency_eur = self.env.ref('base.EUR')

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

    def test_01_create_customer_invoice(self):
        """Test create customer invoice"""
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

    def test_02_create_supplier_invoice(self):
        """Test create supplier invoice"""
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

    def test_03_comercial_partner(self):
        """Test comercial partner"""
        # Create invoice customer
        date_now = time.strftime(DEFAULT_SERVER_DATE_FORMAT)
        invoice_dict = {
            'partner_id': self.comercial.id,
            'nro_ctrl': '2000-694351',
            'date_invoice': date_now,
            'date_document': date_now,
            'type': 'out_invoice',
            'reference_type': 'none',
            'name': 'invoice customer',
            'account_id': self.partner_amd.property_account_receivable.id,
        }
        invoice = self.invoice_obj.create(invoice_dict)
        # Check initial state
        self.assertEqual(
            invoice.state, 'draft', 'Initial state should be in "draft"'
        )
        # Create invoice line with tax general
        self._create_invoice_line(invoice.id, self.tax_s_12)
        # Set invoice state proforma2
        invoice.signal_workflow('invoice_proforma2')
        self.assertEqual(invoice.state, 'proforma2', 'State in proforma2')
        # Check no created journal entries
        self.assertEqual(invoice.move_id, self.move_obj,
                         'There should be no move')
        # Set invoice state open
        invoice.signal_workflow('invoice_open')
        self.assertEqual(invoice.state, 'open', 'State in open')
        # Check created journal entries
        self.assertNotEqual(invoice.move_id, self.move_obj,
                            'There should be move')
        partner = invoice.move_id.partner_id
        self.assertEqual(partner.id, self.parent_com.id,
                         'Partner move should be equal to parent partner of '
                         'the comercial')

    def test_04_wizard_number_control(self):
        """Test wizard change number control in invoice"""
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
        # Check number control
        self.assertEqual(invoice.nro_ctrl, '2000-694351',
                         'Number control bad')
        # Test wizard number control
        context = {'active_id': invoice.id}
        value = {'name': '987654321',
                 'sure': True}
        self.w_ncontrol.with_context(context).create(value).set_noctrl()
        self.assertEqual(invoice.nro_ctrl, '987654321',
                         'Number control no chance')

    def test_05_damaged_paper(self):
        """Test fiscal requirements damaged paper"""
        # Create customer invoice
        invoice = self._create_invoice('out_invoice')
        # Check initial state
        self.assertEqual(
            invoice.state, 'draft', 'Initial state should be in "draft"'
        )
        # Create invoice line with tax general
        self._create_invoice_line(invoice.id, self.tax_s_12)
        # Set invoice state proforma2
        invoice.signal_workflow('invoice_proforma2')
        self.assertEqual(invoice.state, 'proforma2', 'State in proforma2')
        # Check no created journal entries
        self.assertEqual(invoice.move_id, self.move_obj,
                         'There should be no move')
        # Set invoice state open
        invoice.signal_workflow('invoice_open')
        self.assertEqual(invoice.state, 'open', 'State in open')
        # Check created journal entries
        self.assertNotEqual(invoice.move_id, self.move_obj,
                            'There should be move')
        # Update company account for damaged paper
        self.company.write({'acc_id': self.a_sale.id})
        self.assertEqual(self.company.acc_id, self.a_sale,
                         'Account not update')
        # Update journal to allow cancellation
        invoice.journal_id.write({'update_posted': True})
        self.assertTrue(invoice.journal_id.update_posted,
                        'Update_posted should be True')
        # Create a damaged paper
        winc = self.winv_numctrl.create({
            'invoice_id': invoice.id,
            'sure': True
        })
        winc.action_invoice_create(None, invoice)
        self.assertEqual(invoice.move_id.state, 'draft',
                         'Move of invoice should be draft')
        self.assertEqual(invoice.state, 'paid',
                         'State invoice should be paid')

    def test_06_debit_note(self):
        """Test fiscal requirement debit note"""
        # Create customer invoice
        invoice = self._create_invoice('out_invoice')
        # Check initial state
        self.assertEqual(
            invoice.state, 'draft', 'Initial state should be in "draft"'
        )
        # Create invoice line with tax general
        self._create_invoice_line(invoice.id, self.tax_s_12)
        # Set invoice state proforma2
        invoice.signal_workflow('invoice_proforma2')
        self.assertEqual(invoice.state, 'proforma2', 'State in proforma2')
        # Check no created journal entries
        self.assertEqual(invoice.move_id, self.move_obj,
                         'There should be no move')
        # Set invoice state open
        invoice.signal_workflow('invoice_open')
        self.assertEqual(invoice.state, 'open', 'State in open')
        # Check created journal entries
        self.assertNotEqual(invoice.move_id, self.move_obj,
                            'There should be move')
        # Create wizard account invoice debit
        date_now = time.strftime(DEFAULT_SERVER_DATE_FORMAT)
        w_debit = self.inv_debit.create({
            'description': 'Test debit note',
            'date': date_now,
            'journal_id': invoice.journal_id.id,
            'comment': 'Debit note for unit test'
        })
        # Create debit note
        context = {'active_id': invoice.id, 'active_ids': [invoice.id]}
        w_debit.with_context(context).invoice_debit()
        # Check debit note created
        search_inv = self.invoice_obj.search([('parent_id', '=', invoice.id),
                                              ('type', '=', 'out_invoice')])
        self.assertEqual(len(search_inv), 1, 'Should be 1 record')

    def test_07_01_refunds_notes_modify(self):
        """Test fiscal requirement refunds notes method modify"""
        # Create customer invoice
        invoice = self._create_invoice('out_invoice')
        # Check initial state
        self.assertEqual(
            invoice.state, 'draft', 'Initial state should be in "draft"'
        )
        # Create invoice line with tax general
        self._create_invoice_line(invoice.id, self.tax_s_12)
        # Set invoice state proforma2
        invoice.signal_workflow('invoice_proforma2')
        self.assertEqual(invoice.state, 'proforma2', 'State in proforma2')
        # Check no created journal entries
        self.assertEqual(invoice.move_id, self.move_obj,
                         'There should be no move')
        # Set invoice state open
        invoice.signal_workflow('invoice_open')
        self.assertEqual(invoice.state, 'open', 'State in open')
        # Test refund invoice (modify)
        date_now = time.strftime(DEFAULT_SERVER_DATE_FORMAT)
        period_id = self.period_obj.find(date_now)
        context = {'active_id': invoice.id, 'active_ids': [invoice.id]}
        refund = self.inv_refund.with_context(context).create({
            'description': 'Test Refund',
            'date': date_now,
            'filter_refund': 'modify',
            'period': period_id.id,
            'nro_ctrl': '12-123456',
        })
        # Click Refund button from wizard
        refund.with_context(context).invoice_refund()
        # Check invoice state is now 'paid'
        self.assertEqual(invoice.state, 'paid',
                         'State invoice should be paid')
        # Customer refund was properly created
        inv_id = self.invoice_obj.search([('parent_id', '=', invoice.id),
                                          ('type', '=', 'out_refund')])
        self.assertEqual(inv_id.state, 'paid',
                         'Debit note was not created properly')
        # Check if invoice was properly created in draft state
        inv_id = self.invoice_obj.search([('name', '=', 'Test Refund'),
                                          ('state', '=', 'draft'),
                                          ('type', '=', 'out_invoice')])
        create_inv = True if inv_id else False
        self.assertTrue(create_inv, 'Debit note was no created')
        # Check if lines invoice and taxes were created in the new invoice
        self.assertEqual(len(invoice.invoice_line), len(inv_id.invoice_line),
                         'Line invoice no created')
        self.assertEqual(inv_id.invoice_line.invoice_line_tax_id,
                         self.tax_s_12, 'Both invoice has not the same taxes')

    def test_07_02_refunds_notes_refund(self):
        """Test fiscal requirement refunds notes method refund"""
        # Create customer invoice
        invoice = self._create_invoice('out_invoice')
        # Check initial state
        self.assertEqual(
            invoice.state, 'draft', 'Initial state should be in "draft"'
        )
        # Create invoice line with tax general
        self._create_invoice_line(invoice.id, self.tax_s_12)
        # Set invoice state proforma2
        invoice.signal_workflow('invoice_proforma2')
        self.assertEqual(invoice.state, 'proforma2', 'State in proforma2')
        # Check no created journal entries
        self.assertEqual(invoice.move_id, self.move_obj,
                         'There should be no move')
        # Set invoice state open
        invoice.signal_workflow('invoice_open')
        self.assertEqual(invoice.state, 'open', 'State in open')
        # Test refund invoice (refund)
        date_now = time.strftime(DEFAULT_SERVER_DATE_FORMAT)
        period_id = self.period_obj.find(date_now)
        context = {'active_id': invoice.id, 'active_ids': [invoice.id]}
        refund = self.inv_refund.with_context(context).create({
            'description': 'Test Refund',
            'date': date_now,
            'filter_refund': 'refund',
            'period': period_id.id,
            'nro_ctrl': '12-123456',
        })
        # Click Refund button from wizard
        refund.with_context(context).invoice_refund()
        # Check invoice state is open state
        self.assertEqual(invoice.state, 'open',
                         'State invoice should be open')
        # Customer refund was properly created
        inv_id = self.invoice_obj.search([('parent_id', '=', invoice.id),
                                          ('state', '=', 'draft'),
                                          ('type', '=', 'out_refund')])
        create_inv = True if inv_id else False
        self.assertTrue(create_inv, 'Debit note was no created')
        # Check if lines invoice and taxes were created in the new invoice
        self.assertEqual(len(invoice.invoice_line), len(inv_id.invoice_line),
                         'Line invoice no created')
        self.assertEqual(inv_id.invoice_line.invoice_line_tax_id,
                         self.tax_s_12, 'Both invoice has not the same taxes')

    def test_07_03_refunds_notes_cancel(self):
        """Test fiscal requirement refunds notes method cancel"""
        # Create customer invoice
        invoice = self._create_invoice('out_invoice')
        # Check initial state
        self.assertEqual(
            invoice.state, 'draft', 'Initial state should be in "draft"'
        )
        # Create invoice line with tax general
        self._create_invoice_line(invoice.id, self.tax_s_12)
        # Set invoice state proforma2
        invoice.signal_workflow('invoice_proforma2')
        self.assertEqual(invoice.state, 'proforma2', 'State in proforma2')
        # Check no created journal entries
        self.assertEqual(invoice.move_id, self.move_obj,
                         'There should be no move')
        # Set invoice state open
        invoice.signal_workflow('invoice_open')
        self.assertEqual(invoice.state, 'open', 'State in open')
        # Test refund invoice (cancel)
        date_now = time.strftime(DEFAULT_SERVER_DATE_FORMAT)
        period_id = self.period_obj.find(date_now)
        context = {'active_id': invoice.id, 'active_ids': [invoice.id]}
        refund = self.inv_refund.with_context(context).create({
            'description': 'Test Refund',
            'date': date_now,
            'filter_refund': 'cancel',
            'period': period_id.id,
            'nro_ctrl': '12-123456',
        })
        # Click Refund button from wizard
        refund.with_context(context).invoice_refund()
        # Check invoice state is now 'paid'
        self.assertEqual(invoice.state, 'paid',
                         'State invoice should be paid')
        # Customer refund was properly created
        inv_id = self.invoice_obj.search([('parent_id', '=', invoice.id),
                                          ('state', '=', 'paid'),
                                          ('type', '=', 'out_refund')])
        create_inv = True if inv_id else False
        self.assertTrue(create_inv, 'Debit note was no created')
        # Check if lines invoice and taxes were created in the new invoice
        self.assertEqual(len(invoice.invoice_line), len(inv_id.invoice_line),
                         'Line invoice no created')
        self.assertEqual(inv_id.invoice_line.invoice_line_tax_id,
                         self.tax_s_12, 'Both invoice has not the same taxes')

    def test_08_tax_unit(self):
        """Test Tax unit"""
        # Create tax unit
        date_now = time.strftime(DEFAULT_SERVER_DATE_FORMAT)
        self.tax_unit.create({
            'name': '456123',
            'date': date_now,
            'amount': 200.00,
        })
        # Check search by date tax unit
        ut_amount = self.tax_unit.get_amount_ut(date_now)
        self.assertEqual(ut_amount, 200, 'Amount of tax unit should be 200')
        # Check qunatity tax units
        ut_qty = self.tax_unit.compute(400)
        self.assertEqual(ut_qty, 2, 'Quantity tax unit should be 2')
        # Check amount of tax unit
        amount = self.tax_unit.compute_ut_to_money(5)
        self.assertEqual(amount, 1000, 'Amount should be 1000')
        # Check exchange currency in tax unit
        self.company.write({'currency_id': self.currency_eur.id})
        self.assertEqual(self.company.currency_id,
                         self.currency_eur,
                         'Currency company should be EUR')
        datetime_now = datetime.now()
        day = timedelta(days=2)
        datetime_now = datetime_now - day
        datetime_now = datetime_now.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        self.rates_obj.create({'name': datetime_now,
                               'rate': 1.25,
                               'currency_id': self.currency_usd.id})
        _xc = self.tax_unit.sxc(self.company.currency_id.id,
                                self.currency_usd.id,
                                date_now)
        self.assertEqual(_xc(2000), 2500, 'Change currency incorrect')

    def test_09_seniat_search(self):
        """Test seniat search wizard"""
        seniat = self.seniat_srch.create({
            'vat': 'J317520882'
        })
        # Button search RIF
        seniat.search_partner_seniat()
        # Check search RIF
        self.assertEqual(seniat.name, 'VAUXOO, C,A',
                         'This search should return "VAUXOO, C,A"')

    def test_10_vat(self):
        """Test vat in create and validation of partner"""
        # Test Create partner with a wrong formatted var
        # for Venezuelan Standards
        with self.assertRaises(ValidationError):
            self.partner_obj.create({
                'name': 'Partner test fiscal requirements',
                'supplier': True,
                'customer': True,
                'vat': 'VEJ333',
                'type': 'invoice',
                'street': 'Av Siempre Viva',
                'phone': '(555) 5555555',
                'fax': '(555) 9999999',
                'email': 'fakemail@example.com',
            })
        # Test Create partner with a right formatted var
        # for Venezuelan Standards
        partner = self.partner_obj.create({
            'name': 'Partner test fiscal requirements',
            'supplier': True,
            'customer': True,
            'vat': 'VEJ333444116',
            'type': 'invoice',
            'street': 'Av Siempre Viva',
            'phone': '(555) 5555555',
            'fax': '(555) 9999999',
            'email': 'fakemail@example.com',
        })
        self.assertNotEqual(partner, self.partner_obj,
                            'Partner should be created')
        # Test Create partner with no VAT number
        with self.assertRaises(ValidationError):
            self.partner_obj.create({
                'name': 'Partner test fiscal requirements',
                'supplier': True,
                'customer': True,
                'type': 'invoice',
                'street': 'Av Siempre Viva',
                'phone': '(555) 5555555',
                'fax': '(555) 9999999',
                'email': 'fakemail@example.com',
                'country_id': self.env.ref('base.ve').id
            })
        # Set vat_check_vies equal False in main company, will not consult web
        self.company.vat_check_vies = False
        # Test Button 'Check Validity' in Partner Form
        self.partner_amd.button_check_vat()
        self.assertEqual(self.partner_amd.name,
                         'Accesorios AMD Computadoras, C.A.',
                         'Name incorrect')
        self.assertFalse(self.partner_amd.seniat_updated,
                         'seniat_updated should be false')
        # Set vat_check_vies equal True in main company, will consult web
        self.company.vat_check_vies = True
        # Test Button 'Check Validity' in Partner Form
        self.partner_amd.button_check_vat()
        self.assertEqual(self.partner_amd.name,
                         'ACCESORIOS A.M.D. COMPUTADORAS, C.A.',
                         'Name no update')
        self.assertTrue(self.partner_amd.seniat_updated,
                        'seniat_updated should be true')
