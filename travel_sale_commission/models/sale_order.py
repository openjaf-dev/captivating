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


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.one
    @api.depends('order_line.amount_commission',
                 'order_line.amount_vat_commission',
                 'order_line.amount_subtotal_commission')
    def _compute_commission_total(self):
        commission_total = 0.0
        vat_commission_total = 0.0
        total_without_vat_commission = 0.0
        for line in self.order_line:
            commission_total += line.amount_commission
            vat_commission_total += line.amount_vat_commission
            total_without_vat_commission += line.amount_subtotal_commission
        self.commission_total = commission_total
        self.vat_commission_total = vat_commission_total
        self.total_without_vat_commission = total_without_vat_commission

    commission_total = fields.Float(
        string="Total Commissions", compute="_compute_commission_total",
        store=True)
    vat_commission_total = fields.Float(
        string="Vat Commissions", compute="_compute_commission_total",
        store=True)
    total_without_vat_commission = fields.Float(
        string="Total without Commissions and VAT", compute="_compute_commission_total",
        store=True)

    @api.multi
    def action_button_update_commission(self):
        for order in self:
            if order.partner_id.agent:
                for line in order.order_line:
                    vals_line = {
                        'flag_commission': True,
                        'agent_id': order.partner_id.id,
                        'commission': order.partner_id.commission.id,
                        'vat_commission': order.partner_id.vat_commission.id
                    }
                    line.write(vals_line)
        return True

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.multi
    @api.depends('price_subtotal', 'commission', 'vat_commission', 'agent_id')
    def _compute_amount_commission(self):
        for line in self:
            amount_commission = 0.0
            amount_vat_commission = 0.0
            amount_subtotal_commission = 0.0
            if (not line.product_id.commission_free and
                    line.commission):
                if line.commission.commission_type == 'fixed':
                    amount_commission = line.price_subtotal * (line.commission.fix_qty / 100.0)
                else:
                    amount_commission = line.commission.fix_amount
                if line.vat_commission.vat_type == 'fixed':
                    amount_vat_commission = amount_commission * (line.vat_commission.fix_qty / 100.0)
                else:
                    amount_commission = line.vat_commission.fix_amount
            amount_subtotal_commission = line.price_subtotal - amount_commission - amount_vat_commission
            line.amount_commission = amount_commission
            line.amount_vat_commission = amount_vat_commission
            line.amount_subtotal_commission = amount_subtotal_commission

    flag_commission = fields.Boolean(string="flag commission", default=False)
    commission_free = fields.Boolean(string="Comm. free", related="product_id.commission_free", store=True,
                                     readonly=True)
    agent_id = fields.Many2one('res.partner', ondelete="restrict", domain="[('agent', '=', True')]", string="Agent")
    commission = fields.Many2one('sale.commission', ondelete="restrict")
    amount_commission = fields.Float(compute="_compute_amount_commission", store=True, string="Amount Commissions")
    vat_commission = fields.Many2one('sale.vat', ondelete="restrict")
    amount_vat_commission = fields.Float(compute="_compute_amount_commission", store=True,
                                         string="Amount VAT Commissions")
    amount_subtotal_commission = fields.Float(compute="_compute_amount_commission", store=True)

#TODO: change to api new
    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0, uom=False, qty_uos=0, uos=False, name='',
                          partner_id=False, lang=False, update_tax=True, date_order=False, packaging=False,
                          fiscal_position=False, flag=False, context=None):
        rest = super(SaleOrderLine, self).product_id_change(cr, uid, ids, pricelist, product, qty, uom, qty_uos, uos,
                                                            name, partner_id, lang, update_tax, date_order, packaging,
                                                            fiscal_position, flag, context)
        if rest and rest.get('value', False):
            partner = self.pool.get('res.partner').browse(cr, uid, [partner_id])
            if partner.agent:
                rest['value']['flag_commission'] = True
                rest['value']['agent_id'] = partner_id
                rest['value']['commission'] = partner.commission
                rest['value']['vat_commission'] = partner.vat_commission
        return rest
