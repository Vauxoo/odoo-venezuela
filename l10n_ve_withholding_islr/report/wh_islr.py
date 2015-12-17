# coding: utf-8
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############################################################################
#    Credits:
#    Coded by: Maria Gabriela Quilarque  <gabriela@openerp.com.ve>
#    Planified by: Nhomar Hernandez
#    Finance by: Helados Gilda, C.A. http://heladosgilda.com.ve
#    Audited by: Humberto Arocha humberto@openerp.com.ve
#############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
##############################################################################

from openerp.report import report_sxw
from openerp.tools.translate import _


class RepComprobanteIslr(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(RepComprobanteIslr, self).__init__(cr, uid, name,
                                                 context=context)
        self.localcontext.update({
            'get_partner_addr': self._get_partner_addr,
        })

    def _get_partner_addr(self, idp=False):
        """ Return address partner
        """
        if not idp:
            return []

        addr_obj = self.pool.get('res.partner')
        addr_inv = _('NO FISCAL ADDRESS DEFINED')
        addr_inv = {}
        if idp:
            addr = addr_obj.browse(self.cr, self.uid, idp)
            addr_inv = (
                (addr.street and ('%s, ' % addr.street.title()) or '') +
                (addr.zip and ('Codigo Postal: %s, ' % addr.zip) or '') +
                (addr.city and ('%s, ' % addr.city.title()) or '') +
                (addr.state_id and ('%s, ' % addr.state_id.name.title()) or
                 '') + (addr.country_id and
                        ('%s ' % addr.country_id.name.title()) or
                        '') or _('NO INVOICE ADDRESS DEFINED'))
            # addr_inv = (addr.street or '')+' '+(addr.street2 or`` '')+'
            # '+(addr.zip or '')+ ' '+(addr.city or '')+ ' '+ (addr.country_id
            # and addr.country_id.name or '')+ ', TELF.:'+(addr.phone or '')
        return addr_inv


report_sxw.report_sxw(
    'report.islr.wh.doc',
    'islr.wh.doc',
    rml='l10n_ve_withholding_islr/report/wh_islr_report.rml',
    parser=RepComprobanteIslr,
    header=False
)
