#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Humberto Arocha           <humberto@openerp.com.ve>
#              Maria Gabriela Quilarque  <gabrielaquilarque97@gmail.com>
#              Javier Duran              <javier.duran@netquatro.com>             
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
import datetime


class islr_wh_doc(osv.osv):

    def _get_type(self, cr, uid, context=None):
        if context is None:
            context = {}
        type = context.get('type', 'in_invoice')
        return type

    def _get_journal(self, cr, uid, context):
        if context is None:
            context = {}
        type_inv = context.get('type')
        type2journal = {'out_invoice': 'retislrSale', 'in_invoice': 'retislrPurchase', 'out_refund': 'retislrSale', 'in_refund': 'retislrPurchase'}
        journal_obj = self.pool.get('account.journal')
        res = journal_obj.search(cr, uid, [('type', '=', type2journal.get(type_inv, 'retislrPurchase'))], limit=1)
        if res:
            return res[0]
        else:
            return False

    def _get_currency(self, cr, uid, context):
        user = self.pool.get('res.users').browse(cr, uid, [uid])[0]
        if user.company_id:
            return user.company_id.currency_id.id
        else:
            return self.pool.get('res.currency').search(cr, uid, [('rate','=',1.0)])[0]

    def _get_amount_total(self,cr,uid,ids,name,args,context=None):
        res = {}
        for rete in self.browse(cr,uid,ids,context):
            res[rete.id]= 0.0
            for line in rete.concept_ids:
                res[rete.id] += line.amount
        return res

    def _get_period(self,cr,uid,ids,name,args,context={}):
        res = {}
        wh_doc_brw = self.browse(cr,uid,ids, context=None)
        for doc in wh_doc_brw:
            if doc.date_ret:
                period_ids = self.pool.get('account.period').search(cr,uid,[('date_start','<=',doc.date_ret or time.strftime('%Y-%m-%d')),('date_stop','>=',doc.date_ret or time.strftime('%Y-%m-%d'))])
                if len(period_ids):
                    period_id = period_ids[0]
                res[doc.id] = period_id
        return res


    _name = "islr.wh.doc"
    _columns= {
        'name': fields.char('Descripcion', size=64, select=True,readonly=True, states={'draft':[('readonly',False)]}, required=True, help="Descripcion del Comprobante"),
        'code': fields.char('Codigo', size=32, readonly=True, states={'draft':[('readonly',False)]}, help="Referencia del Comprobante"),
        'number': fields.char('Numero de Retencion', size=32, readonly=True, states={'draft':[('readonly',False)]}, help="Nro. del Comprobante"),
        'type': fields.selection([
            ('out_invoice','Customer Invoice'),
            ('in_invoice','Supplier Invoice'),
            ('out_refund','Customer Refund'),
            ('in_refund','Supplier Refund'),
            ],'Tipo', readonly=True, select=True, help="Tipo del Comprobante"),
        'state': fields.selection([
            ('draft','Draft'),
            ('confirmed', 'Confirmed'),
            ('done','Done'),
            ('cancel','Cancelled')
            ],'Estado', select=True, readonly=True, help="Estado del Comprobante"),
        'date_ret': fields.date('Fecha Contable', help="Fecha tomada para seleccionar el periodo fiscal, dejar en blanco en caso de utilizar la actual"),
        'date_uid': fields.date('Fecha del Comprobante', readonly=True, help="Fecha de realizacion del comprobante de retencion"),
        'period_id': fields.function(_get_period, method=True, required=False, type='many2one',relation='account.period', string='Periodo', help="Periodo donde se realizaran los asientos contables."),
        'account_id': fields.many2one('account.account', 'Cuenta', required=True, readonly=True, states={'draft':[('readonly',False)]}, help="Cuenta donde se cargaran los montos retenidos del I.S.L.R."),
        'partner_id': fields.many2one('res.partner', 'Partner', readonly=True, required=True, states={'draft':[('readonly',False)]}, help="Proveedor o Cliente al cual se retiene o te retiene"),
        'currency_id': fields.many2one('res.currency', 'Moneda', required=True, readonly=True, states={'draft':[('readonly',False)]}, help="Moneda enla cual se realiza la operacion"),
        'journal_id': fields.many2one('account.journal', 'Diario', required=True,readonly=True, states={'draft':[('readonly',False)]}, help="Diario donde se registran los asientos"),
        'company_id': fields.many2one('res.company', 'Compania', required=True, help="Compania"),
        'amount_total_ret':fields.function(_get_amount_total,method=True, digits=(16, int(config['price_accuracy'])), string='Amount Total', help="Monto Total Retenido"),
        'concept_ids': fields.one2many('islr.wh.doc.line','islr_wh_doc_id','Lineas del Documento de Retencion de ISLR', readonly=True, states={'draft':[('readonly',False)]}),
        'invoice_ids':fields.one2many('islr.wh.doc.invoices','islr_wh_doc_id','Facturas Retenidas'),
        'invoice_id':fields.many2one('account.invoice','Factura',readonly=True,help="Factura afectada, para realizar el asiento contable"),
    }

    _defaults = {
        'code': lambda obj, cr, uid, context: obj.pool.get('islr.wh.doc').retencion_seq_get(cr, uid, context),
        'type': _get_type,
        'state': lambda *a: 'draft',
        'journal_id': _get_journal,
        'currency_id': _get_currency,
        'company_id': lambda self, cr, uid, context: \
                self.pool.get('res.users').browse(cr, uid, uid,
                    context=context).company_id.id,
    }


    def retencion_seq_get(self, cr, uid, context=None):
        pool_seq=self.pool.get('ir.sequence')
        cr.execute("select id,number_next,number_increment,prefix,suffix,padding from ir_sequence where code='islr.wh.doc' and active=True")
        res = cr.dictfetchone()
        if res:
            if res['number_next']:
                return pool_seq._process(res['prefix']) + '%%0%sd' % res['padding'] % res['number_next'] + pool_seq._process(res['suffix'])
            else:
                return pool_seq._process(res['prefix']) + pool_seq._process(res['suffix'])
        return False

    def onchange_partner_id(self, cr, uid, ids, type, partner_id):
        acc_id = False
        if partner_id:
            p = self.pool.get('res.partner').browse(cr, uid, partner_id)
            if type in ('out_invoice', 'out_refund'):
                acc_id = p.property_account_receivable.id
            else:
                acc_id = p.property_account_payable.id
        result = {'value': {
            'account_id': acc_id}
        }

        return result

    def create(self, cr, uid, vals, context=None, check=True):
        if not context:
            context={}
        code = self.pool.get('ir.sequence').get(cr, uid, 'islr.wh.doc')
        vals['code'] = code
        return super(islr_wh_doc, self).create(cr, uid, vals, context)

    def action_confirm1(self, cr, uid, ids, context={}):
        return self.write(cr, uid, ids, {'state':'confirmed'})


    def action_number(self, cr, uid, ids, *args):
        obj_ret = self.browse(cr, uid, ids)[0]
        cr.execute('SELECT id, number ' \
                'FROM islr_wh_doc ' \
                'WHERE id IN ('+','.join(map(str,ids))+')')

        for (id, number) in cr.fetchall():
            if not number:
                number = self.pool.get('ir.sequence').get(cr, uid, 'islr.wh.doc.%s' % obj_ret.type)
            cr.execute('UPDATE islr_wh_doc SET number=%s ' \
                    'WHERE id=%s', (number, id))
        return True

    def action_done1(self, cr, uid, ids, context={}):
        self.action_number(cr, uid, ids)
        self.action_move_create(cr, uid, ids)
        self.write(cr, uid, ids, {'state':'done'})
        return True

    def action_cancel1(self,cr,uid,ids,context={}):
        self.cancel_move(cr,uid,ids)
        return True

    def cancel_move (self,cr,uid,ids, *args):
        ret_brw = self.browse(cr, uid, ids)
        account_move_obj = self.pool.get('account.move')
        for ret in ret_brw:
            if ret.state == 'done':
                for ret_line in ret.concept_ids:
                    account_move_obj.button_cancel(cr, uid, [ret_line.move_id.id])
                    delete = account_move_obj.unlink(cr, uid,[ret_line.move_id.id])
                if delete:
                    self.write(cr, uid, ids, {'state':'cancel'})
            else:
                self.write(cr, uid, ids, {'state':'cancel'})
        return True
        
    def action_cancel_draft(self,cr,uid,ids, *args):
        self.write(cr, uid, ids, {'state':'draft'})

    def action_move_create(self, cr, uid, ids, *args):

        wh_doc_obj = self.pool.get('islr.wh.doc.line')
        context = {}

        for ret in self.browse(cr, uid, ids):
            if not ret.date_uid:
                self.write(cr, uid, [ret.id], {'date_uid':time.strftime('%Y-%m-%d')})

            if not ret.date_ret:
                self.write(cr, uid, [ret.id], {'date_ret':time.strftime('%Y-%m-%d')})
            
            period_id = ret.period_id and ret.period_id.id or False
            journal_id = ret.journal_id.id
            
            if not period_id:
                period_ids = self.pool.get('account.period').search(cr,uid,[('date_start','<=',ret.date_ret or time.strftime('%Y-%m-%d')),('date_stop','>=',ret.date_ret or time.strftime('%Y-%m-%d'))])
                if len(period_ids):
                    period_id = period_ids[0]
                else:
                    raise osv.except_osv(_('Warning !'), _("No se encontro un periodo fiscal para esta fecha: '%s' por favor verificar.!") % (ret.date_ret or time.strftime('%Y-%m-%d')))

            if ret.concept_ids:
                for line in ret.concept_ids:
                    if ret.type in ('in_invoice', 'in_refund'):
                        if line.concept_id.property_retencion_islr_payable:
                            acc_id = line.concept_id.property_retencion_islr_payable.id
                        else:
                            raise osv.except_osv(_('Invalid action !'),_("Imposible realizar Retencion ISLR, debido a que la cuenta contable para retencion de venta no esta asignada al Concepto '%s' !")% (line.concept_id.name))
                    else:
                        if  line.concept_id.property_retencion_islr_receivable:
                            acc_id = line.concept_id.property_retencion_islr_receivable.id
                        else:
                            raise osv.except_osv(_('Invalid action !'),_("Imposible realizar Retencion ISLR, debido a que la cuenta contable para retencion de compra no esta asignada al Concepto '%s' !") % (line.concept_id.name))

                    writeoff_account_id = False
                    writeoff_journal_id = False
                    amount = line.amount

                    ret_move = self.wh_and_reconcile(cr, uid, [ret.id], ret.invoice_id.id,
                            amount, acc_id, period_id, journal_id, writeoff_account_id,
                            period_id, writeoff_journal_id, context)

                    # make the retencion line point to that move
                    rl = {
                        'move_id': ret_move['move_id'],
                    }
                    #lines = [(op,id,values)] escribir en un one2many
                    lines = [(1, line.id, rl)]
                    self.write(cr, uid, [ret.id], {'concept_ids':lines})
                  
                    for line in ret.concept_ids:
                        for xml in line.xml_ids:
                            if xml.islr_xml_wh_doc.state!='done':
                                if xml.period_id.id != period_id:
                                    self.pool.get('islr.xml.wh.line').write(cr,uid,xml.id,{'period_id':period_id, 'islr_xml_wh_doc':None})
                            else:
                                raise osv.except_osv(_('Invalid action !'),_(" Imposible cambiar el periodo contable a una retencion que ya ha sido declarada"))
                            
