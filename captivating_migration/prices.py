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
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################

import xlrd
import datetime
import base64
from data_utils import data_utils

from openerp.osv import fields, osv
from openerp.osv.orm import TransientModel

class import_prices(data_utils, TransientModel):
    _name = 'import.prices'
    _columns = {
        'file':
            fields.binary('File'),
        'result':
            fields.text('Result'),
        'accept':
            fields.boolean('Display Warnings')
    }

    def import_file(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids[0], context)
        display_warning = obj.accept
        if obj.file:
            data = base64.decodestring(obj.file)
            #try:
            msg = ' '
            document = xlrd.open_workbook(file_contents=data)
                 
#            pricelist_partnerinfo = self.pool.get('pricelist.partnerinfo') 
#            pricelist_ids = pricelist_partnerinfo.search(cr, uid, [])
#            for pricelist_id in pricelist_ids:                
#                pricelist_partnerinfo.unlink(cr, uid, pricelist_id, context)           
#            product_supplierinfo = self.pool.get('product.supplierinfo')
#            suppl_ids = product_supplierinfo.search(cr, uid, [])
#            for supplinfo_id in suppl_ids:                
#                product_supplierinfo.unlink(cr, uid, supplinfo_id, context)

            
            accept_suggestion = obj.accept 
            for sheet in document.sheets():
                if sheet.nrows != 0:
                    destination = self.pool.get('destination')
                    destination_vals = { 'name': sheet.name.strip() }
                    destination_id = destination.search(cr, uid, [('name', '=', destination_vals['name'])], context=context)
                    if not destination_id:
                        destination_id = destination.create(cr, uid, destination_vals, context)
                    else:
                        destination_id = destination_id[0]
                    new_msg = self.import_prices_data(cr, uid, sheet, destination_id, display_warning, context)
                    if new_msg != '':
                        msg += new_msg + '\n'
                    else:
                        msg += new_msg
                    
            #except:
            #    raise osv.except_osv('Error!', 'The file is not valid.')

            self.write(cr, uid, obj.id, {'result': msg}, context)
            return {
                'name': 'Import Prices',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'import.prices',
                'res_id': obj.id,
                'target': 'new',
                'context': context,
            }
        else:
            raise osv.except_osv('Error!', 'You must select a file.')

    def import_prices_data(self, cr, uid, sheet, destination_id, display_warning, context):
        
        msg = ''
        
        hotel = self.pool.get('product.hotel')
        product_product = self.pool.get('product.product')
        supplier = self.pool.get('res.partner')
        product_supplierinfo = self.pool.get('product.supplierinfo')
        pricelist_partnerinfo = self.pool.get('pricelist.partnerinfo')
        
        head = {sheet.cell_value(0, x): x for x in range(sheet.ncols)} 
        product_hotel = False
        hotel_info = ''
        supplier_id = False
        suppinfo_id = False
        meal_plan_id = False
        room_type_id = False
        date_from = False
        date_to = False
        child1 = False
        child2 = False
        double_value = False
        double_option = False
        simple_value = False
        simple_option = False
        triple_value = False
        triple_option = False
        candidates_dict = {}
        for r in range(1, sheet.nrows):
            
            def cell(attr):
                if sheet.cell(r, head[attr]).ctype == xlrd.XL_CELL_ERROR:
                    return None
                return sheet.cell_value(r, head[attr])
                
            if cell('HOTEL NAME'):
                # insert additional information (room and hotel comments) of previous hotel
                if suppinfo_id:
                    product_supplierinfo.write(cr, uid, [suppinfo_id], {'info': hotel_info})
                    print hotel_info
                    hotel_info = ''
                
                hotel_name = cell('HOTEL NAME').strip()
                category_id = self.get_category(cr, uid, 'Hotel', context)
                product_id, ratio = self.get_product(cr, uid, category_id, hotel_name, display_warning)
                product_hotel = product_product.browse(cr, uid, product_id, context)
                
                hotel_id = hotel.search(cr, uid, [('name', '=', product_hotel.name)])[0]
                hotel.write(cr, uid, hotel_id, {'destination': destination_id})
                
                if ratio:
                    msg += "WARNING: " + hotel_name + " is " + product_hotel.name + "? " + str(ratio) + '\n'   
                    product_hotel = None
                
            if cell('SUPPLIER'):
                if product_hotel:
                    supplier_name = str(cell('SUPPLIER')).strip()
                    supplier_id, ratio = self.get_partner(cr, uid, supplier_name, False, display_warning, context)
                    if display_warning and 0.8 < ratio < 1.0:  
                        
                        supplier_warning = supplier.browse(cr, uid, supplier_id, context)
                        msg += "WARNING: " + supplier_name + " is " + supplier_warning.name + "? " + str(ratio) + '\n'
                        supplier_id = None   
                    else:  
                    
                        suppinfo_ids = product_supplierinfo.search(cr, uid, ['&', 
                                                                             ('name', '=', supplier_id), 
                                                                             ('product_id', '=', product_hotel.product_tmpl_id.id)], 
                                                                   context=context)
                        if len(suppinfo_ids) == 0:
        
                            svals = {
                                'name': supplier_id,
                                'product_id': product_hotel.product_tmpl_id.id,
                                'min_qty': 0
                            }
                            
                            suppinfo_id = product_supplierinfo.create(cr, uid, svals, context)
                        else:
                            suppinfo_id = suppinfo_ids[0] 
                                   
            if cell('MEAL PLAN'):
                meal_plan_id = cell('MEAL PLAN').strip()
                mp = self.get_option_value(cr, uid, meal_plan_id, 'mp', context)
                
            if cell('ROOM CATEGORY'):
                room_type_str = cell('ROOM CATEGORY').strip()
                room_type_id = self.get_option_value(cr, uid, room_type_str, 'rt', context)
                
            if cell('DATEBAND FROM'):
                date_from = self.get_date(cell('DATEBAND FROM'))
                double_value = False
                double_option = False
                simple_value = False
                simple_option = False
                triple_value = False
                triple_option = False
                
            if cell('DATEBAND TO'):
                date_to = self.get_date(cell('DATEBAND TO'))  
        
            if cell('ROOM TYPE'):
                if cell('ROOM TYPE') == 'C1':
                    child1 = cell('NET RATE')
                elif cell('ROOM TYPE') == 'C2':
                    child2 = cell('NET RATE')                       
                elif cell('ROOM TYPE') == 'D':
                    double_value = self.get_float(cell('NET RATE'))
                    double_option = True
                elif cell('ROOM TYPE') == 'S':
                    simple_value = self.get_float(cell('NET RATE'))
                    simple_option = True                    
                elif cell('ROOM TYPE') == 'T':
                    triple_value = self.get_float(cell('NET RATE'))
                    triple_option = True    
            
            if cell('HOTEL COMMENTS') and cell('HOTEL COMMENTS').strip() != '':
                hotel_info = cell('HOTEL COMMENTS') + '\n\n' + hotel_info 
                                
            if cell('ROOM COMMENTS') and cell('ROOM COMMENTS').strip() != '':
                hotel_info += self.pool.get('option.value').name_get(cr, uid, room_type_id)[0][1] + '\n' 
                hotel_info +=  cell('ROOM COMMENTS') + '\n\n' 
            
            if simple_option and double_option and triple_option and product_hotel and supplier_id:
                 pvals = {
                    'suppinfo_id': suppinfo_id,
                    'start_date': date_from,
                    'end_date': date_to,
                    'room_type_id': room_type_id,
                    'meal_plan_id': mp,
                    'price': double_value,
                    'simple': simple_value,
                    'triple': triple_value,
                    'child': child1,
                    'second_child': child2,
                    'min_quantity': 0
                 }                 
                 
                 pricelist_ids = pricelist_partnerinfo.search(cr, uid, [('suppinfo_id', '=', suppinfo_id), 
                                                                       ('start_date', '=', date_from), 
                                                                       ('end_date', '=', date_to), 
                                                                       ('room_type_id', '=', room_type_id),
                                                                       ('meal_plan_id', '=', mp)], 
                                                             context=context)
                 if len(pricelist_ids) > 0:
                     pricelist_partnerinfo.write(cr, uid, [pricelist_ids[0]], {'price': double_value, 
                                                                           'simple': simple_value,
                                                                           'triple': triple_value,
                                                                           'child': child1,
                                                                           'second_child': child2}, 
                                                 context=context)                     
                 else:
                     pricelist_partnerinfo.create(cr, uid, pvals, context)
                     
           
        # insert additional information (room and hotel comments) of previous hotel
        # last hotel in sheet case
        if suppinfo_id:
            product_supplierinfo.write(cr, uid, [suppinfo_id], {'info': hotel_info})
            hotel_info = ''      #msg += 'Price list added \n'     
                
        return msg
        
