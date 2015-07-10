# -*- encoding: utf-8 -*-
###############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (c) 2013 Vauxoo C.A. (http://openerp.com.ve/)
#    All Rights Reserved
###############################################################################
#    Credits:
#    Coded by:  Juan Marzquez (Tecvemar, c.a.) <jmarquez@tecvemar.com.ve>
#               Katherine Zaoral               <katherine.zaoral@vauxoo.com>
#    Planified by:
#                Juan Marquez                  <jmarquez@tecvemar.com.ve>
#                Humberto Arocha               <hbto@vauxoo.com>
#    Audited by: Humberto Arocha               <hbto@vauxoo.com>
###############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
###############################################################################

from openerp.osv import fields, osv


class customs_form_config(osv.osv):

    '''
    Stores common config parameters for form_86 data
    '''

    _name = 'customs.form.config'
    _description = ''
    _rec_name = "company_id"

    _columns = {
        'company_id': fields.many2one('res.company', 'Company', required=True,
                                      readonly=True, ondelete='restrict'),
        'journal_id': fields.many2one('account.journal', 'Journal',
                                      required=True, ondelete='restrict'),
    }

    _defaults = {
        'company_id': lambda self, cr, uid, c:
        self.pool.get('res.company')._company_default_get(
            cr, uid, 'customs.form.config', context=c),
    }

    _sql_constraints = [
        ('company_id_uniq', 'UNIQUE(company_id)',
         'The company must be unique!'),
    ]


class customs_facility(osv.osv):

    '''
    Stores a list with Venezuela's customs
    '''

    _name = 'customs.facility'
    _description = ''

    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []
        so_brw = self.browse(cr, uid, ids, context={})
        res = []
        for item in so_brw:
            res.append((item.id, '[%s] %s' % (item.code, item.name)))
        return res

    def name_search(self, cr, user, name='', args=None, operator='ilike',
                    context=None, limit=100):
        # Based on account.account.name_search...
        res = super(customs_facility, self).name_search(
            cr, user, name, args, operator, context, limit)
        if not res and name:
            ids = self.search(cr, user, [(
                'code', '=like', name + "%")] + args, limit=limit)
            if ids:
                res = self.name_get(cr, user, ids, context=context)
        return res

    _columns = {
        'code': fields.char('Code', size=16, required=True, readonly=False),
        'name': fields.char('Name', size=64, required=True, readonly=False),
    }

    _defaults = {
    }

    _sql_constraints = [
        ('code_uniq', 'UNIQUE(code)', 'The code must be unique!'),
    ]


class customs_duty(osv.osv):

    '''
    A list of the concepts for taxes in form_86
    '''

    _name = 'customs.duty'
    _description = ''
    _order = 'sequence'

    def name_get(self, cr, uid, ids, context=None):
        context = context or {}
        if not len(ids):
            return []
        res = []
        so_brw = self.browse(cr, uid, ids, context=context)
        for item in so_brw:
            res.append((item.id, '[%s] %s - %s' % (
                item.code, item.ref, item.name)))
        return res

    _columns = {
        'code': fields.char('Code', size=16, required=True, readonly=False),
        'name': fields.char('Name', size=64, required=True, readonly=False),
        'ref': fields.char('Ref', size=16, required=False, readonly=False),
        'sequence': fields.integer('Sequence'),
        'partner_id': fields.many2one('res.partner', 'Partner',
                                      change_default=True,
                                      ondelete='restrict'),
        'account_id': fields.many2one('account.account', 'Account to pay',
                                      domain="[('type','!=','view')]",
                                      ondelete='restrict',
                                      help="This account will be used for \
                                      expenses related to taxes"),
        'vat_detail': fields.boolean('Tax detail', help="Set true if this is \
        vat related tax"),
        'company_id': fields.many2one('res.company', 'Company', required=True,
                                      readonly=True, ondelete='restrict'),
    }

    _defaults = {
        'company_id': lambda self, cr, uid, c:
        self.pool.get('res.company')._company_default_get(
            cr, uid, 'customs.form.config', context=c),
        'vat_detail': False,
    }

    _sql_constraints = [
        ('code_uniq', 'UNIQUE(code,company_id)',
         'The code must be unique! (for this comany)'),
        ('sequence_uniq', 'UNIQUE(sequence,company_id)',
         'The sequence must be unique! (for this comany)'),
    ]
