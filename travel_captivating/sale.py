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
        if context.get('params', False):
            if not context['params'].get('start_date', False) or not context['params'].get('end_date', False):
                raise Warning(_('Please introduce the range of date.'))
        return super(sale_order_line, self).onchange_category(cr, uid, ids, category_id, context)


class sale_context(Model):
    _name = 'sale.context'
    _inherit = 'sale.context'

    def _get_default_start_date(self, cr, uid, ids, context=None):
        sale_context = self.browse(cr, uid, ids)
        date = ''
        if sale_context.order_id:
            date = sale_context.order_id.date_order
        elif context != {}:
            if context.get('date_order', False):
                date = context.get('date_order', False)
        return date

    _columns = {
        # 'order_line': fields.one2many('sale.order.line', 'sale_context_id', 'Order Lines', readonly=True, copy=True),
        'start_date': fields.date('Start Date'),
        'end_date': fields.date('End Date'),
    }

    _defaults = {
                 'start_date': _get_default_start_date,
                 # 'start_date': lambda self, cr, uid, context: context.get('date_order', False),
                 'end_date': lambda self, cr, uid, context: context.get('end_date', False)
                 # 'end_date': lambda self, cr, uid, context: context.get('end_date', False)
                 }