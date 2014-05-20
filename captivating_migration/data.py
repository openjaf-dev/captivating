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
    'Casa': 'Hotel'
}


class import_data(TransientModel):
    _name = 'import.data'
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
            document = xlrd.open_workbook(file_contents=data)
            for y in ['2014', '2015']:
                sheet = document.sheet_by_name(y)
                self.import_sales_data(cr, uid, sheet, data, context)
            #except:
            #    raise osv.except_osv('Error!', 'The file is not valid.')
            msg = ' '
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

    def import_sales_data(self, cr, uid, sheet, data, context=None):
        order = self.pool.get('sale.order')
        order_line = self.pool.get('sale.order.line')

        head = {sheet.cell_value(0, x): x for x in range(sheet.ncols)}
        order_id = False
        for r in range(1, sheet.nrows):

            def cell(attr):
                return sheet.cell_value(r, head[attr])

            if cell('REQUEST DATE'):
                partner_id = self.get_partner(cr, uid, cell('COMPANY NAME'), True, context)
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
                order.write(cr, uid, order_id, {'pax_ids': [(4, pax_id)]}, context)
                print ("    Added pax " + pax_name)

            if cell('SERVICE TYPE'):
                category_id = self.get_category(cr, uid, cell("SERVICE TYPE"), context)
                product_id = self.get_product(cr, uid, category_id, cell("SERVICE NAME"))
                supplier_id = self.get_partner(cr, uid, cell('SUPPLIER NAME'), False, context)
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
                   'reservation_number': cell("CONFIRM. NUMBER")
                }
                if cell('MEAL PLAN'):
                    mp = self.get_option_value(cr, uid, cell('MEAL PLAN'), 'mp', context)
                    order_line_vals['hotel_2_meal_plan_id'] = mp
                order_line.create(cr, uid, order_line_vals, context)
                print ("    Added line " + cell("SERVICE NAME"))
        return True

    def get_category(self, cr, uid, name, context=None):
        categ = self.pool.get('product.category')
        to_search = [('name', '=', CATEGORIES.get(name, name))]
        categ_id = categ.search(cr, uid, to_search, context=context)
        return categ_id and categ_id[0] or 7

    def get_product(self, cr, uid, categ_id, name, context=None):
        product = self.pool.get('product.product')
        product_id = product.search(cr, uid, [('name', '=', name)],
                                    context=context)
        if product_id:
            product_id = product_id[0]
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
        to_search = [('name', '=', name), ('customer', '=', customer), ('supplier', '=', not customer)]
        partner_id = partner.search(cr, uid, to_search, context=context)
        if partner_id:
            partner_id = partner_id[0]
        else:
            vals = {x[0]: x[2] for x in to_search}
            partner_id = partner.create(cr, uid, vals, context)
        return partner_id

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

    def get_option_value(self, cr, uid, name, code, context=None):
        ov = self.pool.get('option.value')
        to_search = [('name', '=', name), ('option_type_id.code', '=', code)]
        ov_ids = ov.search(cr, uid, to_search, context=context)
        return ov_ids and ov_ids[0] or False

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
