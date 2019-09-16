# -*- coding: utf-8 -*-
import sys
import base64
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.addons.base.models.res_bank import sanitize_account_number
from dateutil.parser import parse
import logging
import re
from decimal import Decimal
import csv
from io import StringIO
import datetime
_logger = logging.getLogger(__name__)


class AccountBankStatementImport(models.TransientModel):
    _name = 'account.bank.statement.import'
    _inherit = "account.bank.statement.import"

    # Function to if two float values are same or not
    def isClose(self, a, b, rel_tol=1e-09, abs_tol=0.0):
        return abs(a - b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)

    def _check_journal_bank_account(self, journal, account_number):
        if journal.bank_account_id.bankintegration_acc_number == account_number:
            return True
        return journal.bank_account_id.sanitized_acc_number == account_number

    def _find_additional_data(self, currency_code, account_number):
        """ Look for a res.currency and account.journal using values extracted from the
            statement and make sure it's consistent.
        """
        company_currency = self.env.user.company_id.currency_id
        journal_obj = self.env['account.journal']
        currency = None
        sanitized_account_number = sanitize_account_number(account_number)

        if currency_code:
            currency = self.env['res.currency'].search(
                [('name', '=ilike', currency_code)], limit=1)
            if not currency:
                raise UserError(
                    _("No currency found matching '%s'.") % currency_code)
            if currency == company_currency:
                currency = False

        journal = journal_obj.browse(self.env.context.get('journal_id', []))
        if account_number:
            # No bank account on the journal : create one from the account
            # number of the statement
            if journal and not journal.bank_account_id:
                journal.set_bank_account(account_number)
            # No journal passed to the wizard : try to find one using the
            # account number of the statement
            elif not journal:
                journal = journal_obj.search(
                    [('bank_account_id.bankintegration_acc_number', '=', sanitized_account_number)])
                if not journal:
                    journal = journal_obj.search(
                        [('bank_account_id.sanitized_acc_number', '=', sanitized_account_number)])
            # Already a bank account on the journal : check it's the same as on
            # the statement
            else:
                if not self._check_journal_bank_account(journal, sanitized_account_number):
                    raise UserError(_('The account of this statement (%s) is not the same as the journal (%s).') % (
                        account_number, journal.bank_account_id.acc_number))

        # If importing into an existing journal, its currency must be the same
        # as the bank statement
        if journal:
            journal_currency = journal.currency_id
            if currency is None:
                currency = journal_currency
            if currency and currency != journal_currency:
                statement_cur_code = not currency and company_currency.name or currency.name
                journal_cur_code = not journal_currency and company_currency.name or journal_currency.name
                raise UserError(_('The currency of the bank statement (%s) is not the same as the currency of the journal (%s).') % (
                    statement_cur_code, journal_cur_code))

        # If we couldn't find / can't create a journal, everything is lost
        if not journal and not account_number:
            raise UserError(
                _('Cannot find in which journal import this statement. Please manually select a journal.'))

        return currency, journal

    @api.multi
    def bankintegration_import_statements(self, currency_code, account_number, stmts_vals):
        """ Process the statements captured using bankintegration API. """
        # self.ensure_one()
        # Check raw data
        self._check_parsed_data(stmts_vals)
        # Try to find the currency and journal in odoo
        currency, journal = self._find_additional_data(
            currency_code, account_number)
        # If no journal found, ask the user about creating one
        if not journal:
            # The active_id is passed in context so the wizard can call
            # import_file again once the journal is created
            return self.with_context(active_id=self.ids[0])._journal_creation_wizard(currency, account_number)
        if not journal.default_debit_account_id or not journal.default_credit_account_id:
            raise UserError(
                _('You have to set a Default Debit Account and a Default Credit Account for the journal: %s') % (journal.name,))
        # Prepare statement data to be used for bank statements creation
        stmts_vals = self._complete_stmts_vals(
            stmts_vals, journal, account_number)
        # Create the bank statements
        statement_ids, notifications = self._create_bank_statements(stmts_vals)
        # Now that the import worked out, set it as the bank_statements_source
        # of the journal
        journal.bank_statements_source = 'bankintegration_import'
        # Finally dispatch to reconciliation interface
        action = self.env.ref('account.action_bank_reconcile_bank_statements')
        return {
            'name': action.name,
            'tag': action.tag,
            'context': {
                'statement_ids': statement_ids,
                'notifications': notifications
            },
            'type': 'ir.actions.client',
        }
