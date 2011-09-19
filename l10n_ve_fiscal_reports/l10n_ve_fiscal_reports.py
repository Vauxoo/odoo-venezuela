# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010 Vauxoo C.A. (http://openerp.com.ve/) All Rights Reserved.
#                    Javier Duran <javier@vauxoo.com>
#                    Nhomar Hernandéz <nhomar@vauxoo.com>
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

'''
Fiscal Report For Venezuela
'''

from osv import osv
from osv import fields
from tools.translate import _
from tools import config
from tools.sql import drop_view_if_exists

class fiscal_reports_purchase(osv.osv):
    '''
    Modifying the object fiscal.reports.purchase
    '''
    _name = "fiscal.reports.purchase"
    _description = "Purchase by period"
    _auto = False
    _rec_name = 'ai_nro_ctrl'
    _order = 'ai_nro_ctrl asc'
    _columns = {
        'ai_date_document': fields.date('Date'),
        'ai_date_invoice': fields.date('Date'),
        'ar_date_document': fields.date('Date Account Retencion'),
        'rp_vat':fields.char('VAT Number', size=24, required=False, readonly=True),
        'rp_id':fields.many2one('res.partner', 'Partner Name', required=True),
        'ai_nro_ctrl':fields.char('Control No.', size=128, required=False, readonly=True),
        'ai_reference':fields.char('Invoice Number', size=128, required=False, readonly=True),
        'ai_amount_total': fields.float('Amount Total', digits=(16, int(config['price_accuracy']))),
        'ai_amount_untaxed': fields.float('Untaxed Amount', digits=(16, int(config['price_accuracy']))),
        'ai_amount_tax': fields.float('Tax Amount', digits=(16, int(config['price_accuracy']))),
        'ai_type':fields.char('Document Type', size=64, required=False, readonly=False),
        'rp_retention': fields.float('Whitholding Rate', digits=(16, int(config['price_accuracy']))),
        'ai_id':fields.many2one('account.invoice', 'Invoice Description', required=False),
        'ar_line_id':fields.many2one('account.retention.line', 'Account Retention', readonly=True),
        'ar_id':fields.many2one('account.retention', 'Account Retention', readonly=True),
    }
    def init(self, cr):
        '''
        Create or replace view fiscal_reports_purchase
        '''
        drop_view_if_exists(cr, 'fiscal_reports_purchase')
        cr.execute("""
            create or replace view fiscal_reports_purchase as (
                SELECT
                     ai."date_document" AS ai_date_document,
                     ai."date_invoice" AS ai_date_invoice,
                     rp."vat" AS rp_vat,
                     rp."id" AS rp_id,
                     ai."nro_ctrl" AS ai_nro_ctrl,
                     ai."reference" AS ai_reference,
                     ar."date_ret" AS ar_date_document,
                case when ai.type='in_refund'
                then
                    ai."amount_total"*(-1)
                else
                    ai."amount_total" 
                end as ai_amount_total,
                case when ai.type='in_refund'
                then
                    ai."amount_untaxed"*(-1)
                else
                    ai."amount_untaxed" 
                end as ai_amount_untaxed,
                case when ai.type='in_refund'
                then
                    ai."amount_tax"*(-1)
                else
                    ai."amount_tax" 
                end as ai_amount_tax,
                     ai."type" AS ai_type,
                     rp."retention" AS rp_retention,
                     ai."id" AS id,
                     ai."id" AS ai_id,
                     ar_line."id" AS ar_line_id,
                     ar_line."retention_id" AS ar_id
                FROM
                     "res_partner" rp INNER JOIN "account_invoice" ai ON rp."id" = ai."partner_id"
                     LEFT JOIN "account_retention_line" ar_line ON ar_line."invoice_id" = ai."id"
                     LEFT JOIN "account_retention" ar ON ar_line."retention_id" = ar."id"                                                     
                WHERE
                     (ai.type = 'in_refund'
                  OR ai.type = 'in_invoice')
                 AND (ai.state = 'open'
                  OR ai.state = 'paid'
                  OR ai.state = 'done')
                ORDER BY
                     ai_date_invoice ASC,
                     ar."number" ASC
                 )
        """)
fiscal_reports_purchase()  

