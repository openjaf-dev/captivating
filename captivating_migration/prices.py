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
import stringmatcher

from openerp.osv import fields, osv
from openerp.osv.orm import TransientModel

BASE_DATE = 693594
CATEGORIES = {
    'Car Hire': 'Car',
    'Extra': 'Miscellaneous',
    'Rep Fee': 'Miscellaneous',
    'tourist Card': 'Miscellaneous',
    'Excursion': 'Activity',
    'Tour': 'Activity',
    'Casa': 'Hotel',
    'Hotel': 'Hotel'
}
ROOM = {'simple': 1, 'double': 2, 'triple': 3}


class import_prices(TransientModel):
    _name = 'import.prices'
    _columns = {
        'file':
            fields.binary('File'),
        'result':
            fields.text('Result')
    }

    def import_file(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids[0], context)
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
             
            for sheet in document.sheets():
                if sheet.nrows != 0:
                    destination = self.pool.get('destination')
                    destination_vals = { 'name': sheet.name.strip() }
                    destination_id = destination.search(cr, uid, [('name', '=', destination_vals['name'])], context=context)
                    if not destination_id:
                        destination_id = destination.create(cr, uid, destination_vals, context)
                    msg += self.import_prices_data(cr, uid, sheet, destination_id, context)
                    
                    #self.import_sales_data(cr, uid, sheet, data, context)
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

    def import_prices_data(self, cr, uid, sheet, destination_id, context):
        
        msg = ' '
        
        hotel = self.pool.get('product.hotel')
        product_product = self.pool.get('product.product')
        supplier = self.pool.get('res.partner')
        product_supplierinfo = self.pool.get('product.supplierinfo')
        pricelist_partnerinfo = self.pool.get('pricelist.partnerinfo')
        
        head = {sheet.cell_value(0, x): x for x in range(sheet.ncols)} 
        product_hotel = False
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
        for r in range(1, sheet.nrows):
            
            def cell(attr):
                if sheet.cell(r, head[attr]).ctype == xlrd.XL_CELL_ERROR:
                    return None
                return sheet.cell_value(r, head[attr])
                
            if cell('HOTEL NAME'):
               
                hotel_name = cell('HOTEL NAME').strip()
                category_id = self.get_category(cr, uid, 'Hotel', context)
                product_id = self.get_product(cr, uid, category_id, hotel_name)
                product_hotel = product_product.browse(cr, uid, product_id, context)
                
            if cell('SUPPLIER'):
                supplier_name = str(cell('SUPPLIER')).strip()
                supplier_id = self.get_partner(cr, uid, supplier_name, False, context)
                
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
                    if len(suppinfo_ids) > 1:
                        print 'supplinfo ohoho ...'
                
                #msg += str(supplier_id)
                #suggestion, ratio = stringmatcher.find_closers(supplier_dict.keys(), supplier_name)
                #real_name = supplier.browse(cr, uid, supplier_dict[suggestion]).name
                #msg += "Supplier " + supplier_name + ", sugs:"+ real_name + " - " + str(ratio) +"\n"
                
                # insert res_partner
                
            if cell('MEAL PLAN'):
                meal_plan_id = cell('MEAL PLAN').strip()
                mp = self.get_option_value(cr, uid, meal_plan_id, 'mp', context)
                #msg += str(mp) + "\n"
                #option_type = self.pool.get('option.type')
                #option_type.search('Meal Plan')
                #msg += 'ok'
                
            if cell('ROOM CATEGORY'):
                room_type_str = cell('ROOM CATEGORY').strip()
                room_type_id = self.get_option_value(cr, uid, room_type_str, 'rt', context)
                #msg += str(rt) + '\n'
                
            if cell('DATEBAND FROM'):
                date_from = self.get_date(cell('DATEBAND FROM'))
                #msg += str(date_from)
                double_value = False
                double_option = False
                simple_value = False
                simple_option = False
                triple_value = False
                triple_option = False
                
            if cell('DATEBAND TO'):
                date_to = self.get_date(cell('DATEBAND TO'))
                #msg += str(date_to)                
        
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
            
            if simple_option and double_option and triple_option:
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
                     if len(pricelist_ids) > 1:
                         print 'pricelist ohoh ...'
                     
                 else:
                     pricelist_partnerinfo.create(cr, uid, pvals, context)
                     
                 #msg += 'Price list added \n'     
                
        return msg
        
    def get_category(self, cr, uid, name, context=None):
        categ = self.pool.get('product.category')
        to_search = [('name', '=', CATEGORIES.get(name, name))]
        categ_id = categ.search(cr, uid, to_search, context=context)
        return categ_id and categ_id[0] or 7 

    def get_product(self, cr, uid, categ_id, name, context=None):
        product = self.pool.get('product.product')
        product_ids = product.search(cr, uid, [('name', '=', name), ('categ_id', '=', categ_id)], context=context)
        if not product_ids:
            product_ids = self.get_match(cr, uid, product, name, [('categ_id', '=', categ_id)], context)
        if product_ids:
            product_id = product_ids[0]
        else:
            category = self.pool.get('product.category')
            categ = category.browse(cr, uid, categ_id)
            cname = categ.name == 'Miscellaneous' and 'misc' or categ.name.lower() 
            model = self.pool.get('product.' + cname)
            vals = {'name': name, 'categ_id': categ_id}
            model_id = model.create(cr, uid, vals, context)
            model_obj = model.browse(cr, uid, model_id, context)
            product_id = model_obj.product_id.id
        return product_id

    def get_partner(self, cr, uid, name, customer, context=None):
        partner = self.pool.get('res.partner')
        partner_ids = partner.search(cr, uid, [('name', '=', name)], context=context)
        if not partner_ids:
            partner_ids = self.get_match(cr, uid, partner, name, [], context)
            # TODO: preguntarle a Cesar si se puede hacer ['supplier', '=', False]
        if partner_ids:
            partner_id = partner_ids[0]
        else:
            vals = {
                'name': name,
                'customer': customer,
                'supplier': not customer
            }
            partner_id = partner.create(cr, uid, vals, context)
        return partner_id

    def get_option_value(self, cr, uid, name, code, context=None):
        ot = self.pool.get('option.type')
        ov = self.pool.get('option.value')

        ot_id = ot.search(cr, uid, [('code', '=', code)], context=context)[0]
        to_search = [('name', '=', name), ('option_type_id', '=', ot_id)]
        ov_ids = ov.search(cr, uid, to_search, context=context)
        if ov_ids:
            return ov_ids[0]
        else:
            to_create = {x[0]: x[2] for x in to_search}
            return ov.create(cr, uid, to_create, context)

    def get_match(self, cr, uid, model_object, name, restrictions, context=None):
       #model_object = self.pool.get(model)
       ids = model_object.search(cr, uid, restrictions, context=context)
       seq_list = [x.name for x in model_object.browse(cr, uid, ids, context=context)]
       seq_closer, ratio = stringmatcher.find_closers(seq_list, name)
       if seq_closer:
           return model_object.search(cr, uid, [('name', '=', seq_closer)], context=context)
       else:
           return None
             
    def get_date(self, value):
        try:
            d = BASE_DATE + int(value)
            return datetime.datetime.fromordinal(d)
        except:
            return datetime.datetime(2017, 1, 1)

    def get_float(self, value):
        try:
            return float(value)
        except:
            return 0.0
