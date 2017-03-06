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

import datetime as dt

from openerp.osv import fields, osv
from openerp.osv.orm import Model
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from openerp.tools.translate import _
from openerp import models, fields, api, _


class account_invoice(models.Model):
    _name = "account.invoice"
    _inherit = 'account.invoice'

    @api.one
    @api.depends('invoice_line')
    def _compute_line_zero(self):
        line_zero = False
        for line in self.invoice_line:
            if line.price_unit == 0:
                line_zero = True
        self.line_zero = line_zero

    line_zero = fields.Boolean(string='Line Zero', store=True, readonly=True, compute='_compute_line_zero',
                               help="It indicates that the invoice has lines with price zero.")

    @api.multi
    def button_rectify_price(self):
        order = self.env['sale.order'].search([('name', '=', self.origin)], limit=1)
        price_list = order.pricelist_id.id
        for line in self.invoice_line:
            product_id = line.product_id.id
            qty = line.quantity
            uom = line.uos_id.id
            supplier_id = self.partner_id.id
            date_order = order.date_order

            cost_price, cost_currency_id = self.env['sale.order.line'].show_cost_price({}, product_id, qty, supplier_id,
                                                                                       uom, date_order, supplier_id,
                                                                                       {}, price_list)
            if cost_currency_id != self.currency_id.id:
                cost_price = cost_price * self.currency_id.rate

            line.write({'price_unit': cost_price})

        return True