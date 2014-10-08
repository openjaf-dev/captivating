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
    
    def _get_hotel_from(self, cr, uid, ids, fields, args, context=None):        
        return self.get_hotel_match(cr, uid, ids, 'end_date', context)
        
    def _get_hotel_to(self, cr, uid, ids, fields, args, context=None):          
        return self.get_hotel_match(cr, uid, ids, 'start_date', context)
    
    def get_hotel_match(self, cr, uid, ids, target_date, context):
        
        result = {} 
          
        hotel = self.pool.get('product.hotel')
        sale = self.pool.get('sale.order')
        order_line = self.pool.get('sale.order.line')
        
        for obj in self.browse(cr, uid, ids, context):
            result[obj.id] = ''
            if obj.product_id.categ_id.name == 'Transfer':
                sale_obj = sale.browse(cr, uid, obj.order_id.id)
                for order_line_obj in sale_obj.order_line:
                    product = order_line_obj.product_id
                    if product.categ_id.name == 'Hotel' and getattr(order_line_obj, target_date) == obj.start_date:
                        result[obj.id] = product.name      
          
        return result    
    
    _columns = {             
        'hotel_from':
            fields.function(_get_hotel_from, method=True, type='char',
                            string='Hotel from', size=128),             
        'hotel_to':
            fields.function(_get_hotel_to, method=True, type='char',
                            string='Hotel to', size=128),
                   
        
    }
    
class sale_order(Model):
    _name = 'sale.order'
    _inherit = 'sale.order'
    
    def _get_start_transfer(self, cr, uid, ids, fields, args, context=None):        
        return self.get_product_match(cr, uid, ids, 'start_date', 'date_order', 'Transfer', context)
        
    def _get_end_transfer(self, cr, uid, ids, fields, args, context=None):          
        return self.get_product_match(cr, uid, ids, 'start_date', 'end_date', 'Transfer', context)
    
    def _get_start_hotel(self, cr, uid, ids, fields, args, context=None):        
        return self.get_product_match(cr, uid, ids, 'start_date', 'date_order', 'Hotel', context)
        
    def _get_end_hotel(self, cr, uid, ids, fields, args, context=None):          
        return self.get_product_match(cr, uid, ids, 'end_date', 'end_date', 'Hotel', context)
         
    def get_product_match(self, cr, uid, ids, order_line_date, order_date, product_name, context):        
        result = {} 
                
        for obj in self.browse(cr, uid, ids, context):
            result[obj.id] = ''
            for order_line_obj in obj.order_line:
                product = order_line_obj.product_id
                if product.categ_id.name == product_name and getattr(order_line_obj, order_line_date) == getattr(obj, order_date):
                    result[obj.id] = product.name + " (" + str(order_line_obj.reservation_number) + ")"      
                  
        return result       
    
    _columns = {             
        'start_transfer':
            fields.function(_get_start_transfer, method=True, type='char',
                            string='Start Transfer', size=128),             
        'end_transfer':
            fields.function(_get_end_transfer, method=True, type='char',
                            string='End Transfer', size=128),
        'start_hotel':      
            fields.function(_get_start_hotel, method=True, type='char',
                            string='Start Hotel', size=128),     
        'end_hotel':      
            fields.function(_get_end_hotel, method=True, type='char',
                            string='End Hotel', size=128),     
        
    }