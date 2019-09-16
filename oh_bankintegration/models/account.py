# -*- coding: utf-8 -*-
from odoo import fields, models, _, api
from odoo.exceptions import UserError, ValidationError
from dateutil.parser import parse
import logging
_logger = logging.getLogger(__name__)


class AccountJournal(models.Model):
    _name = "account.journal"
    _inherit = ["account.journal"]

    def _get_oh_bank_statements_available_import_formats(self):
        # return ["bankintegration_import", "manual"]
        return [('bankintegration_import', _('Auto import from bankintegration'))]

    def __get_bank_statements_available_sources(self):
        rslt = super(AccountJournal,
                     self).__get_bank_statements_available_sources()
        formats_list = self._get_oh_bank_statements_available_import_formats()
        if formats_list:
            # formats_list.sort()
            #import_formats_str = ', '.join(formats_list)
            rslt += formats_list
        return rslt

    customer_code = fields.Char(
        string='Integration Code', help="Please provide Integration Code for bankintegration.")

    def get_last_import_date(self, journal_id):
        error_msg = _('Something went wrong.')
        try:
            # Code to get previous import data
            bank_stmt_obj = self.env['account.bank.statement']
            bank_stmt_line_obj = self.env['account.bank.statement.line']
            last_import_date = None
            last_import_balance = 0.0
            bank_stmt_res = bank_stmt_obj.search(
                [('journal_id', '=', journal_id)], limit=1, order='id desc')
            _logger.debug('bank statement object')
            _logger.debug(bank_stmt_res)
            if bank_stmt_res:
                last_import_balance = bank_stmt_res.balance_end_real
                _logger.debug('last_import_balance:')
                _logger.debug(last_import_balance)
                bank_stmt_line_res = bank_stmt_line_obj.search(
                    [('statement_id', '=', bank_stmt_res.id)], limit=1, order='id desc')
                if bank_stmt_line_res:
                    last_import_date = bank_stmt_line_res.date

                return last_import_date, last_import_balance
            else:
                error_msg = _(
                    'For first time import please make a starting statement, with ending balance filled out, and a unposted transaction with starting reference number.')
                raise ValidationError(error_msg)
            # End of Code to get previous import data
        except Exception as e:
            print(str(e))
            _logger.debug(str(e))
            raise ValidationError(error_msg)

    @api.multi
    def bankintegration_statement(self):
        journal_id = self.id
        account_invoice_model = self.env['account.invoice']
        request_model = self.env['bank.integration.request']
        bank_statement_import_model = self.env['account.bank.statement.import']
        request_obj = request_model.create({})
        auth_header, request_id = account_invoice_model.get_bank_statement_token(
            request_obj.id, journal_id)
        last_import_date, last_import_balance = self.get_last_import_date(
            journal_id)
        stmts_data = account_invoice_model.get_bank_statements(
            auth_header, request_id, last_import_date, last_import_balance)
        if stmts_data:
            bank_statement_import_model.bankintegration_import_statements(
                stmts_data['currency'], stmts_data['account'], stmts_data['statement'])
        else:
            raise ValidationError(_('Nothing to import.'))

    @api.multi
    def bankintegration_statement_auto(self):
        journal_ids = self.search(
            [('bank_statements_source', '=', 'bankintegration_import')])
        for journal in journal_ids:
            journal_id = journal.id
            account_invoice_model = self.env['account.invoice']
            request_model = self.env['bank.integration.request']
            bank_statement_import_model = self.env[
                'account.bank.statement.import']
            request_obj = request_model.create({})
            auth_header, request_id = account_invoice_model.get_bank_statement_token(
                request_obj.id, journal_id)
            last_import_date, last_import_balance = self.get_last_import_date(
                journal_id)
            stmts_data = account_invoice_model.get_bank_statements(
                auth_header, request_id, last_import_date, last_import_balance)
            if stmts_data:
                bank_statement_import_model.bankintegration_import_statements(
                    stmts_data['currency'], stmts_data['account'], stmts_data['statement'])


class AccountBankStatementLine(models.Model):
    _inherit = 'account.bank.statement.line'

    json_log = fields.Text(string='Log')