class fiscal_reports_sale(osv.osv):
    '''
    Modifying the object fiscal.reports.sales
    '''
    _name = "fiscal.reports.sale"
    _description = "Sale by period"
    _auto = False
    _rec_name = 'ai_nro_ctrl'
    _columns = {
    'ai_date_document': fields.date('Date'),
    'ai_date_invoice': fields.date('Date'),
    'ar_date_document': fields.date('Date Account Retencion'),
    'rp_vat':fields.char('VAT Number', size=64, required=False, readonly=False),
    'rp_id':fields.many2one('res.partner', 'Partner Name', required=True),
    'ai_reference':fields.char('Invoice Number', size=64, required=False, readonly=False),
    'ai_nro_ctrl':fields.char('Control No.', size=64, required=False, readonly=False),
    'ai_amount_total': fields.float('Amount Total', digits=(16, int(config['price_accuracy']))),
    'ai_amount_untaxed': fields.float('Untaxed amount', digits=(16, int(config['price_accuracy']))),
    'ai_amount_tax': fields.float('Tax Amount', digits=(16, int(config['price_accuracy']))),
    'ai_type':fields.char('Type', size=64, required=False, readonly=False),
    'rp_retention': fields.float('Withholding', digits=(16, int(config['price_accuracy']))),
    'ai_id':fields.many2one('account.invoice', 'Invoice Description', required=False),
    'ar_line_id':fields.many2one('account.retention.line', 'Account Retention', readonly=True),
    'ar_id':fields.many2one('account.retention', 'Account Retention', readonly=True),
    }
    def init(self, cr):
        '''
        Create or replace view fiscal_reports_sale
        '''   
        drop_view_if_exists(cr, 'fiscal_reports_sale') 
        cr.execute("""
            create or replace view fiscal_reports_sale as (
                SELECT
                ai."date_document" AS ai_date_document,
                ai."date_invoice" AS ai_date_invoice,
                rp."vat" AS rp_vat,
                rp."id" AS rp_id,
                ai."number" AS ai_reference,
                ai."nro_ctrl" AS ai_nro_ctrl,
                ar."date_ret" AS ar_date_document,
                case when ai.type='out_refund'
                then
                    ai."amount_total"*(-1)
                else
                    ai."amount_total" 
                end as ai_amount_total,
                case when ai.type='out_refund'
                then
                    ai."amount_untaxed"*(-1)
                else
                    ai."amount_untaxed" 
                end as ai_amount_untaxed,
                case when ai.type='out_refund'
                then
                    ai."amount_tax"*(-1)
                else
                    ai."amount_tax" 
                end as ai_amount_tax,
                ai."type" AS ai_type,
                rp."retention" AS rp_retention,
                ai."id" AS id,
                ai."id" AS ai_id,
                ar_line."id" AS ar_line_id,
                ar_line."retention_id" AS ar_id
                FROM
                 "res_partner" rp INNER JOIN "account_invoice" ai ON rp."id" = ai."partner_id"
                 LEFT JOIN "account_retention_line" ar_line ON ar_line."invoice_id" = ai."id"
                 LEFT JOIN "account_retention" ar ON ar_line."retention_id" = ar."id"
                WHERE
                (ai.type = 'out_refund'
                OR ai.type = 'out_invoice')
                AND (ai.state = 'open'
                OR ai.state = 'paid'
                OR ai.state = 'done')
                ORDER BY
                ai_date_invoice ASC,
                ai."nro_ctrl" ASC
                )
        """)
fiscal_reports_sale()
class fiscal_reports_whp(osv.osv):
    '''
    Modifying the object fiscal.reports.whp
    '''
    _name = "fiscal.reports.whp"
    _description = "Purchase by period"
    _auto = False
    _rec_name = 'ai_nro_ctrl'
    _columns = {
    'ar_date_ret': fields.date('Date ret.', readonly=True),
    'rp_vat':fields.char('Vat Number', size=64, readonly=True),
    'rp_id':fields.many2one('res.partner', 'Partner', readonly=True),
    'ar_number':fields.char('Retention Number', size=64, required=False, readonly=True),
    'ai_reference':fields.char('Invoice Number', size=64, required=False, readonly=True),
    'ai_amount_total': fields.float('Amount Total', digits=(16, int(config['price_accuracy']))),
    'ai_amount_untaxed': fields.float('Amount Untaxed', digits=(16, int(config['price_accuracy'])), readonly=True),
    'ai_amount_tax': fields.float('Amount tax', digits=(16, int(config['price_accuracy'])), readonly=True),
    'ar_line_id':fields.many2one('account.retention.line', 'Account Retention', readonly=True),
    'ai_id':fields.many2one('account.invoice', 'Account Invoice', readonly=True),
    'ar_id':fields.many2one('account.retention', 'Account Retention', readonly=True),
    }
    def init(self, cr):
        '''
        Create or replace view fiscal_reports_whp
        '''    
        drop_view_if_exists(cr, 'fiscal_reports_whp')
        cr.execute("""
            create or replace view fiscal_reports_whp as (
                SELECT
                     ar."date_ret" AS ar_date_ret,
                     rp."vat" AS rp_vat,
                     ar."number" AS ar_number,
                     ai."reference" AS ai_reference,
                    case when ai.type='in_refund'
                    then
                        ai."amount_total"*(-1)
                    else
                        ai."amount_total" 
                    end as ai_amount_total,
                    case when ai.type='in_refund'
                    then
                        ai."amount_tax"*(-1)
                    else
                        ai."amount_tax" 
                    end as ai_amount_tax,
                    case when ai.type='in_refund'
                    then
                        ai."amount_untaxed"*(-1)
                    else
                        ai."amount_untaxed" 
                    end as ai_amount_untaxed,
                     ar_line."id" AS id,
                     ar_line."id" AS ar_line_id,
                     ar."id" AS ar_id,
                     rp."id" AS rp_id,
                     ai."id" AS ai_id
                FROM
                     "account_retention_line" ar_line INNER JOIN "account_retention" ar ON ar_line."retention_id" = ar."id"
                     INNER JOIN "res_partner" rp ON ar."partner_id" = rp."id"
                     INNER JOIN "account_invoice" ai ON ar_line."invoice_id" = ai."id"
                WHERE
                    ar."state" = 'done'
                AND
                    (ai."type" = 'in_invoice' OR ai."type" = 'in_refund')
                    )
        """)
