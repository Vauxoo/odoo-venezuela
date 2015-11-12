# coding: utf-8
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############################################################################
#    Credits:
#    Coded by: Vauxoo C.A.
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


class SplitInvoiceConfig(osv.osv_memory):

    """ Fiscal Requirements installer wizard
    """
    _name = 'split.invoice.config'
    _inherit = 'res.config'
    _description = __doc__

    def default_get(self, cr, uid, fields_list=None, context=None):
        """ Default value to the config_logo field
        """
        defaults = super(SplitInvoiceConfig, self).default_get(
            cr, uid, fields_list=fields_list, context=context)
        logo = open(addons.get_module_resource(
            'l10n_ve_split_invoice', 'images', 'puente-maracaibo.jpg'), 'rb')
        defaults['config_logo'] = base64.encodestring(logo.read())
        return defaults

    def execute(self, cr, uid, ids, context=None):
        """
        In this method I will configure the maximum number of lines in your
        invoices.
        """
        wiz_data = self.browse(cr, uid, ids[0])
        if wiz_data.name < 1:
            raise osv.except_osv(
                _('Error !'),
                _('The number of customer invoice lines must be at least one'))
        company = self.pool.get('res.users').browse(cr, uid, uid).company_id
        company_obj = self.pool.get('res.company')
        company_id = company_obj.search(cr, uid, [('id', '=', company.id)])
        data = {'lines_invoice': wiz_data.name}
        company_obj.write(cr, uid, company_id, data)

    _columns = {
        'name': fields.integer(
            'Max Invoice Lines', required=True, default=50,
            help='Select the maximum number of lines in your customer'
                 ' invoices'),
    }

SplitInvoiceConfig()
