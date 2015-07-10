# ~ # -*- coding: utf-8 -*-
from openerp.report import report_sxw


class wh_src_report(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):

        super(wh_src_report, self).__init__(cr, uid, name, context)
        self.localcontext.update(
            {
                'get_empresa': self.get_empresa,

            })
        self.context = context

    def get_empresa(self, partner_id):
        """ Get information company
        """
        partner_id = isinstance(partner_id, (int, long)) and [partner_id] or \
            partner_id
        rp_obj = self.pool.get('res.partner')
        row = rp_obj.browse(self.cr, self.uid, partner_id[0])
        row = rp_obj._find_accounting_partner(row)
        return {
            'street': row.street,
            'phone': row.phone,
            'fax': row.fax,
            'email': row.email,
            'city': row.city,
            'name': row.name,
            'country': row.country_id.name,
        }

report_sxw.report_sxw(
    'report.wh.src.report',
    'account.wh.src',
    parser=wh_src_report,
    # header= 'internal',
    rml='l10n_ve_withholding_src/report/wh_src_report.rml'
)
