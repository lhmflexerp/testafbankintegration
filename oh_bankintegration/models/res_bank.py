# -*- coding: utf-8 -*-
from odoo import fields, models, _, api
from odoo.exceptions import UserError, ValidationError
from dateutil.parser import parse
import logging
_logger = logging.getLogger(__name__)


class ResPartnerBank(models.Model):
    _name = 'res.partner.bank'
    _inherit = ["res.partner.bank"]

    bankintegration_acc_number = fields.Char(
        'Domestic account number', help="For bankintegration insert domestic account number, if IBAN number is used in the Account Number field")
