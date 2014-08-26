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

from openerp.osv import fields
from openerp.osv.orm import Model


class product_product(Model):
    _name = 'product.product'
    _inherit = 'product.product'
    _columns = {
        'mid': fields.char('Migration ID', size=128,
                            select=1, help='Format "concept.table,id". Ex: Hotel.ProductHotel,23'),
    }
    
class product_hotel(Model):
    _name = 'product.hotel'
    _inherit = 'product.hotel'
    _columns = {
        'address': fields.text('Address'),
        'phone': fields.char('Phone'),
        'fax': fields.char('Fax')
    }


class option_value(Model):
    _name = 'option.value'
    _inherit = 'option.value'
    _columns = {
        'mid': fields.char('Migration ID', size=128,
                            select=1, help='Format "concept.table,id". Ex: Hotel.ProductHotel,23'),
    }
