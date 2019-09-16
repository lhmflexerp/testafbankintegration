# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2018-     Odoo House (<https://odoohouse.dk>).
#
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
#
##############################################################################

{
    'name': 'Odoo Hosting Bankintegration',
    'version': '1.0',
    'category': 'Tools',
    'description': """
Odoo Hosting Bankintegration.
=======================================
This module use bankintegration.dk api to import bank statements into bank. And also allow payment of vendor invoices.
""",
    'author': 'Odoo Hosting',
    'website': 'http://odoohosting.dk',
    'summary': 'Odoo Hosting Bankintegration',
    'sequence': 20,
    'depends': ['base', 'base_vat', 'account', 'account_bank_statement_import', 'account_cancel'],
    'data': [
        'views/conversion_list_view.xml',
        'views/res_config_view.xml',
        'views/res_bank_view.xml',
        'views/account_bank_statement_import_view.xml',
        'views/account_invoice_view.xml',
        'views/bank_statement_view.xml',
        'wizard/account_bankintegration_payment_view.xml',
        'views/config_data.xml',
        'security/ir.model.access.csv',
        'data/bankintegration.conversion_list.csv'
    ],
    'demo': [
    ],
    'test': [
    ],
    'css': [
    ],
    'images': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
