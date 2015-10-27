# coding: utf-8
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############################################################################
#    Credits:
#    Coded by: Yanina Gabriela Aular Osorio  <yanina.aular@vauxoo.com>
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


class ListWhIslr(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(ListWhIslr, self).__init__(cr, uid, name, context=context)


report_sxw.report_sxw(
    'report.islr.xml.wh.doc',
    'islr.xml.wh.doc',
    rml='l10n_ve_withholding_islr/report/list_wh_islr_report.rml',
    parser=ListWhIslr,
    header=False
)
