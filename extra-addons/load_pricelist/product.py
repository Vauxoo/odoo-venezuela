# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    d$
#    This Modules was developed by Vauxoo, C.A. (<http://openerp.com.ve>)
#    Silver partner of Tiny.
#    author Javier Duran (<javier@vauxoo.com>) & 
#           Nhomar Hernandez (nhomar@vauxoo.com)
#
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
#
##############################################################################

from osv import fields, osv
from tools.translate import _


class pricelist_partnerinfo(osv.osv):
    _inherit = "pricelist.partnerinfo"

    _columns = {
        'date': fields.date('Valid Since'),
    }
pricelist_partnerinfo()



