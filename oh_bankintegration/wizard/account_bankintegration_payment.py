# -*- coding: utf-8 -*-
from odoo import models, api, _
from odoo.exceptions import UserError


class AccountBankintegrationPayment(models.TransientModel):
    """
    This wizard will make payment for selected invoices
    """

    _name = "account.bankintegration.payment"
    _description = "Bankintegration paymnet for selected invoices"

    @api.multi
    def make_bankintegration_payment(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []
        customer_payment = False
        invoice_ids = []
        invoice_model = self.env['account.invoice']
        for record in invoice_model.browse(active_ids):
            if record.type == 'out_invoice':
                customer_payment = True
                break
            elif record.payment_status in ['created', 'pending', 'accepted', 'success', 'rejected', 'failed', 'not_found']:
                raise UserError(_("One of the selected invoice is already under payment processing/processed status."))
                break
            else:
                invoice_ids.append(record.id)
            if record.payment_status and record.payment_status not in ['open']:
                raise UserError(_("Selected invoice(s) cannot be paid as they are not in 'Open' status."))
            # Write code here to make automatic payment
        if customer_payment:
            raise UserError(_("Access Denied."))
        
        if invoice_ids:
            invoice_model.bankintegration_schedule_payment(invoice_ids)

        return {'type': 'ir.actions.act_window_close'}