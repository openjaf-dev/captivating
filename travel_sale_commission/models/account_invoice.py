# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

from openerp import api, fields, models


# class AccountInvoice(models.Model):
#     """Invoice inherit to add salesman"""
#     _inherit = "account.invoice"
#
#     @api.depends('invoice_line')
#     def _compute_commission_total(self):
#         for record in self:
#             record.commission_total = 0.0
#             for line in record.invoice_line:
#                 record.commission_total += sum(x.amount for x in line.agents)
#
#     commission_total = fields.Float(
#         string="Commissions", compute="_compute_commission_total",
#         store=True)
#
#     commission_total = fields.Float(
#         string="Commissions", compute="_compute_commission_total",
#         store=True)
#
#
# class AccountInvoiceLine(models.Model):
#     _inherit = "account.invoice.line"
#
#     commission_free = fields.Boolean(
#         string="Comm. free", related="product_id.commission_free",
#         store=True, readonly=True)
