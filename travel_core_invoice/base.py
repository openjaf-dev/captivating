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

import datetime as dt

from openerp.osv import fields
from openerp.osv.orm import Model


class res_company(Model):
    _name = 'res.company'
    _inherit = 'res.company'

    def _journal_customer_payment_invoice(self, cr, uid, context=None):
        ctx = dict(context or {})
        journal_ids = self.pool.get('account.journal').search(cr, uid, [('type', '=', 'bank')], context=ctx)
        if journal_ids:
            return journal_ids[0]

    _columns = {
        'journal_customer_payment_invoice_id': fields.many2one('account.journal', 'Customer Payment Journal',
                                                               domain=[('type', '=', 'bank')],
                                                               help="Accounting journal used to pay customer invoice.")
                }

    _defaults = {
        'journal_customer_payment_invoice_id': _journal_customer_payment_invoice
    }
