# -*- encoding: utf-8 -*-
##############################################################################
#    Company: Tecvemar, c.a.
#    Author: Juan V. Márquez L.
#    Creation Date: 26/11/2012
#    Version: 0.0.0.0
#
#    Description: Gets a CSV file from data collector and import it to
#                 sale order
#
##############################################################################

from openerp.osv import fields, osv
from openerp.tools.translate import _


class islr_wh_change_concept(osv.osv_memory):

    _name = 'islr.wh.change.concept'
    _columns = {
        'sure': fields.boolean('Are you Sure?'),
        'new_concept_id': fields.many2one(
            'islr.wh.concept', 'New Income Wh Concept', required=True),
    }

    def income_wh_change(self, cr, uid, ids, context=None):
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        iwcc_brw = self.browse(cr, uid, ids[0], context=context)
        if not iwcc_brw.sure:
            raise osv.except_osv(
                _('Warning!'), _('You have to tick the "Are you Sure" Check'))
        ail_obj = self.pool.get('account.invoice.line')
        ail_brw = ail_obj.browse(cr, uid, context.get('active_id'), context={})
        inv_brw = ail_brw.invoice_id
        if inv_brw.state != 'open':
            raise osv.except_osv(
                _('Warning!'),
                _('This Button is meant to be used with Invoices in'
                  ' "Open State"'))

        ail_brw.write({'concept_id': iwcc_brw.new_concept_id.id})
        inv_brw.refresh()

        if inv_brw.islr_wh_doc_id:
            if inv_brw.islr_wh_doc_id.state == 'draft':
                inv_brw.islr_wh_doc_id.compute_amount_wh()
            else:
                raise osv.except_osv(
                    _('Warning!'),
                    _('Income Withholding from this invoice must be cancelled'
                      ' prior to change concept'))
        else:
            if (inv_brw.check_invoice_type() and
                    inv_brw.check_withholdable_concept()):
                inv_brw._create_islr_wh_doc()

        return {'type': 'ir.actions.act_window_close'}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
