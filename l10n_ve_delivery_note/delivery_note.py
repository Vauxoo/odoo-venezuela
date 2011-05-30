#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Maria Gabriela Quilarque  <gabrielaquilarque97@gmail.com>
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
from osv import osv
from osv import fields
from tools.translate import _
from tools import config
import time
import pooler

class delivery_note(osv.osv):

    def _amount_all(self, cr, uid, ids, name, args, context=None):
        res = {}
        for invoice in self.browse(cr,uid,ids, context=context):
            res[invoice.id] = {
                'amount_untaxed': 0.0,
                'amount_tax': 0.0,
                'amount_total': 0.0
            }
            for line in invoice.note_line:
                res[invoice.id]['amount_untaxed'] += line.price_subtotal
            for line in invoice.tax_line:
                res[invoice.id]['amount_tax'] += line.amount
            res[invoice.id]['amount_total'] = res[invoice.id]['amount_tax'] + res[invoice.id]['amount_untaxed']
        return res

    def _get_invoice_tax(self, cr, uid, ids, context=None):
        result = {}
        for tax in self.pool.get('delivery.note.tax').browse(cr, uid, ids, context=context):
            result[tax.note_id.id] = True
        return result.keys()

    def _get_invoice_line(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('delivery.note.line').browse(cr, uid, ids, context=context):
            result[line.note_id.id] = True
        return result.keys()

    def _get_currency(self, cr, uid, context):
        user = pooler.get_pool(cr.dbname).get('res.users').browse(cr, uid, [uid])[0]
        if user.company_id:
            return user.company_id.currency_id.id
        else:
            return pooler.get_pool(cr.dbname).get('res.currency').search(cr, uid, [('rate','=',1.0)])[0]

    _name = 'delivery.note'
    _description = 'Delivery Note'
    _order = "number"
    _columns = {
        'origin': fields.char('Origin', size=64, help="Reference of the document that produced this invoice."),
        'number': fields.char('Number', size=32, readonly=True, help="Unique number of the invoice, computed automatically when the invoice is created."),
        'comment': fields.text('Additional Information'),
        'state': fields.selection([
            ('draft','Draft'),
            ('open','Open'),
            ('done','Done'),
            ('cancel','Cancelled')
        ],'State', select=True, readonly=True),
        'date_note': fields.date('Date', readonly=True, help="Keep empty to use the current date"),
        'partner_id': fields.many2one('res.partner', 'Partner', change_default=True, readonly=True, required=True),
        'address_shipping_id': fields.many2one('res.partner.address', 'Shipping Address',readonly=True, required=True),
        'address_invoice_id': fields.many2one('res.partner.address', 'Invoice Address', readonly=True, required=True),
        'payment_term': fields.many2one('account.payment.term', 'Payment Term',
            help="If you use payment terms, the due date will be computed automatically at the generation "\
                "of accounting entries. If you keep the payment term and the due date empty, it means direct payment. "\
                "The payment term may compute several due dates, for example 50% now, 50% in one month."),
        'picking_id': fields.many2one('stock.picking', 'Picking',readonly=True),
        'sale_id': fields.many2one('sale.order', 'Sale Order', ondelete='set null', select=True,readonly=True),
        'note_line': fields.one2many('delivery.note.line', 'note_id', 'Delivery Note Lines', readonly=True,),
        'tax_line': fields.one2many('delivery.note.tax', 'note_id', 'Tax Lines', readonly=True),
        'amount_untaxed': fields.function(_amount_all, method=True, digits=(16, int(config['price_accuracy'])),string='Untaxed',
            store={
                'delivery.note': (lambda self, cr, uid, ids, c={}: ids, ['note_line'], 20),
                'delivery.note.tax': (_get_invoice_tax, None, 20),
                'delivery.note.line': (_get_invoice_line, ['price_unit','note_line_tax_id','quantity','discount'], 20),
            },
            multi='all'),
        'amount_tax': fields.function(_amount_all, method=True, digits=(16, int(config['price_accuracy'])), string='Tax',
            store={
                'delivery.note': (lambda self, cr, uid, ids, c={}: ids, ['note_line'], 20),
                'delivery.note.tax': (_get_invoice_tax, None, 20),
                'delivery.note.line': (_get_invoice_line, ['price_unit','note_line_tax_id','quantity','discount'], 20),
            },
            multi='all'),
        'amount_total': fields.function(_amount_all, method=True, digits=(16, int(config['price_accuracy'])), string='Total',
            store={
                'delivery.note': (lambda self, cr, uid, ids, c={}: ids, ['note_line'], 20),
                'delivery.note.tax': (_get_invoice_tax, None, 20),
                'delivery.note.line': (_get_invoice_line, ['price_unit','note_line_tax_id','quantity','discount'], 20),
            },
            multi='all'),
        'currency_id': fields.many2one('res.currency', 'Currency', required=True, readonly=True),
        'company_id': fields.many2one('res.company', 'Company', required=True,readonly=True),
        'invoice_id': fields.many2one('account.invoice', 'Invoice'),
        'check_total': fields.float('Total', digits=(16, int(config['price_accuracy'])), states={'open':[('readonly',True)],'close':[('readonly',True)]}),
        'note': fields.text('Notes'),
        'invoice_state': fields.selection([
            ("invoiced", "Invoiced"),
            ("2binvoiced", "To Be Invoiced"),
            ("none", "Not from Packing")], "Invoice Status",
            select=True, required=False, readonly=True),
        'nro_ctrl': fields.char('Nro. de Control', size=32, readonly=True, states={'draft':[('readonly',False)]}, help="Control number delivery note"),
    }
    _rec_name = 'number'
    _defaults = {
        'sale_id': lambda *a: False,
        'state': lambda *a: 'draft',
        'currency_id': _get_currency,
        'company_id': lambda self, cr, uid, context: \
                self.pool.get('res.users').browse(cr, uid, uid,
                    context=context).company_id.id,
        'check_total': lambda *a: 0.0,
        'invoice_state': lambda *a: 'none',
    }

    def copy(self, cr, uid, id, default=None, context={}):
        if context.get('split_dn', False):
            default = default.copy()
            return super(delivery_note, self).copy(cr, uid, id, default, context)
        else:
            raise osv.except_osv(_('Error !'),
                _('Impossible to duplicate delivery note.'))
            return super(delivery.note, self).copy(cr, uid, id, default, context)

    def create(self, cr, uid, vals, context={}):
        if context.get('split_dn',False):
            res = super(delivery_note, self).create(cr, uid, vals, context)
            return res
        else:
            if not context.get('delivery_note',False):
                raise osv.except_osv(_('User Error!'),
                     _('The Delivery Note must be created from Outgoing Product!'))
            else:
                return super(delivery_note, self).create(cr, uid, vals, context)

    def unlink(self, cr, uid, ids, context={}):
        raise osv.except_osv(_('Error !'),
            _('Impossible to delete delivery note.'))
        return True

    def _get_payment_term(self, cursor, user, delivery):
        '''Return {'contact': address, 'invoice': address} for invoice'''
        partner_obj = self.pool.get('res.partner')
        partner = delivery.partner_id
        return partner.property_payment_term and partner.property_payment_term.id or False

    def _get_address_invoice(self, cursor, user, delivery):
        '''Return {'contact': address, 'invoice': address} for invoice'''
        partner_obj = self.pool.get('res.partner')
        partner = delivery.sale_id and delivery.sale_id.partner_id
        return partner_obj.address_get(cursor, user, [partner.id],
                ['contact', 'invoice'])

    def _get_comment_invoice(self, cursor, user, delivery):
        '''Return comment string for invoice'''
        return delivery.note or ''
    
    def get_currency_id(self, cursor, user, delivery):
        return False

    def _get_taxes_invoice(self, cursor, user, note_line, type):
        '''Return taxes ids for the note line'''
        taxes = note_line.product_id.taxes_id
        if note_line.note_id and note_line.note_id.partner_id:
            return self.pool.get('account.fiscal.position').map_tax(
                cursor,
                user,
                note_line.note_id.partner_id.property_account_position,
                taxes
            )
        else:
            return map(lambda x: x.id, taxes)

    def _get_account_analytic_invoice(self, cursor, user, delivery, note_line):
        return False

    def _invoice_line_hook(self, cursor, user, note_line, invoice_line_id):
        '''Call after the creation of the invoice line'''
        return

    def _invoice_hook(self, cursor, user, delivery, invoice_id):
        sale_obj = self.pool.get('sale.order')
        if delivery.sale_id:
            sale_obj.write(cursor, user, [delivery.sale_id.id], {
                'invoice_ids': [(4, invoice_id)],
                })
        return
    
    def action_invoice_create(self, cursor, user, ids, journal_id=False,
            group=False, type='out_invoice', context=None):
        '''Return ids of created invoices for the delivery note'''
        invoice_obj = self.pool.get('account.invoice')
        invoice_line_obj = self.pool.get('account.invoice.line')
        invoices_group = {}
        res = {}
        for delivery in self.browse(cursor, user, ids, context=context):
            if delivery.invoice_state != '2binvoiced':
                continue
            
            payment_term_id = False
            partner = delivery.sale_id and delivery.sale_id.partner_id
            if not partner:
                raise osv.except_osv(_('Error, no partner !'),
                    _('Please put a partner on the delivery list if you want to generate invoice.'))
            
            account_id = partner.property_account_receivable.id
            payment_term_id = self._get_payment_term(cursor, user, delivery)

            address_contact_id, address_invoice_id = \
                    self._get_address_invoice(cursor, user, delivery).values()
                    
            comment = self._get_comment_invoice(cursor, user, delivery)
            
            if group and partner.id in invoices_group:
                invoice_id = invoices_group[partner.id]
                invoice = invoice_obj.browse(cursor, user, invoice_id)
                invoice_vals = {
                    'name': (invoice.name or '') + ', ' + (str(delivery.number) or ''),
                    'origin': (invoice.origin or '') + ', ' + (str(delivery.number) or '') + (delivery.sale_id and (':' + delivery.sale_id.name) or ''),
                    'comment': (comment and (invoice.comment and invoice.comment+"\n"+comment or comment)) or (invoice.comment and invoice.comment or ''),
                }
                invoice_obj.write(cursor, user, [invoice_id], invoice_vals, context=context)
            else:
                invoice_vals = {
                    'name': str(delivery.number),
                    'origin': (str(delivery.number) or '') + (delivery.sale_id and (':' + delivery.sale_id.name) or ''),
                    'type': type,
                    'account_id': account_id,
                    'partner_id': partner.id,
                    'address_invoice_id': address_invoice_id,
                    'address_contact_id': address_contact_id,
                    'comment': comment,
                    'payment_term': payment_term_id,
                    'fiscal_position': partner.property_account_position.id,
                    }
                cur_id = self.get_currency_id(cursor, user, delivery)
                if cur_id:
                    invoice_vals['currency_id'] = cur_id
                if journal_id:
                    invoice_vals['journal_id'] = journal_id
                invoice_id = invoice_obj.create(cursor, user, invoice_vals,
                        context=context)
                invoices_group[partner.id] = invoice_id
            res[delivery.id] = invoice_id

            self.write(cursor, user, delivery.id, {'invoice_id':invoice_id}, context=context)

            for note_line in delivery.note_line:

                origin = str(note_line.note_id.number)
                if note_line.note_id.number:
                    origin += ':' + str(note_line.note_id.number)
                if group:
                    name = (str(delivery.number) or '') + '-' + note_line.name
                else:
                    name = note_line.name

                account_id = note_line.product_id.product_tmpl_id.\
                        property_account_income.id
                if not account_id:
                    account_id = note_line.product_id.categ_id.\
                            property_account_income_categ.id

                price_unit = note_line.price_unit
                discount = note_line.discount
                tax_ids = self._get_taxes_invoice(cursor, user, note_line, type)
                account_analytic_id = self._get_account_analytic_invoice(cursor,
                        user, delivery, note_line)
                #set UoS if it's a sale and the delivery doesn't have one
                uos_id = note_line.uos_id and note_line.uos_id.id or False

                account_id = self.pool.get('account.fiscal.position').map_account(cursor, user, partner.property_account_position, account_id)
                invoice_line_id = invoice_line_obj.create(cursor, user, {
                    'name': name,
                    'origin': origin,
                    'invoice_id': invoice_id,
                    'uos_id': uos_id,
                    'product_id': note_line.product_id.id,
                    'account_id': account_id,
                    'price_unit': price_unit,
                    'discount': discount,
                    'quantity': note_line.quantity,
                    'invoice_line_tax_id': [(6, 0, tax_ids)],
                    'account_analytic_id': account_analytic_id,
                    }, context=context)
                self._invoice_line_hook(cursor, user, note_line, invoice_line_id)
            
            
            invoice_obj.button_compute(cursor, user, [invoice_id], context=context,
                    set_total=(type in ('in_invoice', 'in_refund')))
            self.write(cursor, user, [delivery.id], {
                'invoice_state': 'invoiced',
                }, context=context)
            self._invoice_hook(cursor, user, delivery, invoice_id)
            self._concept_id(cursor,user,delivery,invoice_id,context=context)
        self.write(cursor, user, res.keys(), {
            'invoice_state': 'invoiced','state':'done',
            }, context=context)
        return res

    def _concept_id(self,cursor,user,delivery,invoice_id,context=None):
        '''Search concept id for product, from sale order'''
        invoice_brw = self.pool.get('account.invoice').browse(cursor, user, invoice_id)
        for line_invoice in invoice_brw.invoice_line: #lineas de la factura
            for line_orden in delivery.sale_id.order_line: #lineas de la orden de venta
                if line_invoice.product_id==line_orden.product_id: #si es la misma linea
                    self.pool.get('account.invoice.line').write(cursor, user, line_invoice.id, {'concept_id':line_orden.concept_id.id})       
        return True 


    def onchange_partner_id(self, cr, uid, ids, partner_id,
            date_note=False, payment_term=False, partner_bank=False):
        invoice_addr_id = False
        contact_addr_id = False
        delivery_addr_id= False
        partner_payment_term = False

        opt = [('uid', str(uid))]
        if partner_id:

            opt.insert(0, ('id', partner_id))
            res = self.pool.get('res.partner').address_get(cr, uid, [partner_id], ['contact', 'invoice','delivery'])
            contact_addr_id = res['contact']
            invoice_addr_id = res['invoice']
            delivery_addr_id = res['invoice']
            p = self.pool.get('res.partner').browse(cr, uid, partner_id)
            partner_payment_term = p.property_payment_term and p.property_payment_term.id or False

        result = {'value': {
            'address_contact_id': contact_addr_id,
            'address_invoice_id': invoice_addr_id,
            'address_shipping_id': delivery_addr_id,
            'payment_term': partner_payment_term,
            }
        }
        return result

    def button_reset_taxes(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        ctx = context.copy()
        ait_obj = self.pool.get('delivery.note.tax')
        for id in ids:
            cr.execute("DELETE FROM delivery_note_tax WHERE note_id=%s", (id,))
            partner = self.browse(cr, uid, id,context=ctx).partner_id
            if partner.lang:
                ctx.update({'lang': partner.lang})
            for taxe in ait_obj.compute(cr, uid, id, context=ctx).values():
                ait_obj.create(cr, uid, taxe)
         # Update the stored value (fields.function), so we write to trigger recompute
        self.pool.get('delivery.note').write(cr, uid, ids, {'note_line':[]}, context=ctx)    
#        self.pool.get('account.invoice').write(cr, uid, ids, {}, context=context)
        return True

    def button_compute(self, cr, uid, ids, context=None, set_total=False):
        self.button_reset_taxes(cr, uid, ids, context)
        for inv in self.browse(cr, uid, ids):
            if set_total:
                self.pool.get('delivery.note').write(cr, uid, [inv.id], {'check_total': inv.amount_total})
        return True


    def amount_change(self, cr, uid, ids, amount,currency_id=False,company_id=False,date_invoice=False):
        cur_obj = self.pool.get('res.currency')
        company_obj = self.pool.get('res.company')
        company_currency=False
        if company_id:
            company_currency = company_obj.read(cr,uid,[company_id],['currency_id'])[0]['currency_id'][0]
        if currency_id and company_currency:
            amount = cur_obj.compute(cr, uid, currency_id, company_currency, amount, context={'date': date_invoice or time.strftime('%Y-%m-%d')}, round=False)
        return {'value': {'tax_amount':amount}}

    def action_number(self, cr, uid, ids, *args):
        obj_ret = self.browse(cr, uid, ids)[0]
        cr.execute('SELECT id, number ' \
                'FROM delivery_note ' \
                'WHERE id IN ('+','.join(map(str,ids))+')')

        for (id, number) in cr.fetchall():
            if not number:
                number = self.pool.get('ir.sequence').get(cr, uid, 'delivery.note')
            cr.execute('UPDATE delivery_note SET number=%s ' \
                    'WHERE id=%s', (number, id))
        return True

    def action_date(self,cr,uid,ids,*args):
        for deli in self.browse(cr, uid, ids):
            if not deli.date_note:
                self.write(cr, uid, [deli.id], {'date_note':time.strftime('%Y-%m-%d')})
        return True

    def split_delivery_note(self, cr, uid, ids,context):
        for dn in self.browse(cr, uid, ids):
            dn_id =False
            cont2 = 0
            if len(dn.note_line)> dn.company_id.lines_invoice:
                lst = []
                context.update({'split_dn':True})
                dn_id = self.copy(cr, uid,dn.id,
                {
                    'number': dn.number,
                    'note_line': [],
                },context)
                cont = 0
                lst = dn.note_line
                while cont < dn.company_id.lines_invoice:
                    lst.pop(0)
                    cont += 1
                for il in lst:
                    self.pool.get('delivery.note.line').write(cr,uid,il.id,{'note_id':dn_id})
                self.button_compute(cr, uid, [dn.id], set_total=True)

            if dn_id:
                self.button_compute(cr, uid, [dn_id], set_total=True)

    def delivery_note_proforma(self, cr, uid, ids, *args):
        return self.write(cr, uid, ids, {'state':'proforma'})

    def delivery_note_open(self, cr, uid, ids, context=None,*args):
        invoice_obj=self.pool.get('account.invoice')
        self.action_number(cr, uid, ids)
        self.action_date(cr,uid,ids)
        self.split_delivery_note(cr,uid,ids,context)
        self.write(cr, uid, ids, {'state':'open'})
        return True

    def delivery_note_cancel(self, cr, uid, ids, *args):
        return self.write(cr, uid, ids, {'state':'cancel'})

    def action_cancel_draft(self, cr, uid, ids, *args):
        return self.write(cr, uid, ids, {'state':'draft'})

delivery_note()

class delivery_note_line(osv.osv):

    def _amount_line(self, cr, uid, ids, prop, unknow_none,unknow_dict):
        res = {}
        cur_obj=self.pool.get('res.currency')
        for line in self.browse(cr, uid, ids):
            if line.note_id:
                res[line.id] = line.price_unit * line.quantity * (1-(line.discount or 0.0)/100.0)
                cur = line.note_id.currency_id
                res[line.id] = cur_obj.round(cr, uid, cur, res[line.id])
            else:
                res[line.id] = round(line.price_unit * line.quantity * (1-(line.discount or 0.0)/100.0),int(config['price_accuracy']))
        return res

    def _price_unit_default(self, cr, uid, context=None):
        if context is None:
            context = {}
        if 'check_total' in context:
            t = context['check_total']
            for l in context.get('note_line', {}):
                if isinstance(l, (list, tuple)) and len(l) >= 3 and l[2]:
                    tax_obj = self.pool.get('account.tax')
                    p = l[2].get('price_unit', 0) * (1-l[2].get('discount', 0)/100.0)
                    t = t - (p * l[2].get('quantity'))
                    taxes = l[2].get('note_line_tax_id')
                    if len(taxes[0]) >= 3 and taxes[0][2]:
                        taxes=tax_obj.browse(cr, uid, taxes[0][2])
                        for tax in tax_obj.compute(cr, uid, taxes, p,l[2].get('quantity'), context.get('address_invoice_id', False), l[2].get('product_id', False), context.get('partner_id', False)):
                            t = t - tax['amount']
            return t
        return 0

    _name = "delivery.note.line"
    _description = "Delivery Note line"

    def name_get(self, cr, uid, ids, context={}):
        res = []
        for line in self.browse(cr, uid, ids, context):
            res.append(line.id, (line.product_id.code or '/'))
        return res

    _columns = {
        'name': fields.char('Name', size=64, required=False, select=True),
        'note_id': fields.many2one('delivery.note', 'Delivery Note Ref', ondelete='cascade', select=False),
        'uos_id': fields.many2one('product.uom', 'Unit of Measure', ondelete='set null'),
        'product_id': fields.many2one('product.product', 'Product', ondelete='set null',required=True),
        'price_unit': fields.float('Unit Price', required=True, digits=(16, int(config['price_accuracy']))),
        'price_subtotal': fields.function(_amount_line, method=True, string='Subtotal',store=True, type="float", digits=(16, int(config['price_accuracy']))),
        'quantity': fields.float('Quantity', required=True),
        'note_line_tax_id': fields.many2many('account.tax', 'account_note_line_tax_id', 'note_line_id', 'taxx_id', 'Taxes', domain=[('parent_id','=',False)]),
        'discount': fields.float('Discount (%)', digits=(16, int(config['price_accuracy']))),
        'note': fields.text('Notes'),
        }
    _defaults = {
        'quantity': lambda *a: 1,
        'discount': lambda *a: 0.0,
        'price_unit': _price_unit_default,
    }
delivery_note_line()

class delivery_note_tax(osv.osv):
    _name = "delivery.note.tax"
    _description = "Delivery Note Tax"
    _columns = {
        'note_id': fields.many2one('delivery.note', 'Delivery Note Ref', ondelete='cascade', select=True),
        'name': fields.char('Tax Description', size=64, required=True),
        'account_id': fields.many2one('account.account', 'Tax Account', required=False, domain=[('type','<>','view'),('type','<>','income'), ('type', '<>', 'closed')]),
        'base': fields.float('Base', digits=(16,int(config['price_accuracy']))),
        'amount': fields.float('Amount', digits=(16,int(config['price_accuracy']))),
        'manual': fields.boolean('Manual'),
        'sequence': fields.integer('Sequence'),

        'base_code_id': fields.many2one('account.tax.code', 'Base Code', help="The account basis of the tax declaration."),
        'base_amount': fields.float('Base Code Amount', digits=(16,int(config['price_accuracy']))),
        'tax_code_id': fields.many2one('account.tax.code', 'Tax Code', help="The tax basis of the tax declaration."),
        'tax_amount': fields.float('Tax Code Amount', digits=(16,int(config['price_accuracy']))),
    }
    _order = 'sequence'
    _defaults = {
        'manual': lambda *a: 1,
        'base_amount': lambda *a: 0.0,
        'tax_amount': lambda *a: 0.0,
    }

    def base_change(self, cr, uid, ids, base,currency_id=False,company_id=False,date_invoice=False):
        cur_obj = self.pool.get('res.currency')
        company_obj = self.pool.get('res.company')
        company_currency=False
        if company_id:            
            company_currency = company_obj.read(cr,uid,[company_id],['currency_id'])[0]['currency_id'][0]
        if currency_id and company_currency:
            base = cur_obj.compute(cr, uid, currency_id, company_currency, base, context={'date': date_note or time.strftime('%Y-%m-%d')}, round=False)
        return {'value': {'base_amount':base}}

    def amount_change(self, cr, uid, ids, amount,currency_id=False,company_id=False,date_note=False):
        cur_obj = self.pool.get('res.currency')
        company_obj = self.pool.get('res.company')
        company_currency=False
        if company_id:
            company_currency = company_obj.read(cr,uid,[company_id],['currency_id'])[0]['currency_id'][0]
        if currency_id and company_currency:
            amount = cur_obj.compute(cr, uid, currency_id, company_currency, amount, context={'date': date_note or time.strftime('%Y-%m-%d')}, round=False)
        return {'value': {'tax_amount':amount}}

    def compute(self, cr, uid, note_id, context={}):
        tax_grouped = {}
        tax_obj = self.pool.get('account.tax')
        cur_obj = self.pool.get('res.currency')
        inv = self.pool.get('delivery.note').browse(cr, uid, note_id, context)
        cur = inv.currency_id
        company_currency = inv.company_id.currency_id.id

        for line in inv.note_line:
            for tax in tax_obj.compute(cr, uid, line.note_line_tax_id, (line.price_unit* (1-(line.discount or 0.0)/100.0)), line.quantity, inv.address_invoice_id.id, line.product_id, inv.partner_id):
                val={}
                val['note_id'] = inv.id
                val['name'] = tax['name']
                val['amount'] = tax['amount']
                val['manual'] = False
                val['sequence'] = tax['sequence']
                val['base'] = tax['price_unit'] * line['quantity']

                val['base_code_id'] = tax['base_code_id']
                val['tax_code_id'] = tax['tax_code_id']
                val['base_amount'] = cur_obj.compute(cr, uid, inv.currency_id.id, company_currency, val['base'] * tax['base_sign'], context={'date': inv.date_note or time.strftime('%Y-%m-%d')}, round=False)
                val['tax_amount'] = cur_obj.compute(cr, uid, inv.currency_id.id, company_currency, val['amount'] * tax['tax_sign'], context={'date': inv.date_note or time.strftime('%Y-%m-%d')}, round=False)

                key = (val['tax_code_id'], val['base_code_id'])
                if not key in tax_grouped:
                    tax_grouped[key] = val
                else:
                    tax_grouped[key]['amount'] += val['amount']
                    tax_grouped[key]['base'] += val['base']
                    tax_grouped[key]['base_amount'] += val['base_amount']
                    tax_grouped[key]['tax_amount'] += val['tax_amount']

        for t in tax_grouped.values():
            t['base'] = cur_obj.round(cr, uid, cur, t['base'])
            t['amount'] = cur_obj.round(cr, uid, cur, t['amount'])
            t['base_amount'] = cur_obj.round(cr, uid, cur, t['base_amount'])
            t['tax_amount'] = cur_obj.round(cr, uid, cur, t['tax_amount'])
        return tax_grouped

delivery_note_tax()





