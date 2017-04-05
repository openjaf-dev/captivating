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


class ResPartner(models.Model):
    """Add some fields related to commissions"""
    _inherit = "res.partner"

    agent = fields.Boolean(
        string="Creditor/Agent",
        help="Check this field if the partner is a creditor or an agent.")
    agent_type = fields.Selection(
        selection=[("agent", "External agent")], string="Type", required=True,
        default="agent")
    commission = fields.Many2one('sale.commission', string="Commission",
                                 help="This is the default commission used in the sales where this "
                                      "agent is assigned. It can be changed on each operation if "
                                      "needed.")
    vat_commission = fields.Many2one('sale.vat', string="VAT Commission",
                                     help="This is the default vat commission used in the sales where this "
                                          "agent is assigned. It can be changed on each operation if "
                                          "needed.")

    @api.onchange('agent_type')
    def onchange_agent_type(self):
        if self.agent_type == 'agent' and self.agent:
            self.supplier = True