fiscal_reports_whp()

class fiscal_reports_whs(osv.osv):
    '''
    Modifying the object fiscal.reports.whs
    '''
    _name = "fiscal.reports.whs"
    _description = "Sale by period"
    _auto = False
    _rec_name = 'ai_nro_ctrl'
    _columns = {
    'ar_date_ret': fields.date('Date'),
    'ai_date_inv': fields.date('Date Invoice'),
    'rp_vat':fields.char('Vat Number', size=64, readonly=True),
    'rp_id':fields.many2one('res.partner', 'Partner Name', readonly=True),
    'ar_number':fields.char('WH Number', size=64, readonly=True),
    'ai_number':fields.char('Invoice Number', size=64, readonly=True),
    'ai_id':fields.many2one('account.invoice', 'Invoice', required=False, readonly=True),
    'ai_amount_total': fields.float('Invoice Total', digits=(16, int(config['price_accuracy'])), readonly=True),
    'ai_amount_untaxed': fields.float('Amount Untaxed', digits=(16, int(config['price_accuracy'])), readonly=True),
    'ar_line_id':fields.many2one('account.retention.line', 'Account Retention', readonly=True),
    'ai_amount_tax': fields.float('Amount Tax', digits=(16, int(config['price_accuracy'])), readonly=True),
    'ar_id':fields.many2one('account.retention', 'Retention', required=False, readonly=True),
    'ai_reference':fields.char('Invoice Number', size=64, required=False, readonly=True),
    }
    def init(self, cr):
        '''
        Create or replace view fiscal_reports_whs
        '''    
        drop_view_if_exists(cr, 'fiscal_reports_whs')
        cr.execute("""
            create or replace view fiscal_reports_whs as (
                SELECT
                     ar."date_ret" AS ar_date_ret,
                     rp."vat" AS rp_vat,
                     ar."number" AS ar_number,
                     ai."number" AS ai_reference,
                     ai."number" AS ai_number,
                     ai."date_invoice" AS ai_date_inv,
                    case when ai.type='out_refund'
                    then
                        ai."amount_total"*(-1)
                    else
                        ai."amount_total" 
                    end as ai_amount_total,
                    case when ai.type='out_refund'
                    then
                        ai."amount_tax"*(-1)
                    else
                        ai."amount_tax" 
                    end as ai_amount_tax,
                    case when ai.type='out_refund'
                    then
                        ai."amount_untaxed"*(-1)
                    else
                        ai."amount_untaxed" 
                    end as ai_amount_untaxed,
                     ar_line."id" AS id,
                     ar_line."id" AS ar_line_id,
                     ar."id" AS ar_id,
                     rp."id" AS rp_id,
                     ai."id" AS ai_id
                FROM
                     "account_retention_line" ar_line INNER JOIN "account_retention" ar ON ar_line."retention_id" = ar."id"
                     INNER JOIN "res_partner" rp ON ar."partner_id" = rp."id"
                     INNER JOIN "account_invoice" ai ON ar_line."invoice_id" = ai."id"
                WHERE
                    ar."state" = 'done'
                AND
                    (ai."type" = 'out_invoice' OR ai."type" = 'out_refund')
                ORDER BY ar_date_ret
                )
        """)
fiscal_reports_whs()
