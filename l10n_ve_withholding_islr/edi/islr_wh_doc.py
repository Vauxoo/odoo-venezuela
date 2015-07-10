# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############################################################################
#    Credits:
#    Coded by: Humberto Arocha <hbto@vauxoo.com>
#    Planified by: Rafael Silva <rsilvam@vauxoo.com>
#    Audited by: Nhomar Hernandez <nhomar@vauxoo.com>
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


from openerp.osv import osv

from openerp.addons.edi import EDIMixin

ISLR_WH_DOC_LINE_EDI_STRUCT = {
    'sequence': True,
    'name': True,
    # custom: 'date_planned'
    'product_id': True,
    'product_uom': True,
    'price_unit': True,
    # custom: 'product_qty'
    'discount': True,
    'notes': True,

    # fields used for web preview only - discarded on import
    'price_subtotal': True,
}

ISLR_WH_DOC_EDI_STRUCT = {
    'journal_id': True,
    'type': True,
    'code': True,
    'partner_id': True,
    'currency_id': True,
    'date_ret': True,
    'account_id': True,
    'name': True,
    'period_id': True,
    'number': True,
    'date_uid': True,
    'company_id': True,  # -> to be changed into partner
    # custom: 'partner_ref'
    # custom: 'partner_address'
    # custom: 'notes'
    # 'order_line': ISLR_WH_DOC_LINE_EDI_STRUCT,

}


class islr_wh_doc(osv.osv, EDIMixin):
    _inherit = 'islr.wh.doc'

    def edi_export(self, cr, uid, records, edi_struct=None, context=None):
        """Exports a ISLR WH DOC"""
        edi_struct = dict(edi_struct or ISLR_WH_DOC_EDI_STRUCT)
        edi_doc_list = []
        for order in records:
            # generate the main report
            self._edi_generate_report_attachment(cr, uid, order,
                                                 context=context)

            # Get EDI doc based on struct. The result will also contain all
            # metadata fields and attachments.
            edi_doc = super(islr_wh_doc, self).edi_export(
                cr, uid, [order], edi_struct, context)[0]
            edi_doc_list.append(edi_doc)
        return edi_doc_list