#                    inv_obj.write(cr, uid, line.invoice_id.id, {'retention':True}, context=context)
        return True


    def wh_and_reconcile(self, cr, uid, ids, invoice_id, pay_amount, pay_account_id, period_id, pay_journal_id, writeoff_acc_id, writeoff_period_id, writeoff_journal_id,context=None, name=''):
        inv_obj = self.pool.get('account.invoice')
        ret = self.browse(cr, uid, ids)[0]
        if context is None:
            context = {}
        #TODO check if we can use different period for payment and the writeoff line
        #~ assert len(invoice_ids)==1, "Can only pay one invoice at a time"
        invoice = inv_obj.browse(cr, uid, invoice_id)
        src_account_id = invoice.account_id.id
        # Take the seq as name for move
        types = {'out_invoice': -1, 'in_invoice': 1, 'out_refund': 1, 'in_refund': -1}
        direction = types[invoice.type]
       
        date=ret.date_ret
            
        l1 = {
            'debit': direction * pay_amount>0 and direction * pay_amount,
            'credit': direction * pay_amount<0 and - direction * pay_amount,
            'account_id': src_account_id,
            'partner_id': invoice.partner_id.id,
            'ref':invoice.number,
            'date': date,
            'currency_id': False,
        }
        l2 = {
            'debit': direction * pay_amount<0 and - direction * pay_amount,
            'credit': direction * pay_amount>0 and direction * pay_amount,
            'account_id': pay_account_id,
            'partner_id': invoice.partner_id.id,
            'ref':invoice.number,
            'date': date,
            'currency_id': False, 
        }
        if not name:
            if invoice.type in ['in_invoice','in_refund']:
                name = 'COMP. RET. ISLR ' + ret.number + ' Doc. '+ (invoice.reference or '')
            else:
                name = 'COMP. RET. ISLR ' + ret.number + ' Doc. '+ (str(int(invoice.number)) or '')

        l1['name'] = name
        l2['name'] = name

        lines = [(0, 0, l1), (0, 0, l2)]
        move = {'ref': invoice.number, 'line_id': lines, 'journal_id': pay_journal_id, 'period_id': period_id, 'date': date}
        move_id = self.pool.get('account.move').create(cr, uid, move, context=context)

        self.pool.get('account.move').post(cr, uid, [move_id])

        line_ids = []
        total = 0.0
        line = self.pool.get('account.move.line')
        cr.execute('select id from account_move_line where move_id in ('+str(move_id)+','+str(invoice.move_id.id)+')')
        lines = line.browse(cr, uid, map(lambda x: x[0], cr.fetchall()) )
        for l in lines+invoice.payment_ids:
            if l.account_id.id==src_account_id:
                line_ids.append(l.id)
                total += (l.debit or 0.0) - (l.credit or 0.0)
        if (not round(total,int(config['price_accuracy']))) or writeoff_acc_id:
            self.pool.get('account.move.line').reconcile(cr, uid, line_ids, 'manual', writeoff_acc_id, writeoff_period_id, writeoff_journal_id, context)
        else:
            self.pool.get('account.move.line').reconcile_partial(cr, uid, line_ids, 'manual', context)

        # Update the stored value (fields.function), so we write to trigger recompute
        self.pool.get('account.invoice').write(cr, uid, invoice_id, {}, context=context)
        return {'move_id': move_id}

