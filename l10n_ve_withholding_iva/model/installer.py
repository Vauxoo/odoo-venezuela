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
from openerp.osv import fields, osv
from openerp.tools.translate import _


class WhVatInstaller(osv.osv_memory):

    """ wh_vat_installer
    """
    _name = 'l10n_ve_withholding_iva.installer'
    _inherit = 'res.config.installer'
    _description = __doc__

    def default_get(self, cr, uid, field_list, context=None):
        """ Return information relating to the withholding regime
        """
        # NOTE: use field_list argument instead of fields for fix the pylint
        # error W0621 Redefining name 'fields' from outer scope
        data = super(WhVatInstaller, self).default_get(cr, uid, field_list,
                                                         context=context)
        gaceta = open(addons.get_module_resource(
            'l10n_ve_withholding_iva', 'files',
            'RegimendeRetencionesdelIVA.odt'), 'rb')
        data['gaceta'] = base64.encodestring(gaceta.read())
        return data

    _columns = {
        'name': fields.char('First Data', 34),
        'gaceta': fields.binary(
            'Law related', readonly=True,
            help="Law related where we are referencing this module"),
        'description': fields.text(
            'Description', readonly=True, help='description of the installer'),
    }

    _defaults = {
        'name': 'RegimendeRetencionesdelIVA.odt',
        'description': """
        With this wizard you will configure all needs for work out of the box
        with This module,
        First: Setting if The company will be withholding agent.
        Second: Create Minimal Journals.
        Third: Assign Account to work.
        Fourth: Ask if you have internet conexion and you want to connect to
        SENIAT and update all your partners information.
        """
    }
WhVatInstaller()


class WhIvaConfig(osv.osv_memory):
    _name = 'wh_iva.config'
    _inherit = 'res.config'

    _columns = {
        'name': fields.char('Name', 64, help='name'),
        'wh': fields.boolean('Are You Withholding Agent?',
                             help='if is withholding agent'),
        'journal_purchase_vat': fields.char(
            "Journal Wh VAT Purchase", 64,
            help="Journal for purchase operations involving VAT Withholding"),
        'journal_sale_vat': fields.char(
            "Journal Wh VAT Sale", 64,
            help="Journal for sale operations involving VAT Withholding"),
    }
    _defaults = {
        'journal_purchase_vat': _("Journal VAT Withholding Purchase"),
        'journal_sale_vat': _("Journal VAT Withholding Sale"),
    }

    def _show_company_data(self, cr, uid, context=None):
        """ We only want to show the default company data in demo mode,
        otherwise users tend to forget to fill in the real company data in
        their production databases
        """
        return self.pool.get('ir.model.data').get_object(
            cr, uid, 'base', 'module_meta_information').demo

    def default_get(self, cr, uid, fields_list=None, context=None):
        """ Get default company if any, and the various other fields
        from the company's fields
        """
        defaults = super(WhIvaConfig, self)\
            .default_get(cr, uid, fields_list=fields_list, context=context)
        # Set Vauxoo logo on config Window.
        logo = open(addons.get_module_resource(
            'l10n_ve_withholding_iva', 'images', 'angelfalls.jpg'), 'rb')
        defaults['config_logo'] = base64.encodestring(logo.read())
        if not self._show_company_data(cr, uid, context=context):
            #            defaults['add']=''
            #            defaults['vat']=''
            return defaults
        return defaults

    def _create_journal(self, cr, uid, name, jtype, code):
        """ Create a journal
        @param name: journal name
        @param type: journal type
        @param code: code for journal
        """
        self.pool.get("account.journal").create(cr, uid, {
            'name': name,
            'type': jtype,
            'code': code,
            'view_id': 3, }
        )

    def execute(self, cr, uid, ids, context=None):
        """ In this method I will configure all needs for work out of the box with
        This module,
        First: Setting if The company will be agent of retention.
        Second: Create Minimal Journals.
        Third: Assign Account to work.
        Fourth: Ask if you have internet conexion and you want to connect to
        SENIAT
        and update all your partners information.
        """
        user = self.pool.get('res.users').browse(cr, uid, [uid], context)
        wiz_data = self.read(cr, uid, ids[0], context)
        p_obj = self.pool.get('res.partner')
        partner_id = user[0].company_id.partner_id.id

        if wiz_data.get('journal_purchase_vat'):
            self._create_journal(cr, uid, wiz_data["journal_purchase_vat"],
                                 'iva_purchase', 'VATP')
        if wiz_data.get('journal_sale_vat'):
            self._create_journal(cr, uid, wiz_data['journal_sale_vat'],
                                 'iva_sale', 'VATS')
        if wiz_data.get('wh'):
            p_obj.write(cr, uid, [partner_id], {'wh_iva_agent': 1,
                                                'wh_iva_rate': 75.00})
        else:
            p_obj.write(cr, uid, [partner_id], {'wh_iva_agent': 0,
                                                'wh_iva_rate': 75.00})

WhIvaConfig()
