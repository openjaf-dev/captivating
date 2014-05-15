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

from openerp.osv import fields
from openerp.osv.orm import Model


class res_partner(Model):
    _name = "res.partner"
    _description = "Partner extension for MIG attributes."
    _inherit = "res.partner"
    _columns = {
        'mid': fields.char('Migration ID', size=128,
                            select=1, help='Format "concept.table,id". Ex: Clients.ResPartner,12'),
    }


class res_bank(Model):
    _name = "res.bank"
    _description = "Bank extension for MIG attributes."
    _inherit = "res.bank"
    _columns = {
        'mid': fields.char('Migration ID', size=128,
                            select=1, help='Format "concept.table,id". Ex: Proveedores.Banco,10'),
    }


class res_partner_bank(Model):
    _name = "res.partner.bank"
    _description = "Partner extension for MIG attributes."
    _inherit = "res.partner.bank"
    _columns = {
        'mid': fields.char('Migration ID', size=128,
                            select=1, help='Format "concept.table,id". Ex: Proveedores.CuentaBanco,12'),
    }


class destination(Model):
    _name = "destination"
    _description = "Destination extension for MIG attributes."
    _inherit = "destination"
    _columns = {
        'mid': fields.char('Migration ID', size=128,
                            select=1, help='Format "concept.table,id". Ex: Destination.Distancias,12'),
    }


class destination_distance(Model):
    _name = "destination.distance"
    _description = "Destination distance extension for MIG attributes."
    _inherit = "destination.distance"
    _columns = {
        'mid': fields.char('Migration ID', size=128,
                            select=1, help='Format "concept.table,id". Ex: Destination.Distancias,12'),
    }
