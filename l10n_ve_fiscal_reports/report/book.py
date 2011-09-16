# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010 Netquatro C.A. (http://openerp.netquatro.com/) All Rights Reserved.
#                    Javier Duran <javier.duran@netquatro.com>
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

'''
Fiscal Report For Venezuela
'''

import time
from report import report_sxw
from osv import osv
import pooler

class pur_sal_book(report_sxw.rml_parse):
    '''
    Book generates purchase and sale
    '''

    def __init__(self, cr, uid, name, context):
        '''
        Reference to the current instance
        '''
        super(pur_sal_book, self).__init__(cr, uid, name, context)    
        self.localcontext.update({
            'time': time,
            'get_data':self._get_data,
            'get_partner_addr': self._get_partner_addr,
            'get_p_country': self._get_p_country,
            'get_rif': self._get_rif,
            'get_month':self._get_month,
            'get_doc':self._get_doc,
            'get_ret':self._get_ret,
            'get_data_adjustment': self._get_data_adjustment,
            'validation': self._validation,
            'get_data_wh': self._get_data_wh,
            'get_amount_withheld': self._get_amount_withheld,
            'get_date_wh': self._get_date_wh,
            'get_v_sdcf': self._get_v_sdcf,
            'get_tax_line': self._get_tax_line,
            'get_total_wh': self._get_total_wh,
            'get_total_iva': self._get_total_iva,
            'get_amount_untaxed_tax': self._get_amount_untaxed_tax,
            'get_taxes': self._get_taxes,
        })

    def _get_book_type(self,form):
        book_type=None
        book_type='fiscal.reports.sale'
        if form['type']=='purchase':
            book_type='fiscal.reports.purchase'
        
        return book_type

    def _get_book_type_wh(self,form):
        book_type=None
        book_type='fiscal.reports.whs'
        if form['type']=='purchase':
            book_type='fiscal.reports.whp'
        return book_type

    def _validation(self,form):
        type_doc = 'sale'
        if form['type']=='purchase':
            type_doc = 'purchase'
        period_obj=self.pool.get('account.period')
        adjust_obj = self.pool.get('adjustment.book')
        period_ids = period_obj.search(self.cr,self.uid,[('date_start','<=',form['date_start']),('date_stop','>=',form['date_end'])])
        if len(period_ids)<=0:
            return False
        fr_ids = adjust_obj.search(self.cr,self.uid,[('period_id','in',period_ids),('type','=',type_doc)])
        if len(fr_ids)<=0:
            return False
        return True
        
    def _get_data_adjustment(self,form):

        type_doc = 'sale'
        if form['type']=='purchase':
            type_doc = 'purchase'
        adjust_obj = self.pool.get('adjustment.book')
        adjust_line_obj = self.pool.get('adjustment.book.line')
        period_obj=self.pool.get('account.period')
        data=[]
        data_line=[]
        period_ids = period_obj.search(self.cr,self.uid,[('date_start','<=',form['date_start']),('date_stop','>=',form['date_end'])])
        
        if len(period_ids)>0:
            fr_ids = adjust_obj.search(self.cr,self.uid,[('period_id', 'in',period_ids),('type','=',type_doc)])
            if len(fr_ids)>0:
                adj_ids = adjust_line_obj.search(self.cr,self.uid,[('adjustment_id','=',fr_ids[0])],order='date_admin')
                data = adjust_obj.browse(self.cr,self.uid, fr_ids)
                data_line = adjust_line_obj.browse(self.cr,self.uid, adj_ids)
        return (data,data_line)

    def _get_date_wh(self,form, l):
        if l.ar_date_document> form['date_end']:
            return False
        return True

    def _get_v_sdcf(self,l):
        amount = 0.0
        if not l:
            return 0.0
        for tax in l.ai_id.tax_line:
            name=tax.name
            if name.find('SDCF')>=0:
                amount = tax.base
                if l.ai_id.type in ['in_refund', 'out_refund']:
                    amount = amount * (-1)
        return (amount)

    def _get_tax_line(self,s):
        name = s.name
        cont = 0
        if name.find('SDCF')>=0:
            if cont==0:
                return 0
        else:
            cont = cont + 1
        return s.base_amount
    
    def _get_data(self,form):
        data=[]
        orden='ai_nro_ctrl'
        
        book_type = self._get_book_type(form)
        fr_obj = self.pool.get(book_type)
        
        if book_type=='fiscal.reports.purchase':
            orden='ai_date_document'
        fr_ids = fr_obj.search(self.cr,self.uid,[('ai_date_invoice', '<=', form['date_end']), ('ai_date_invoice', '>=', form['date_start'])], order=orden)
        
        if len(fr_ids)<=0:
            return False
        data = fr_obj.browse(self.cr,self.uid, fr_ids)
        return data

    def _get_data_wh(self,form):
        data=[]
        d1=form['date_start']
        d2=form['date_end']
        fr_obj = self.pool.get('fiscal.reports.whs')
        fr_ids = fr_obj.search(self.cr,self.uid,[('ar_date_ret', '<=', d2), ('ar_date_ret', '>=',d1),('ai_date_inv','<=',d1)], order='ar_date_ret')
        data = fr_obj.browse(self.cr,self.uid, fr_ids)
        return data

    def _get_total_wh(self,form):
        total=0
        data=[]
        book_type= self._get_book_type_wh(form)
        fr_obj = self.pool.get(book_type)
        
        fr_ids = fr_obj.search(self.cr,self.uid,[('ar_date_ret', '<=', form['date_end']), ('ar_date_ret', '>=', form['date_start'])])
        data = fr_obj.browse(self.cr,self.uid, fr_ids)
        
        for wh in data:
            if wh.ai_id.type in ['in_refund', 'out_refund']:
                total+= wh.ar_line_id.amount_tax_ret * (-1)
            else:
                total+= wh.ar_line_id.amount_tax_ret
        return total

    def _get_ret(self,form,ret_id=None):
        '''
            Ensure that Withholding date is inside period specified on form.
        '''
        d1=form['date_start']
        d2=form['date_end']
        if form['type']=='purchase':
            if ret_id:
                ret_obj = self.pool.get('account.retention')
                rets = ret_obj.browse(self.cr,self.uid,[ret_id])
                return rets[0].number
        if ret_id:
            ret_obj = self.pool.get('account.retention')
            rets = ret_obj.browse(self.cr,self.uid,[ret_id])
            if rets:
                if time.strptime(rets[0].date, '%Y-%m-%d') >= time.strptime(d1, '%Y-%m-%d') \
                and time.strptime(rets[0].date, '%Y-%m-%d') <=  time.strptime(d2, '%Y-%m-%d'):
                    return rets[0].number
                else:
                    return False
            else:
                return False
        else:
            return False

    def _get_amount_withheld(self,wh_line_id):
        wh_obj = self.pool.get('account.retention.line')
        data = wh_obj.browse(self.cr,self.uid, [wh_line_id])[0]
        return data.amount_tax_ret

    def _get_partner_addr(self, idp=None):
        '''
        Obtains the address of partner
        '''
        if not idp:
            return []

        addr_obj = self.pool.get('res.partner.address')
        addr_inv = 'NO HAY DIRECCION FISCAL DEFINIDA'
        addr_ids = addr_obj.search(self.cr,self.uid,[('partner_id','=',idp), ('type','=','invoice')])
        if addr_ids:
            addr = addr_obj.browse(self.cr,self.uid, addr_ids[0])
            addr_inv = (addr.street or '')+' '+(addr.street2 or '')+' '+(addr.zip or '')+ ' '+(addr.city or '')+ ' '+ (addr.country_id and addr.country_id.name or '')+ ', TELF.:'+(addr.phone or '')
        return addr_inv
    
    def _get_p_country(self, idp=None):
        '''
        Obtains the address of partner
        '''
        if not idp:
            return []

        addr_obj = self.pool.get('res.partner.address')
        a_id = 1000
        a_ids = addr_obj.search(self.cr,self.uid,[('partner_id','=',idp), ('type','=','invoice')])
        if a_ids:
            a = addr_obj.browse(self.cr,self.uid, a_ids[0])
            a_id = a.country_id.id
        return a_id 

    def _get_doc(self, inv_id=None):
        '''
        Get String Document Type
        '''
        inv_obj = self.pool.get('account.invoice')
        inv_ids = inv_obj.search(self.cr,self.uid,[('id', '=', inv_id)])
        inv = inv_obj.browse(self.cr,self.uid, inv_ids)[0]        
        doc_type = ''
        if (inv.type=="in_invoice" or inv.type=="out_invoice") and inv.parent_id:
            doc_type = "ND"
        elif (inv.type=="in_invoice" or inv.type=="in_refund") and inv.expedient:
            doc_type="E"
        elif inv.type=='in_refund' or inv.type=='out_refund':
            doc_type = "NC"
        elif inv.type=="in_invoice" or inv.type=="out_invoice":
            doc_type = "F"
        return doc_type

    def _get_rif(self, vat=''):
        '''
        Get R.I.F.
        '''
        if not vat:
            return []
        return vat[2:].replace(' ', '')

    def _get_month(self, form):
        '''
        return year and month
        '''
        months=["Enero","Febrero","Marzo","Abril","Mayo","Junio","Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"]
        res = ['',0]
        res[0] = months[time.strptime(form['date_start'],"%Y-%m-%d")[1]-1]
        res[1] = time.strptime(form['date_start'],"%Y-%m-%d")[0]
        return res

    def _get_total_iva(self,form):
        '''
        Return Amount Total of each invoice at Withholding Vat
        '''
        book_type= self._get_book_type(form)
        
        sql =   ''' select sum(ai_amount_total) as total 
                    from %s 
                    where ai_date_invoice>= '%s' and ai_date_invoice<='%s' 
                ''' % (book_type.replace('.','_'),form['date_start'],form['date_end'])
        self.cr.execute(sql)
        
        res = self.cr.dictfetchone()
        return res['total']

    def _get_amount_untaxed_tax(self,form,percent,nationality=''):
        '''
        Return Amount Untaxed and Amount Tax, accorded percent of withholding vat
        '''
        amount_untaxed=0.0
        amount_tax=0.0

        book_type=self._get_book_type(form)
    
        fr_obj = self.pool.get(book_type)
        user_obj = self.pool.get('res.users')
        
        user_ids = user_obj.search(self.cr,self.uid,[('id', '=', self.uid)])
        fr_ids = fr_obj.search(self.cr,self.uid,[('ai_date_invoice', '<=', form['date_end']), ('ai_date_invoice', '>=', form['date_start'])])

        user=user_obj.browse(self.cr,self.uid, [self.uid])
        
        for d in fr_obj.browse(self.cr,self.uid, fr_ids):
            for tax in d.ai_id.tax_line:
                
                if percent in tax.name:
                    if nationality=='nacional':
                        if self._get_p_country(user[0].company_id.partner_id.id)==self._get_p_country(d.ai_id.partner_id.id):
                            amount_untaxed+= self._get_amount_untaxed_tax2(d.ai_id.type,tax)[0]
                            amount_tax+= self._get_amount_untaxed_tax2(d.ai_id.type,tax)[1]
                    else:
                        if self._get_p_country(user[0].company_id.partner_id.id)!=self._get_p_country(d.ai_id.partner_id.id):
                            amount_untaxed+= self._get_amount_untaxed_tax2(d.ai_id.type,tax)[0]
                            amount_tax+= self._get_amount_untaxed_tax2(d.ai_id.type,tax)[1]

        return (amount_untaxed,amount_tax)


    def _get_amount_untaxed_tax2(self,type,tax):
        amount_untaxed=0.0
        amount_tax=0.0
        if type in ['in_refund', 'out_refund']:
            amount_untaxed= tax.base * (-1)
            amount_tax= tax.amount * (-1)
        else:
            amount_untaxed= tax.base
            amount_tax= tax.amount
        return [amount_untaxed,amount_tax]

    def _get_taxes(self,l):
        
        tax_obj = self.pool.get('account.invoice.tax')
        tax_ids = tax_obj.search(self.cr,self.uid,[('invoice_id', '=', l.ai_id.id)])
        
        tam = len(tax_ids)
        data = tax_obj.browse(self.cr,self.uid, tax_ids)
        
        for tax in data:
            if 'SDCF' in tax.name and tam>=2:
                tax_ids.remove(tax.id)
        
        data = tax_obj.browse(self.cr,self.uid, tax_ids)
        
        if len(data)<=0:
            return False
        return data


report_sxw.report_sxw(
    'report.fiscal.reports.purchase.purchase_seniat',
    'fiscal.reports.purchase',
    'addons/l10n_ve_fiscal_reports/report/book_seniat.rml',
    parser=pur_sal_book,
    header=False
)      
