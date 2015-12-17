# coding: utf-8
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############################################################################
#    Credits:
#    Coded by: <nhomar@vauxoo.com>
#    Planified by: Nhomar Hernandez
#    Audited by: Vauxoo C.A.
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
###############################################################################
import base64

import openerp.addons as addons
from openerp import models, fields, api


class WhVatInstaller(models.TransientModel):

    """ wh_vat_installer
    """
    _name = 'l10n_ve_withholding_iva.installer'
    _inherit = 'res.config.installer'
    _description = __doc__

    @api.model
    def default_get(self, field_list):
        """ Return information relating to the withholding regime
        """
        # NOTE: use field_list argument instead of fields for fix the pylint
        # error W0621 Redefining name 'fields' from outer scope
        data = super(WhVatInstaller, self).default_get(field_list)
        gaceta = open(addons.get_module_resource(
            'l10n_ve_withholding_iva', 'files',
            'RegimendeRetencionesdelIVA.odt'), 'rb')
        data['gaceta'] = base64.encodestring(gaceta.read())
        return data

    name = fields.Char(
        string='First Data', size=34,
        default='RegimendeRetencionesdelIVA.odt')
    gaceta = fields.Binary(
        string='Law related', readonly=True,
        help="Law related where we are referencing this module")
    description = fields.Text(
        string='Description', readonly=True,
        default="""
        With this wizard you will configure all needs for work out of the box
        with This module,
        First: Setting if The company will be withholding agent.
        Second: Create Minimal Journals.
        Third: Assign Account to work.
        Fourth: Ask if you have internet conexion and you want to connect to
        SENIAT and update all your partners information.
        """,
        help='description of the installer')


class WhIvaConfig(models.TransientModel):
    _name = 'wh_iva.config'
    _inherit = 'res.config'

    name = fields.Char(string='Name', size=64, help='name')
    wh = fields.Boolean(
        string='Are You Withholding Agent?',
        help='if is withholding agent')
    journal_purchase_vat = fields.Char(
        string="Journal Wh VAT Purchase", size=64,
        default="Journal VAT Withholding Purchase",
        help="Journal for purchase operations involving VAT Withholding")
    journal_sale_vat = fields.Char(
        string="Journal Wh VAT Sale", size=64,
        default="Journal VAT Withholding Sale",
        help="Journal for sale operations involving VAT Withholding")

    @api.model
    def _show_company_data(self):
        """ We only want to show the default company data in demo mode,
        otherwise users tend to forget to fill in the real company data in
        their production databases
        """
        return self.env['ir.model.data'].get_object(
            'base', 'module_meta_information').demo

    @api.model
    def default_get(self, fields_list):
        """ Get default company if any, and the various other fields
        from the company's fields
        """
        defaults = super(WhIvaConfig, self).default_get(fields_list)
        # Set Vauxoo logo on config Window.
        logo = open(addons.get_module_resource(
            'l10n_ve_withholding_iva', 'images', 'angelfalls.jpg'), 'rb')
        defaults['config_logo'] = base64.encodestring(logo.read())
        return defaults

    @api.model
    def _create_journal(self, name, jtype, code):
        """ Create a journal
        @param name: journal name
        @param type: journal type
        @param code: code for journal
        """
        self.env['account.journal'].create({
            'name': name,
            'type': jtype,
            'code': code,
            'view_id': 3, }
        )

    @api.multi
    def execute(self):
        """ In this method I will configure all needs for work out of the box with
        This module,
        First: Setting if The company will be agent of retention.
        Second: Create Minimal Journals.
        Third: Assign Account to work.
        Fourth: Ask if you have internet conexion and you want to connect to
        SENIAT
        and update all your partners information.
        """
        partner = self.env.user.company_id.partner_id.id
        if self.journal_purchase_vat:
            self._create_journal(self.journal_purchase_vat,
                                 'iva_purchase', 'VATP')
        if self.journal_sale_vat:
            self._create_journal(self.journal_sale_vat,
                                 'iva_sale', 'VATS')
        if self.wh:
            partner.write({'wh_iva_agent': 1, 'wh_iva_rate': 75.00})
        else:
            partner.write({'wh_iva_agent': 0, 'wh_iva_rate': 75.00})
