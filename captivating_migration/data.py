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

BASE_DATE = 693594
ROOM = {'simple': 1, 'double': 2, 'triple': 3}


class import_data(data_utils, TransientModel):
    _name = 'import.data'
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
        msg = ''
        if obj.file:
            data = base64.decodestring(obj.file)
            #try:
            document = xlrd.open_workbook(file_contents=data)
            for y in ['2014', '2015']:
                sheet = document.sheet_by_name(y)
                msg += self.import_sales_data(cr, uid, sheet, data, display_warning, context) + '\n'
            #except:
            #    raise osv.except_osv('Error!', 'The file is not valid.')

            self.write(cr, uid, obj.id, {'result': msg}, context)
            return {
                'name': 'Import Operations',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'import.data',
                'res_id': obj.id,
                'target': 'new',
                'context': context,
            }
        else:
            raise osv.except_osv('Error!', 'You must select a file.')

    def import_sales_data(self, cr, uid, sheet, data, display_warning, context=None):
        order = self.pool.get('sale.order')
        order_line = self.pool.get('sale.order.line')
        product_product = self.pool.get('product.product')
        supplier = self.pool.get('res.partner')

        msg = ''

        head = {sheet.cell_value(0, x): x for x in range(sheet.ncols)}
        order_id = False
        warning = False
        for r in range(1, sheet.nrows):

            def cell(attr):
                if sheet.cell(r, head[attr]).ctype == xlrd.XL_CELL_ERROR:
                    return None
                return sheet.cell_value(r, head[attr])

            if cell('REQUEST DATE'):
                partner_id, ratio = self.get_partner(cr, uid, cell('COMPANY NAME'), True, display_warning, context)                   
                if ratio:
                    supplier_warning = supplier.browse(cr, uid, supplier_id, context)
                    msg += "WARNING: " + cell('COMPANY NAME') + " is " + supplier_warning.name + "? " + str(ratio) + '\n'
                    partner_id = None    
                else:
                    order_vals = {
                        'partner_id': partner_id,
                        'partner_invoice_id': partner_id,
                        'partner_shipping_id': partner_id,
                        'client_order_ref': cell('DC REF NUMBER'),
                        'date_order': self.get_date(cell('START DATE')),
                        'end_date': self.get_date(cell('START DATE')),
                        'pricelist_id': 1
                    }
                    order_id = order.create(cr, uid, order_vals, context)
                    print ("Created order " + cell('DC REF NUMBER'))

            if cell('CLIENT NAME'):
                pax_name = str(cell('CLIENT NAME')) + ' ' + str(cell('CLIENT SURNAME'))
                pax_id = self.get_pax(cr, uid, pax_name, context)
                if order_id:
                    order.write(cr, uid, order_id, {'pax_ids': [(4, pax_id)]}, context)
                print ("    Added pax " + pax_name)

            if cell('SERVICE TYPE'):
                category_id = self.get_category(cr, uid, cell("SERVICE TYPE"), context)
                product_id, product_ratio = self.get_product(cr, uid, category_id, cell("SERVICE NAME"), display_warning)
                supplier_id, supplier_ratio = self.get_partner(cr, uid, cell('SUPPLIER NAME'), False, display_warning, context)   
                
                if (product_ratio and cell("SERVICE TYPE") == 'Hotel') or supplier_ratio:
                    if product_ratio:
                        product_warning = product_product.browse(cr, uid, product_id, context)
                        msg += "WARNING: " + cell("SERVICE NAME") + " is " + product_warning.name + "? " + str(product_ratio) + '\n'
                        product_id = None                                     
                    if supplier_ratio:
                        supplier_warning = supplier.browse(cr, uid, supplier_id, context)
                        msg += "WARNING: " + cell('SUPPLIER NAME') + " is " + supplier_warning.name + "? " + str(ratio) + '\n'
                        partner_id = None                 
                else:    
                
                    order_line_vals = {
                       'order_id': order_id,
                       'category_id': category_id,
                       'product_id': product_id,
                       'name': cell("SERVICE NAME"),
                       'description': cell("SERVICE NAME"),
                       'start_date': self.get_date(cell("START DATE")),
                       'end_date': self.get_date(cell("END DATE")),
                       'supplier_id': supplier_id,
                       'price_unit': self.get_float(cell("SERVICE INVOICED PRICE")),
                       'price_unit_cost': self.get_float(cell("SERVICE NET PRICE")), # TODO: este precio puede estar en otra moneda
                       'reservation_number': cell("CONFIRM. NUMBER")
                    }
                        
                    if cell('MEAL PLAN'):
                        mp = self.get_option_value(cr, uid, cell('MEAL PLAN'), 'mp', context)
                        order_line_vals['hotel_2_meal_plan_id'] = mp
                    if cell('ROOM TYPE'):
                        # TODO: falta tener en cuenta el caso de los ninnos
                        occuppation = []
                        rooms = cell('ROOM TYPE').split(' & ')
                        for r in rooms:
                            d = {}
                            attrs = r.split(' ')
                            try:
                                d['quantity'] = int(attrs.pop(0))
                            except:
                                continue
                            if attrs[0] in ['Single', 'Double', 'Triple']:
                                room = attrs.pop(0).lower()
                                d['room'] = room == 'single' and 'simple' or room
                                d['adults'] = ROOM[d['room']]
                            else:
                                d['room'] = 'double'
                                d['adults'] = 2
                            if '+' in attrs:
                                continue
                            if attrs:
                                room_type = ' '.join(attrs)
                                rt = self.get_option_value(cr, uid, room_type, 'rt', context)
                                d['room_type_id'] = rt
                            occuppation.append((0, 0, d))
                        order_line_vals['hotel_1_rooming_ids'] = occuppation
                    order_line.create(cr, uid, order_line_vals, context)
                    #print ("    Added line " + str(cell('SERVICE NAME')))
        return msg

    def get_pax(self, cr, uid, name, context=None):
        partner = self.pool.get('res.partner')
        to_search = [('name', '=', name), ('pax', '=', True)]
        pax_id = partner.search(cr, uid, to_search, context=context)
        if pax_id:
            pax_id = pax_id[0]
        else:
            vals = {x[0]: x[2] for x in to_search}
            pax_id = partner.create(cr, uid, vals, context)
        return pax_id
