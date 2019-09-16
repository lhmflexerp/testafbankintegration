# -*- coding: utf-8 -*-

import time
import datetime
from dateutil.relativedelta import relativedelta
import ast
import odoo
from odoo import SUPERUSER_ID
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # api_key = fields.Char(string=_('API key'), help="Enter API key here")
    payment_margin = fields.Integer(
        string=_('Payment Margin'), help="Payment Margin", default=0)
    autopay = fields.Boolean(string=_('Default auto pay'), default=False)
    set_validate_payment = fields.Boolean(
        string=_('Set for payment after validate?'), default=False)
    payment_journal = fields.Many2one(
        'account.journal', string='Payment journal', domain=[('type', '=', 'bank')])
    multiple_payment_type = fields.Selection([(1, 'Pay each separately'), (2, 'Pay national and international collected in one single payment'), (
        3, 'Pay only international collected in one single payment')], string='If multiple payments to same customer on one day', default=1)
    erp_provider = fields.Char(
        string='ERP Provider', help="Please enter ERP Provider name.")
    bi_api_key = fields.Char(
        string='API Key', help="Please enter API Key.")
    use_note_msg = fields.Boolean(
        string=_('Use not as label in denish?'), default=False)

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        get_param = self.env['ir.config_parameter'].sudo().get_param
        payment_journal = get_param('payment_journal')
        erp_provider = 'OdooHouse'
        api_key = 'a5d07ba8-ab89-4003-bd3b-30113ea277fb'
        set_validate_payment = get_param('set_validate_payment')
        use_note_msg = get_param('use_note_msg')
        if isinstance(get_param('set_validate_payment'), str):
            set_validate_payment = ast.literal_eval(
                get_param('set_validate_payment'))
        if isinstance(get_param('use_note_msg'), str):
            use_note_msg = ast.literal_eval(
                get_param('use_note_msg'))
        res.update(
            payment_margin=int(get_param('payment_margin')),
            autopay=False if get_param('autopay') == 'False' else True,
            payment_journal=int(
                payment_journal) if payment_journal != '0' else 0,
            multiple_payment_type=1,
            erp_provider=get_param('erp_provider') if get_param(
                'erp_provider') else erp_provider,
            bi_api_key=get_param('bi_api_key') if get_param(
                'bi_api_key') else api_key,
            set_validate_payment=set_validate_payment,
            use_note_msg=use_note_msg,
        )
        return res

    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        set_param = self.env['ir.config_parameter'].sudo().set_param
        # we store the repr of the values, since the value of the parameter is
        # a required string
        try:
            set_param('payment_margin', repr(self.payment_margin))
            set_param('autopay', repr(self.autopay))
            set_param('payment_journal', repr(
                self.payment_journal.id if self.payment_journal else 0))
            set_param('erp_provider', self.erp_provider)
            set_param('bi_api_key', self.bi_api_key)
            set_param('set_validate_payment', repr(self.set_validate_payment))
            set_param('use_note_msg', repr(self.use_note_msg))
        except Exception as e:
            print(str(e))
