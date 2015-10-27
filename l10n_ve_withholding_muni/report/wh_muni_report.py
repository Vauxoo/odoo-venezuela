# coding: utf-8
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############################################################################
#    Credits:
#    Coded by: Javier Duran <javier@vauxoo.com>
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

import time

from openerp.report import report_sxw
from openerp.tools.translate import _


class WhMuniReport(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(WhMuniReport, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'get_partner_addr': self._get_partner_addr,
            'get_rif': self._get_rif
        })

    def _get_partner_addr(self, idp=False):
        """ Return partner address
        """
        if not idp:
            return []

        addr_obj = self.pool.get('res.partner')
        addr_inv = _('NO INVOICE ADDRESS DEFINED')
        if idp:
            addr = addr_obj.browse(self.cr, self.uid, idp)
            addr_inv = (addr.type == 'invoice' and (addr.street or '') + ' ' +
                        (addr.street2 or '') + ' ' + (addr.zip or '') + ' ' +
                        (addr.city or '') + ' ' +
                        (addr.country_id and addr.country_id.name or '') +
                        ', TELF.:' + (addr.phone or '') or
                        _('NO INVOICE ADDRESS DEFINED'))
        return addr_inv

    def _get_rif(self, vat=''):
        """ Return partner rif
        """
        if not vat:
            return []
        return vat[2:].replace(' ', '')


report_sxw.report_sxw(
    'report.wh.muni.report',
    'account.wh.munici',
    rml='l10n_ve_withholding_muni/report/wh_muni_report.rml',
    parser=WhMuniReport,
    header=False
)
