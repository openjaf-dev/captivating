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
from openerp.osv import fields

class sale_order(Model):
    _name = 'sale.order'
    _inherit = 'sale.order'
    
    _columns = {
        'voucher_logo': fields.selection([('dc', 'Destination Cuba'), 
                                          ('cc', 'Captivating Cuba')],
                            'Voucher Logo'),
    }
    
    _defaults = {
                 'voucher_logo': 'dc'
                 }

class sale_order_line(Model):
    _name = 'sale.order.line'
    _inherit = 'sale.order.line'

    def print_voucher(self, cr, uid, ids, context=None):
        datas = {
                 'model': 'sale.order.line',
                 'ids': ids,
                 'form': self.read(cr, uid, ids, context=context),
        }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'travel_voucher_report',
            'datas': datas,
            'nodestroy': True
        }
