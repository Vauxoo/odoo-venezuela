# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    nhomar@vauxoo.com
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

from osv import osv
from osv import fields
from tools.translate import _



class costo_inicial(osv.osv):
    """
    OpenERP Model : costo_inicial
    """
    
    _name = 'costo.inicial'
    _description = "Costo Inicial Archivo de Importacion."
    
    _columns = {
        'default_code':fields.char('Codigo', size=64, required=False, readonly=False),
        'categ_id':fields.char('Id de la Categoria', size=64, required=False, readonly=False),
        'standard_price':fields.char('Precio Estandard', size=64, required=False, readonly=False),
        'list_price':fields.char('Precio Lista', size=64, required=False, readonly=False),
        'cost_method':fields.char('Metodo de Costos', size=64, required=False, readonly=False),
        'uom_id':fields.char('id UOM', size=64, required=False, readonly=False),
        'uos_id':fields.char('id UOS', size=64, required=False, readonly=False),
        'mes_type':fields.char('Mes Type', size=64, required=False, readonly=False),
        'name':fields.char('Nombre', size=64, required=False, readonly=False),
        'procure_method':fields.char('Procure Method', size=64, required=False, readonly=False),
        'type':fields.char('Type', size=64, required=False, readonly=False),
        'uom_po_id':fields.char('uom_po_id', size=64, required=False, readonly=False),
        'supply_method':fields.char('Supply Method', size=64, required=False, readonly=False),
        'sale_ok':fields.char('Sale Ok.', size=64, required=False, readonly=False),
        'purchase_ok':fields.char('Purchase Ok', size=64, required=False, readonly=False),
        'property_account_income':fields.char('PAI', size=64, required=False, readonly=False),
        'property_account_expense':fields.char('PAE', size=64, required=False, readonly=False),
        'property_stock_account_output':fields.char('PSAO', size=64, required=False, readonly=False),
        'property_stock_account_input':fields.char('PSAI', size=64, required=False, readonly=False),
        'taxes_id':fields.char('Tax Id', size=64, required=False, readonly=False),
        'supplier_taxes_id':fields.char('STID', size=64, required=False, readonly=False),
        'product_qty':fields.char('Prod Quatiny', size=64, required=False, readonly=False),
    }
costo_inicial()
