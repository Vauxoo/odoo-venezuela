# coding: utf-8
###############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://www.vauxoo.com>).
#    All Rights Reserved
###############################################################################
#    Credits:
#    Coded by: Katherine Zaoral <kathy@vauxoo.com>
#    Planified by: Humberto Arocha <hbto@vauxoo.com>
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

from openerp.osv import fields, osv
from openerp.tools.translate import _


class PartnerIncomeWhPrintwizard(osv.TransientModel):

    """
    This wizard will print the islr reports for a given partner.
    """
    def _get_company(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid)
        return user.company_id.id

    _name = 'partner.income.wh.print'
    _description = 'Partner Income Withholding Print'
    _columns = {
        'period_id': fields.many2one(
            'account.period',
            string='Period',
            required=True,
            help='Fiscal period to be use in the report.'),
        'partner_id': fields.many2one(
            'res.partner',
            string='Partner',
            required=True,
            help='Partner to be use in the report.'),
        'company_id': fields.many2one(
            'res.company',
            string='Company',
            required=True,
            default=lambda s: s._get_company(),
            help='Company'),
        'iwdl_ids': fields.many2many(
            'islr.wh.doc.line',
            'rel_wizard_iwdl',
            'iwdl_list',
            'iwdl_ids',
            string='ISLR WH Doc Line',
            help='ISLR WH Doc Line'),
    }

    def get_partner_address(self, cr, uid, ids, idp, context=None):
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        rp_obj = self.pool.get('res.partner')
        addr = rp_obj.browse(cr, uid, idp, context=context)
        addr_inv = (addr.street and ('%s, ' % addr.street.title()) or '') + \
            (addr.zip and ('Codigo Postal: %s, ' % addr.zip) or '') +\
            (addr.city and ('%s, ' % addr.city.title()) or '') + \
            (addr.state_id and ('%s, ' % addr.state_id.name.title()) or '') + \
            (addr.country_id and
             ('%s ' % addr.country_id.name.title()) or
             '') or _('NO INVOICE ADDRESS DEFINED')
        return addr_inv

    def print_report(self, cr, uid, ids, context=None):
        """
        @return an action that will print a report.
        """
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        iwdl_obj = self.pool.get('islr.wh.doc.line')
        brw = self.browse(cr, uid, ids[0], context=context)
        iwdl_ids = iwdl_obj.search(cr, uid, [
            ('invoice_id.partner_id', '=', brw.partner_id.id),
            ('islr_wh_doc_id.period_id', '=', brw.period_id.id),
            ('islr_wh_doc_id.type', '=', 'in_invoice'),
            ('islr_wh_doc_id.state', '=', 'done')], context=context)
        if iwdl_ids:
            self.write(cr, uid, ids, {
                'iwdl_ids': [(6, 0, iwdl_ids)]}, context=context)
        else:
            raise osv.except_osv(_(u'No Withholdings'),
                                 _(u'No Income Withholding for %s'
                                   % brw.partner_id.name.upper()))
        data = dict()
        data['ids'] = ids
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'l10n.ve.partner.income.wh.report', 'datas': data}
