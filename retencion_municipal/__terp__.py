# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Vauxoo C.A. (http://openerp.com.ve/) All Rights Reserved.
#                    Javier Duran <javier@vauxoo.com>
# 
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

{
	"name" : "Retenciones Municipales",
	"version" : "0.1",
	"author" : "Vauxoo",
	"category" : "Generic Modules",
	"website": "http://wiki.openerp.org.ve/",
	"description": '''
Administración de las retenciones aplicadas a tributos municipales.
''',
	"depends" : ["base","account","retencion_iva"],
	"init_xml" : [],
	"demo_xml" : [

    ], 
	"update_xml" : [
            "security/ir.model.access.csv",
#            "retention_workflow.xml",
            "retencion_munici_view.xml",
            "retencion_munici_sequence.xml",
            "account_invoice_view.xml",
#            "account_view.xml", 
            "partner_view.xml",
#            "stock_view.xml", 
            "retencion_munici_report.xml",
            "retencion_munici_wizard.xml",
    ],
	"active": False,
	"installable": True
}
