# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    Author: nhomar@vauxoo.com  & Javier Duran <javier@vauxoo.com>
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


{
    "name" : "Automatized Calc for ISLR",
    "version" : "0.1",
    "depends" : ["account","retencion_islr",],
    "author" : "Vauxoo",
    "description" : """
    What do this module:
    Calculate in an automatic way the ISLR for Venezuela.
    Laws:
        "Codigo Organico tributario - GO No. 37305 fecha: 17-10-2001"
        "Ley de Impuestos Sbre la Renta - GO No. 38628 fecha: 16-02-2007"
        "Reglamento de retenciones e Impuestos sobre la renta - Decreto No. 1808 de GO No. 36203 fecha 12-05-1997"
        "Reglamento LISLR Decreto No. 2507 de la GO No. 5662 Extraordinaria de fecha 24-09-2003"
        "regulación del Cumplimiento del Deber de Información y enteramiento de retenciones ISLR - Providencia 0095 - GO No. 39269 del 22-09-2009"
                    """,
    "website" : "http://openerp.com.ve",
    "category" : "Localisation/Accounting",
    "init_xml" : [
    ],
    "demo_xml" : [
    ],
    "update_xml" : [
        "l10n_tax_islr_view.xml",
        "partner_view.xml",
        "product_view.xml",
        "account_invoice_view.xml",
        "retencion_islr_view.xml",
        "data/group.concept.islr.csv",
        "data/concepts.rates.islr.csv"
    ],
    "active": False,
    "installable": True,
}
