# coding: utf-8
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############################################################################
#    Credits:
#    Coded by: Maria Gabriela Quilarque  <gabrielaquilarque97@gmail.com>
#    Planified by: Nhomar Hernandez
#    Finance by: Helados Gilda, C.A. http://heladosgilda.com.ve
#    Audited by: Humberto Arocha humberto@openerp.com.ve
#############################################################################
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
##############################################################################

from openerp.osv import fields, osv
from openerp.tools.translate import _


class WizardInvoiceNroCtrl(osv.osv_memory):

    _name = "wizard.invoice.nro.ctrl"
    _columns = {
        'invoice_id': fields.many2one(
            'account.invoice', 'Invoice',
            help="Invoice to be declared damaged."),
        'date': fields.date(
            'Date',
            help="Date used for declared damaged paper. Keep empty to use the"
                 " current date"),
        'sure': fields.boolean('Are You Sure?'),
    }

    def action_invoice_create(self, cr, uid, ids, wizard_brw, inv_brw,
                              context=None):
        """
        If the invoice has control number, this function is responsible for
        passing the bill to damaged paper
        @param wizard_brw: nothing for now
        @param inv_brw: damaged paper
        """
        invoice_line_obj = self.pool.get('account.invoice.line')
        invoice_obj = self.pool.get('account.invoice')
        acc_mv_obj = self.pool.get('account.move')
        acc_mv_l_obj = self.pool.get('account.move.line')
        tax_obj = self.pool.get('account.invoice.tax')
        invoice = {}
        if inv_brw.nro_ctrl:
            invoice.update({
                'name': 'PAPELANULADO_NRO_CTRL_%s' % (
                    inv_brw.nro_ctrl and inv_brw.nro_ctrl or ''),
                'state': 'paid',
                'tax_line': [],
            })
        else:
            raise osv.except_osv(
                _('Validation error!'),
                _("You can run this process just if the invoice have Control"
                  " Number, please verify the invoice and try again."))
        invoice_obj.write(cr, uid, [inv_brw.id], invoice, context=context)
        for line in inv_brw.invoice_line:
            invoice_line_obj.write(
                cr, uid, [line.id],
                {'quantity': 0.0, 'invoice_line_tax_id': [],
                 'price_unit': 0.0}, context=context)

        tax_ids = self.pool.get('account.tax').search(cr, uid, [],
                                                      context=context)
        tax = tax_obj.search(cr, uid,
                             [('invoice_id', '=', inv_brw and inv_brw.id)],
                             context=context)
        if tax:
            tax_obj.write(cr, uid, tax[0], {'invoice_id': []}, context=context)
        tax_obj.create(cr, uid, {
            'name': 'SDCF',
            'tax_id': tax_ids and tax_ids[0],
            'amount': 0.00,
            'tax_amount': 0.00,
            'base': 0.00,
            'account_id': inv_brw.company_id.acc_id.id,
            'invoice_id': inv_brw and inv_brw.id}, {})
        move_id = inv_brw.move_id and inv_brw.move_id.id

        if move_id:
            acc_mv_obj.button_cancel(cr, uid, [inv_brw.move_id.id],
                                     context=context)
            acc_mv_obj.write(cr, uid, [inv_brw.move_id.id],
                             {'ref': 'Damanged Paper'}, context=context)
            acc_mv_l_obj.unlink(cr, uid,
                                [i.id for i in inv_brw.move_id.line_id])
        return inv_brw.id

    def new_open_window(self, cr, uid, ids, list_ids, xml_id, module,
                        context=None):
        """ Generate new window at view form or tree
        """
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
        result = mod_obj._get_id(cr, uid, module, xml_id)
        imd_id = mod_obj.read(cr, uid, result, ['res_id'])['res_id']
        result = act_obj.read(cr, uid, imd_id)
        result['res_id'] = list_ids
        return result

    def create_invoice(self, cr, uid, ids, context=None):
        """ Create a invoice refund
        """
        context = context or {}
        wizard_brw = self.browse(cr, uid, ids, context=context)
        inv_id = context.get('active_id')
        for wizard in wizard_brw:
            if not wizard.sure:
                raise osv.except_osv(
                    _("Validation error!"),
                    _("Please confirm that you know what you're doing by"
                      " checking the option bellow!"))
            if (wizard.invoice_id and wizard.invoice_id.company_id.jour_id and
                    wizard.invoice_id and wizard.invoice_id.company_id.acc_id):
                inv_id = self.action_invoice_create(cr, uid, ids, wizard,
                                                    wizard.invoice_id, context)
            else:
                raise osv.except_osv(
                    _('Validation error!'),
                    _("You must go to the company form and configure a journal"
                      " and an account for damaged invoices"))
        return self.new_open_window(cr, uid, ids, [inv_id],
                                    'action_invoice_tree1', 'account')

WizardInvoiceNroCtrl()