islr_wh_doc()


class account_invoice(osv.osv):
    _inherit = 'account.invoice'
    _columns = {
        'islr_wh_doc_id': fields.many2one('islr.wh.doc','Doc. de Retencion ISLR',readonly=True,help="Documento de Retencion de ISLR, generado a partir de esta factura"),
    }
    _defaults = {
        'islr_wh_doc_id': lambda *a: 0,
    }

    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default = default.copy()
        default.update({'islr_wh_doc_id':0 })

        return super(account_invoice, self).copy(cr, uid, id, default, context)
        
account_invoice()
        
        
class islr_wh_doc_invoices(osv.osv):
    _name = "islr.wh.doc.invoices"
    _columns= {
        'islr_wh_doc_id': fields.many2one('islr.wh.doc','Id del Documento', ondelete='cascade'),
        'invoice_id':fields.many2one('account.invoice','Invoice'),
    }
    _rec_rame = 'invoice_id'
islr_wh_doc_invoices()


class islr_wh_doc_line(osv.osv):
    _name = "islr.wh.doc.line"

    def _retention_rate(self, cr, uid, ids, name, args, context=None):
        res = {}
        for ret_line in self.browse(cr, uid, ids, context=context):
            if ret_line.invoice_id:
                pass
            else:
                res[ret_line.id] = 0.0
        return res

    _columns= {
        'name': fields.char('Descripcion', size=64, help="Descripcion de la linea del comprobante"),
        'invoice_id': fields.many2one('account.invoice', 'Factura', ondelete='set null', select=True, help="Factura a retener"),
        'amount':fields.float('Amount'),
        'islr_wh_doc_id': fields.many2one('islr.wh.doc','Comprobante', ondelete='cascade'),
        'concept_id': fields.many2one('islr.wh.concept','Concepto de Retencion'),
        'retencion_islr':fields.float('Retencion por 100'),
        'retention_rate': fields.function(_retention_rate, method=True, string='Retencion Por 100', type='float', help="Porcentaje de Retencion ha aplicar a la factura"),
        'move_id': fields.many2one('account.move', 'Movimiento Contable', readonly=True, help="Asiento Contable"),
        'islr_rates_id': fields.many2one('islr.rates','Tasas'),
        'xml_ids':fields.one2many('islr.xml.wh.line','islr_wh_doc_line_id','Lineas de Xml'),
    }

islr_wh_doc_line()






