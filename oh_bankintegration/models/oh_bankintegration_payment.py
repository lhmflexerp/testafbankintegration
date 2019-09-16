# -*- coding: utf-8 -*-
from datetime import datetime
import random
from odoo import fields, api, models, _


class BankIntegrationRequest(models.Model):
    _name = "bank.integration.request"
    _model = "bank.integration.request"
    _description = "Bank Integration Request Status"

    request_id = fields.Char(string="Request id")
    request_status = fields.Selection([
        ('created', 'Created'),
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('success', 'Success'),
        ('rejected', 'Rejected'),
        ('failed', 'Failed'),
        ('not_found', 'Not Found'),
        ('warning', 'Warning'),
        ('canceling', 'Canceling'),
        ('invalid_signature', 'Invalid Signature'),
    ], string='Request status', index=True, readonly=True, default='created')
    request_datetime = fields.Datetime(string='Request datetime', index=True,
                                       help="API Request date")
    invoice_id = fields.Many2one(
        'account.invoice', string='Payment Invoice', domain=[('type', '=', 'in_invoice')])
    vendor_account = fields.Many2one(
        'res.partner.bank', string="Vendor Bank Account", ondelete='restrict', copy=False)
    bank_account = fields.Many2one(
        'res.partner.bank', string="Bank Account", ondelete='restrict', copy=False)
    fik_number = fields.Char(string="FIK Number", readonly=True)
    response_text = fields.Char(string="Response text")

    @api.model
    def generateReqId(self):
        request_id = str(random.randint(100000, 1000000))
        request_obj = self.search([('request_id', '=', request_id)])
        while request_obj:
            self.generateReqId()
        return request_id

    @api.model
    def create(self, vals):
        if not vals.get('request_id'):
            vals['request_id'] = self.generateReqId()

        request_obj = super(BankIntegrationRequest, self).create(vals)
        return request_obj

    @api.multi
    def bankintegration_multi_payments(self, invoice_ids):
        invoice_model = self.env['account.invoice']
        if invoice_ids:
            invoice_details = invoice_model.browse(invoice_ids)
            # Write code to make payments using REST API
