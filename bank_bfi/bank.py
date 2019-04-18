# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010, 2014 Tiny SPRL (<http://tiny.be>).
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

import re
import datetime as dt
import base64

from openerp.osv import fields, osv
from openerp.osv.orm import TransientModel
from openerp.tools.translate import _


class import_transactions(TransientModel):
    _name = 'import.transactions'
    _columns = {
        'file': fields.binary('File')
    }

    def import_file(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids[0], context)
        if obj.file:
            origin = base64.decodestring(obj.file)
            try:
                data = self.get_transactions_data(origin)
            except:
                raise osv.except_osv(_('Error!'), _('The file is not valid.'))
            t_ids = self.create_bank_statements(cr, uid, data, context)
            return t_ids
        else:
            raise osv.except_osv(_('Error!'), _('You must select a file.'))

    def create_bank_statements(self, cr, uid, data, context=None):
        abs_obj = self.pool.get('account.bank.statement')
        cmp_obj = self.pool.get('res.company')
        cmp_id = cmp_obj._company_default_get(cr, uid, 'account.account',
                                              context=context)
        company = cmp_obj.browse(cr, uid, cmp_id, context)

        # Se selecciona la misma compania para coger la cuenta por defecto.
        rp_obj = self.pool.get('res.partner')
        ptn = rp_obj.browse(cr, uid, 1, context)

        abs_ids = []
        for d in data:
            abs_data = {}
            abs_data['journal_id'] = self.find_bank_journal(company, d['account'])
            abs_data['name'] = 'Estado de cuenta'
            abs_data['date'] = d['emission_date']
            balance_start = self.compute_balance_end_real(cr, uid, abs_data['journal_id'], context=context)
            abs_data['balance_start'] = d['start_balance'] if balance_start == 0.0 else balance_start
            pre_balance = 0.0
            abs_data['line_ids'] = []
            for t in d['transactions']:
                transaction = {}
                transaction['date'] = t['date']
                transaction['name'] = t['description']
                transaction['ref'] = t['ref']
                if t['debit'] > 0:
                    transaction['type'] = 'supplier'
                    transaction['account_id'] = ptn.property_account_payable.id
                    transaction['amount'] = t['debit'] * (-1)
                else:
                    transaction['type'] = 'customer'
                    transaction['account_id'] = ptn.property_account_receivable.id
                    transaction['amount'] = t['credit']

                if not self.exist_transaction(cr, uid, transaction, context):
                    pre_balance += float(transaction['amount'])
                    abs_data['line_ids'].append((0, 0, transaction))

            if abs_data['line_ids']:
                abs_data['balance_end_real'] = abs_data['balance_start'] + pre_balance
                bid = abs_obj.create(cr, uid, abs_data, context)
                abs_ids.append(bid)
        return abs_ids

    def find_bank_journal(self, company, account):
        banks = filter(lambda x: account == x.acc_number, company.bank_ids)
        if banks:
            return banks[0].journal_id.id
        raise osv.except_osv(_('Error!'),
          _("The company doesn't have the bank account %s") % (account,))
    
    def compute_balance_end_real(self, cr, uid, journal_id, context=None):
        res = False
        if journal_id:
            cr.execute('SELECT balance_end_real \
                    FROM account_bank_statement \
                    WHERE journal_id = %s \
                    ORDER BY date DESC,id DESC LIMIT 1', (journal_id,))
            res = cr.fetchone()
        return res and res[0] or 0.0

    def exist_transaction(self, cr, uid, transaction, context=None):
        line = self.pool.get('account.bank.statement.line')
        to_search = [(k, '=', v) for k, v in transaction.iteritems()]
        exist = line.search(cr, uid, to_search, context=context)
        return True if exist else False

    def is_head(self, line):
        head = filter(lambda x: x != ' ', line)
        if head.startswith('ESTADODECUENTA'):
            return True
        return False

    def get_transactions_data(self, origin):
        file_list = origin.split('\n')
        data = []
        cl = 3

        # TODO: cambiar numeros por expresiones regulares
        while(cl < len(file_list)):
            if self.is_head(file_list[cl]):
                new_data = {}
                emission_date = file_list[cl + 1][-20:]
                emission_date = emission_date.strip()
                emission_date = dt.datetime.strptime(emission_date, "%d %m %y %H:%M:%S")
                new_data['emission_date'] = emission_date
                account = file_list[cl + 3][14:30]
                new_data['account'] = account
                currency = file_list[cl + 4][15:18]
                new_data['currency'] = currency
                cl += 8
            elif re.match('[0-9]', file_list[cl]):
                if file_list[cl][38:73].rstrip() == 'Saldo Anterior':
                    start_balance = file_list[cl][112:131]
                    start_balance = float(start_balance.replace(',', ''))
                    new_data['start_balance'] = start_balance
                    cl += 1
                elif file_list[cl][38:73].rstrip() == 'Saldo':
                    balance = file_list[cl][112:131]
                    balance = float(balance.replace(',', ''))
                    new_data['balance'] = balance
                    if 'transactions' in new_data:
                        data.append(new_data)
                    cl += 4
                else:
                    new_transaction = {}
                    new_transaction['date'] = dt.datetime.strptime(file_list[cl][:8] , "%d %m %y")
                    new_transaction['value_date'] = dt.datetime.strptime(file_list[cl][11:19] , "%d %m %y")
                    new_transaction['ref'] = file_list[cl][22:36]
                    new_transaction['description'] = file_list[cl][38:73].rstrip()
                    desc_count = 1
                    dcl = cl + 1
                    while(file_list[dcl].startswith(' ')):
                        new_transaction['description'] += file_list[dcl][38:73].rstrip()
                        dcl += 1
                        desc_count += 1
                    debit = file_list[cl][73:93].lstrip()
                    if debit == '':
                        new_transaction['debit'] = 0.0
                    else:
                        debit = float(debit.replace(',', ''))
                        new_transaction['debit'] = debit
                    credit = file_list[cl][93:112].lstrip()
                    if credit == '':
                        new_transaction['credit'] = 0.0
                    else:
                        credit = float(credit.replace(',', ''))
                        new_transaction['credit'] = credit
                    balance = file_list[cl][112:131]
                    balance = float(balance.replace(',', ''))
                    new_transaction['balance'] = balance
                    if 'transactions' in new_data:
                        new_data['transactions'].append(new_transaction)
                    else:
                        new_data['transactions'] = [new_transaction]
                    cl += desc_count
            else:
                cl += 1
        return data
    
    
class statement_line_supplier(TransientModel):
    _name = 'statement.line.supplier'
    _columns = {
        'supplier_id': fields.many2one('res.partner', 'Supplier')
    }

    def set_supplier_to_lines(self, cr, uid, ids, context=None):
        supplier_id = self.browse(cr, uid, ids[0], context).supplier_id.id
        vals = {'partner_id': supplier_id}
        absl = self.pool.get('account.bank.statement.line')
        absl.write(cr, uid, context['active_ids'], vals, context)
        return {'type': 'ir.actions.act_window_close'}
