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

from openerp import api, exceptions, fields, models, _


class SaleVat(models.Model):
    _name = "sale.vat"
    _description = "VAT in sales"

    name = fields.Char('Name', required=True)
    vat_type = fields.Selection(
        selection=[("fixed", "Fixed percentage"),
                   ("amount", "Fixed amount")],
        string="Type", required=True, default="fixed")
    fix_qty = fields.Float(string="Fixed percentage")
    fix_amount = fields.Float(string="Fixed amount")
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env['res.company']._company_default_get('sale.vat'))
    active = fields.Boolean(default=True)
