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

class sale_order_line(Model):
    _name = 'sale.order.line'
    _inherit = 'sale.order.line'
    
    def _get_related_order_lines(self, cr, uid, ids, context=None):
        # Get all order_lines belonging to same sale_order 
        res = {}
        for ol1 in self.browse(cr, uid, ids, context=context):
            for ol2 in ol1.order_id.order_line:
                res[ol2.id] = True
                
        return res.keys()  
        
    def _get_hotel_from(self, cr, uid, ids, fields, args, context=None):        
        return self.get_hotel_match(cr, uid, ids, 'end_date', context)
        
    def _get_hotel_to(self, cr, uid, ids, fields, args, context=None):          
        return self.get_hotel_match(cr, uid, ids, 'start_date', context)
    
    def _compute_start_end(self, cr, uid, ids, fields, args, context=None):
        
        result = {} 
          
        hotel = self.pool.get('product.hotel')
        sale = self.pool.get('sale.order')
        order_line = self.pool.get('sale.order.line')
        
        for obj in self.browse(cr, uid, ids, context):
            if obj.product_id.categ_id.name == 'Transfer':
                sale_obj = sale.browse(cr, uid, obj.order_id.id)
                for order_line_obj in sale_obj.order_line:
                    product = order_line_obj.product_id
                    if product.categ_id.name == 'Hotel':
                        if order_line_obj.end_date == obj.start_date:
                            result.setdefault(obj.id, {'hotel_from': product.name, 'hotel_to': ''})
                            result[obj.id]['hotel_from'] = product.name   
                        elif order_line_obj.start_date == obj.start_date:
                            result.setdefault(obj.id, {'hotel_from': '', 'hotel_to': product.name})
                            result[obj.id]['hotel_to'] = product.name     
          
        return result    
    
    _columns = {             
        'hotel_from':
            fields.function(_compute_start_end, method=True, type='char',
                            string='Hotel from', size=128,
                            store = {'sale.order.line': (_get_related_order_lines, 
                                                         ['start_date', 
                                                          'end_date',
                                                          'reservation_number',
                                                          'name'], 
                                                         10)},
                            multi = 'from_to'),             
        'hotel_to':
            fields.function(_compute_start_end, method=True, type='char',
                            string='Hotel to', size=128,
                            store = {'sale.order.line': (_get_related_order_lines, 
                                                         ['start_date', 
                                                          'end_date',
                                                          'reservation_number',
                                                          'name'], 
                                                         10)},
                            multi = 'from_to')
                   
        
    }
    
class sale_order(Model):
    _name = 'sale.order'
    _inherit = 'sale.order'   
     
    def _get_related_orders(self, cr, uid, ids, context=None):
        # Get all order_lines belonging to same sale_order 
        res = {}
        order_lines = self.pool.get('sale.order.line').browse(cr, uid, ids, context=context)
        for ol in order_lines:
                res[ol.order_id.id] = True
                
        return res.keys()  
    
    def _get_start_transfer(self, cr, uid, ids, fields, args, context=None):        
        return self.get_product_match(cr, uid, ids, 'start_date', 'date_order', 'Transfer', context)
        
    def _get_end_transfer(self, cr, uid, ids, fields, args, context=None):          
        return self.get_product_match(cr, uid, ids, 'start_date', 'end_date', 'Transfer', context)
    
    def _get_start_hotel(self, cr, uid, ids, fields, args, context=None):        
        return self.get_product_match(cr, uid, ids, 'start_date', 'date_order', 'Hotel', context)
        
    def _get_end_hotel(self, cr, uid, ids, fields, args, context=None):          
        return self.get_product_match(cr, uid, ids, 'end_date', 'end_date', 'Hotel', context)
         
    def _compute_start_end(self, cr, uid, ids, fields, args, context=None):        
        result = {} 
                
        for order_obj in self.browse(cr, uid, ids, context):
            order_lines = order_obj.order_line
            for i in range(0, len(order_obj.order_line)-1):
                for j in range(i+1, len(order_obj.order_line)):
                    hotel = None
                    transfer = None
                    def get_product(product_name):
                        for idx in [i,j]:
                            if order_lines[idx].product_id.categ_id.name == product_name:
                                return order_lines[idx]
                        return None
                    hotel = get_product('Hotel')
                    transfer = get_product('Transfer')
                    if hotel and transfer:
                        transfer_str = transfer.name + " (" + str(transfer.reservation_number) + ")"
                        hotel_str = hotel.name + " (" + str(hotel.reservation_number) + ")"
                        if order_obj.date_order == transfer.start_date:
                            result.setdefault(order_obj.id, {'start_transfer': transfer_str, 
                                                       'end_transfer': '',
                                                       'start_hotel': '',
                                                       'end_hotel': ''})
                            result[order_obj.id]['start_transfer'] = transfer_str
                        if order_obj.date_order == hotel.start_date:  
                            result.setdefault(order_obj.id, {'start_transfer': '', 
                                                       'end_transfer': '',
                                                       'start_hotel': hotel_str,
                                                       'end_hotel': ''})  
                            result[order_obj.id]['start_hotel'] = hotel_str                        
                        if order_obj.end_date == transfer.start_date:
                            result.setdefault(order_obj.id, {'start_transfer': '', 
                                                       'end_transfer': transfer_str,
                                                       'start_hotel': '',
                                                       'end_hotel': ''})
                            result[order_obj.id]['end_transfer'] = transfer_str
                        if order_obj.end_date == hotel.end_date:  
                            result.setdefault(order_obj.id, {'start_transfer': '', 
                                                       'end_transfer': '',
                                                       'start_hotel': '',
                                                       'end_hotel': hotel_str})   
                            result[order_obj.id]['end_hotel'] = hotel_str
                            
        return result   
                       
    _columns = {             
        'start_transfer':
            fields.function(_compute_start_end, method=True, type='char',
                            string='Start Transfer', size=128,
                            store = {'sale.order.line': (_get_related_orders, 
                                                         ['start_date', 
                                                          'end_date',
                                                          'reservation_number',
                                                          'name'], 
                                                         10)},
                            multi = 'from_to'),             
        'end_transfer':
            fields.function(_compute_start_end, method=True, type='char',
                            string='End Transfer', size=128,
                            store = {'sale.order.line': (_get_related_orders, 
                                                         ['start_date', 
                                                          'end_date',
                                                          'reservation_number',
                                                          'name'], 
                                                         10)},
                            multi = 'from_to'),
        'start_hotel':      
            fields.function(_compute_start_end, method=True, type='char',
                            string='Start Hotel', size=128,
                            store = {'sale.order.line': (_get_related_orders, 
                                                         ['start_date', 
                                                          'end_date',
                                                          'reservation_number',
                                                          'name'], 
                                                         10)},
                            multi = 'from_to'),     
        'end_hotel':      
            fields.function(_compute_start_end, method=True, type='char',
                            string='End Hotel', size=128,
                            store = {'sale.order.line': (_get_related_orders, 
                                                         ['start_date', 
                                                          'end_date',
                                                          'reservation_number',
                                                          'name'], 
                                                         10)},
                            multi = 'from_to'),     
        
    }