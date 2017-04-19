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
from openerp.exceptions import except_orm, Warning, RedirectWarning
from openerp import _


class sale_order(Model):
    _name = 'sale.order'
    _inherit = 'sale.order'
    
    _columns = {
        'voucher_logo': fields.selection([('dc', 'Destination Cuba'), 
                                          ('cc', 'Captivating Cuba'),
                                          ('cd', 'Destino Cuba'),
                                          ('htg', 'Hovis Travel Group')],
                                         'Voucher Logo'),
    }
    
    _defaults = {
                 'voucher_logo': 'dc'
                 }

    # def action_button_confirm(self, cr, uid, ids, context=None):
    #     for order in self.browse(cr, uid, ids, context):
    #         for line in order.order_line:
    #             if line.price_unit == 0:
    #                 raise except_orm(_('Operation Canceled'), _('Please verify that price unit lines must be distinct of zero.'))
    #     return super(sale_order, self).action_button_confirm(cr, uid, ids, context)


class sale_order_line(Model):
    _name = 'sale.order.line'
    _inherit = 'sale.order.line'

    def get_margin_days(self, cr, uid, params, context=None):
        '''
        The number of days of the service countable for apply a per day margin.
        Redefining the travel_core function
        '''
        if not params.get('start_date', False) or not params.get('end_date', False):
            raise Warning(_('Please introduce the range of date.'))
        return super(sale_order_line, self).get_margin_days(cr, uid, params, context)

    def onchange_category(self, cr, uid, ids, category_id, context=None):
        if not category_id:
            res = {}
            order_line = self.browse(cr, uid, ids)
            if order_line:
                if not order_line.start_date and not order_line.end_date:
                    res['value'] = {'start_date': context.get('date_order', False), 'end_date': context.get('end_date', False)}
            else:
                res['value'] = {'start_date': context.get('date_order', False), 'end_date': context.get('end_date', False)}
            return res
        else:
            return super(sale_order_line, self).onchange_category(cr, uid, ids, category_id, context)
