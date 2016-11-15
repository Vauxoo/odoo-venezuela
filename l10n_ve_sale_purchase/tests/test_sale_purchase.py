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


class TestSalePurchase(TransactionCase):
    """ Test of l10_ve_sale_purchase """

    def setUp(self):
        """Seudo-constructor method"""
        super(TestSalePurchase, self).setUp()
        self.purchase_obj = self.env['purchase.order']
        self.pur_line_obj = self.env['purchase.order.line']
        self.sale_obj = self.env['sale.order']
        self.sal_line_obj = self.env['sale.order.line']
        self.picking_obj = self.env['stock.picking']
        self.invoice_obj = self.env['account.invoice']
        self.transfer_obj = self.env['stock.transfer_details']
        self.partner_amd = self.env.ref(
            'l10n_ve_fiscal_requirements.f_req_partner_2')
        self.product_ipad = self.env.ref(
            'product.product_product_6_product_template')
        self.product_pc = self.env.ref(
            'product.product_product_3_product_template')
        self.location = self.env.ref('stock.stock_location_stock')
        self.pricelist = self.env.ref('product.list0')
        self.no_concept = self.env.ref(
            'l10n_ve_withholding_islr.islr_wh_concept_no_apply_withholding')

    def test_01_purchase_order_method_order(self):
        """Test Purchase Order, invoice method order"""
        # Create purchase order
        date_now = time.strftime(DEFAULT_SERVER_DATE_FORMAT)
        pur_ord = self.purchase_obj.create({
            'date_order': date_now,
            'location_id': self.location.id,
            'partner_id': self.partner_amd.id,
            'invoice_method': 'order',
            'pricelist_id': self.pricelist.id,
        })
        self.pur_line_obj.create({
            'product_id': self.product_pc.id,
            'product_qty': 3,
            'price_unit': 10,
            'name': 'PC3',
            'date_planned': date_now,
            'order_id': pur_ord.id,
            'concept_id': self.no_concept.id,
        })
        self.pur_line_obj.create({
            'product_id': self.product_ipad.id,
            'product_qty': 5,
            'price_unit': 5,
            'name': 'Ipad',
            'date_planned': date_now,
            'order_id': pur_ord.id,
            'concept_id': self.no_concept.id,
        })
        # Check state purchase order
        self.assertEqual(pur_ord.state, 'draft', 'State should be draft')
        # Set purchase order state approved
        pur_ord.signal_workflow('purchase_confirm')
        self.assertEqual(pur_ord.state, 'approved', 'State should be confirm')
        # Check stock picking created
        picking = self.picking_obj.search([('origin', '=', pur_ord.name)])
        self.assertEqual(len(picking), 1, 'Picking not created')
        self.assertEqual(picking.state, 'assigned',
                         'State picking should be equal to assigned')
        self.assertEqual(len(picking.move_lines), 2,
                         'Quantity lines incorrect')
        # Validate stock picking
        transfer = picking.do_enter_transfer_details()
        context = transfer.get('context', {})
        transf = self.transfer_obj.with_context(context).create({
            'picking_id': picking.id})
        transf.do_detailed_transfer()
        # Check stock picking and stock move
        self.assertEqual(picking.state, 'done', 'Picking should be validated')
        for sm_id in picking.move_lines:
            self.assertEqual(sm_id.state, 'done',
                             'State stock move should be done')

        # Check invoice created
        self.assertEqual(len(pur_ord.invoice_ids), 1,
                         'There should be a created invoice')
        self.assertEqual(pur_ord.invoice_ids.state, 'draft',
                         'State invoice should be draft')
        pur_ord.invoice_ids.signal_workflow('invoice_open')
        self.assertEqual(pur_ord.invoice_ids.state, 'open',
                         'State invoice should be open')
        # Check invoice line
        self.assertEqual(len(pur_ord.invoice_ids.invoice_line), 2,
                         'Quantity lines incorrect')
        for line in pur_ord.invoice_ids.invoice_line:
            self.assertEqual(line.concept_id, self.no_concept,
                             'ISLR concept not copied')

    def test_02_purchase_order_method_picking(self):
        """Test Purchase Order, invoice method picking"""
        # Create purchase order
        date_now = time.strftime(DEFAULT_SERVER_DATE_FORMAT)
        pur_ord = self.purchase_obj.create({
            'date_order': date_now,
            'location_id': self.location.id,
            'partner_id': self.partner_amd.id,
            'invoice_method': 'picking',
            'pricelist_id': self.pricelist.id,
        })
        self.pur_line_obj.create({
            'product_id': self.product_pc.id,
            'product_qty': 3,
            'price_unit': 10,
            'name': 'PC3',
            'date_planned': date_now,
            'order_id': pur_ord.id,
            'concept_id': self.no_concept.id,
        })
        # Check state purchase order
        self.assertEqual(pur_ord.state, 'draft', 'State should be draft')
        # Set purchase order state approved
        pur_ord.signal_workflow('purchase_confirm')
        self.assertEqual(pur_ord.state, 'approved', 'State should be confirm')
        # Check stock picking created
        picking = self.picking_obj.search([('origin', '=', pur_ord.name)])
        self.assertEqual(len(picking), 1, 'Picking not created')
        self.assertEqual(picking.state, 'assigned',
                         'State picking should be equal to assigned')
        self.assertEqual(len(picking.move_lines), 1,
                         'Quantity lines incorrect')
        # Check invoice not created
        self.assertEqual(pur_ord.invoice_ids, self.invoice_obj,
                         'Not should be a created invoice')

    def test_03_sale_order(self):
        """Test Sale Order"""
        # Create sale order
        date_now = time.strftime(DEFAULT_SERVER_DATE_FORMAT)
        sal_ord = self.sale_obj.create({
            'name': 'Sale Order Test',
            'date_order': date_now,
            'partner_id': self.partner_amd.id,
            'pricelist_id': self.pricelist.id,
        })
        self.sal_line_obj.create({
            'product_id': self.product_pc.id,
            'product_uom_qty': 3,
            'price_unit': 10,
            'name': 'PC3',
            'order_id': sal_ord.id,
            'concept_id': self.no_concept.id,
        })
        self.sal_line_obj.create({
            'product_id': self.product_ipad.id,
            'product_uom_qty': 5,
            'price_unit': 5,
            'name': 'Ipad',
            'order_id': sal_ord.id,
            'concept_id': self.no_concept.id,
        })
        # Check state initial
        self.assertEqual(sal_ord.state, 'draft', 'State should be draft')
        # Set state manual
        sal_ord.signal_workflow('order_confirm')
        self.assertEqual(sal_ord.state, 'manual', 'State should be manual')
        # Create invoice
        sal_ord.signal_workflow('manual_invoice')
        self.assertEqual(sal_ord.state, 'progress', 'State should be progress')
        # Check invoice created
        self.assertEqual(len(sal_ord.invoice_ids), 1, 'Invoice not create')
        self.assertEqual(sal_ord.invoice_ids.state, 'draft',
                         'Invoice state should be draft')
        # Set invoice state open
        sal_ord.invoice_ids.signal_workflow('invoice_open')
        self.assertEqual(sal_ord.invoice_ids.state, 'open',
                         'Invoice state should be open')
        # Check invoice line
        self.assertEqual(len(sal_ord.invoice_ids.invoice_line), 2,
                         'Quantity lines incorrect')
        for line in sal_ord.invoice_ids.invoice_line:
            self.assertEqual(line.concept_id, self.no_concept,
                             'ISLR concept not copied')
