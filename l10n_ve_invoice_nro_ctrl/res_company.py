#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Humberto Arocha           <humberto@vauxoo.com>
#              María Gabriela Quilarque  <gabriela@vauxoo.com>
#              Nhomar Hernandez          <nhomar@vauxoo.com>
#    Planified by: Humberto Arocha
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

from osv import fields, osv
import tools
from tools.translate import _
from tools import config

class res_company(osv.osv):
    _inherit = 'res.company'
    _columns = {
        'journal_id': fields.many2one('account.journal', 'Journal',required=True,help="Journal used by default for invoices damaged"),
        'account_id': fields.many2one('account.account', 'Account',required=True,help="Account used by default for invoices and lines of invoices damaged"),
        }
res_company()

