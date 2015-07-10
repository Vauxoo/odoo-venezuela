# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    author.name@company.com
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp.osv import fields, osv


class wizard_url_seniat(osv.osv_memory):

    def _get_url(self, cr, uid, ids, context=None):
        """ Get seniat web page
        """
        url = self.pool.get('seniat.url')
        url_ids = url.search(cr, uid, [])
        if len(url_ids) > 1:
            url.unlink(cr, uid, url_ids[1:])
        url_obj = url.browse(cr, uid, url_ids, context=None)[0]
        return url_obj

    def _get_url1(self, cr, uid, ids, context=None):
        url_obj = self._get_url(cr, uid, ids, context)
        return url_obj.name

    def _get_url2(self, cr, uid, ids, context=None):
        url_obj = self._get_url(cr, uid, ids, context)
        return url_obj.url_seniat

    def _get_url3(self, cr, uid, ids, context=None):
        url_obj = self._get_url(cr, uid, ids, context)
        return url_obj.url_seniat2

    def update_url(self, cr, uid, ids, context=None):
        data = self.pool.get('wizard.seniat.url').read(cr, uid, ids)[0]
        url_obj = self._get_url(cr, uid, ids, context)
        url_obj.write(
            {'name': data['url1'],
             'url_seniat': data['url2'],
             'url_seniat2': data['url3']})
        return {}

    _name = "wizard.seniat.url"
    _columns = {
        'url1': fields.char(
            'URL1', 255, required=True, readonly=False, help='In this field'
            ' enter the URL from Seniat for search the fiscal information from'
            ' partner'),
        'url2': fields.char(
            'URL2', 255, required=True, readonly=False, help='In this field'
            ' enter the URL from Seniat for search the retention rate from'
            ' partner (RIF)'),
        'url3': fields.char(
            'URL3', 255, required=True, readonly=False, help='In this field'
            ' enter the URL from Seniat for search the retention rate from'
            ' partner (CI or Passport)'),
    }
    _defaults = {
        'url1': _get_url1,
        'url2': _get_url2,
        'url3': _get_url3,
    }
wizard_url_seniat()
