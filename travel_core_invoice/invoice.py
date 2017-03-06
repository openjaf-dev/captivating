# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010, 2013, 2014 Tiny SPRL (<http://tiny.be>).
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

from openerp.osv.orm import Model
from openerp import models, fields, api, _
from openerp import workflow
from openerp.exceptions import except_orm, Warning, RedirectWarning


class account_voucher(Model):
    _name = 'account.voucher'
    _description = 'Accounting Voucher'
    _inherit = 'account.voucher'

    def voucher(self, cr, uid, values, context, invoice_type):

        idvoucher = None
        values_voucher = {}
        invoice_pool = self.pool.get('account.invoice')
        partner_pool = self.pool.get('res.partner')
        journal_pool = self.pool.get('account.journal')

        for inv in invoice_pool.browse(cr, uid, [values['invoice_id']], context=context):

            values_voucher['reference'] = inv.number
            values_voucher['name'] = inv.name
            values_voucher['type'] = 'receipt'

            values_voucher['partner_id'] = inv.partner_id.id
            if not values_voucher['partner_id']:
                raise except_orm(_('Operation Canceled'), _('Please verify that the customer exists.'))

            amount = 0
            for line in inv.invoice_line:
                amount += line.price_unit
            values_voucher['amount'] = amount

            values_voucher['date'] = inv.date_invoice

            if inv.company_id.journal_customer_payment_invoice_id:
                values_voucher['journal_id'] = inv.company_id.journal_customer_payment_invoice_id.id
            else:
                values_voucher['journal_id'] = journal_pool.search(cr, uid, [('type', '=', 'bank')])[0]

            if not values_voucher['journal_id']:
                raise except_orm(_('Operation Canceled'), _('Please verify that journal bank exist.'))

            values_voucher['type'] = 'receipt'
            ttype = 'sale'
            result = self.onchange_journal(cr, uid, [], values_voucher['journal_id'], [], False,
                                           values_voucher['partner_id'], False, values_voucher['amount'],
                                           ttype, False, context)
            values_voucher['tax_id'] = result['value']['tax_id']
            values_voucher['amount'] = result['value']['amount']
            values_voucher['currency_id'] = result['value']['currency_id']
            values_voucher['account_id'] = result['value']['account_id']

            idvoucher = super(account_voucher, self).create(cr, uid, values_voucher, context=context)

            account_voucher_line_pool = self.pool.get('account.voucher.line')
            partner_obj = partner_pool.browse(cr, uid, values_voucher['partner_id'], context)
            val_lin_vou = {}
            if partner_obj:
                if partner_obj.customer and values_voucher['type'] == 'receipt':
                    move_avl = [move_line for move_line in inv.move_id.line_id if move_line.account_id.id == inv.partner_id.property_account_receivable.id]

                    if move_avl:
                        for move_line in move_avl:
                            val_lin_vou = {
                                'voucher_id': idvoucher,
                                'name': inv.name,
                                'account_id': move_line.account_id.id,
                                'amount': move_line.debit,
                                'move_line_id':move_line.id,
                                'type': 'cr'
                            }

                account_voucher_line_pool.create(cr, uid, val_lin_vou, context=context)

        return idvoucher

    def voucher_workflow(self, cr, uid, values, context):
        self.signal_workflow(cr, uid, [values['voucher_id']], 'proforma_voucher')
        obj_voucher = self.browse(cr, uid, values['voucher_id'])
        self.pool.get('account.move').button_validate(cr, uid, [obj_voucher.move_id.id])


class account_invoice(Model):
    _name = 'account.invoice'
    _inherit = 'account.invoice'

    def invoice_workflow(self, cr, uid, values, context):
        self.test_paid(cr, uid, [values['invoice_id']])
        self.signal_workflow(cr, uid, [values['invoice_id']], 'invoice_open')

    def create(self, cr, uid, vals, context=None):
        inv_id = super(account_invoice, self).create(cr, uid, vals, context)

        if vals.get('type', False) == 'out_invoice':
            voucher_pool = self.pool.get('account.voucher')
            vals['invoice_id'] = inv_id
            self.invoice_workflow(cr, uid, vals, context)
            voucher_id = voucher_pool.voucher(cr, uid, vals, context, 'out_invoice')
            vals['voucher_id'] = voucher_id
            voucher_pool.voucher_workflow(cr, uid, vals, context)

        return inv_id
