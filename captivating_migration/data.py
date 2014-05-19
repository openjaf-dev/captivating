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
            try:
                document = xlrd.open_workbook(file_contents=data)
                for y in ['2014', '2015']:
                    sheet = document.sheet_by_name(y)
                    self.import_sales_data(cr, uid, sheet, data, context)
            except:
                raise osv.except_osv('Error!', 'The file is not valid.')
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
        partner = self.pool.get('res.partner')
        order = self.pool.get('sale.order')
        order_line = self.pool.get('sale.order.line')
        category = self.pool.get('product.category')

        head = {sheet.cell_value(0, x): x  for x in range(sheet.ncols)}
        order_id = False
        for r in range(1, sheet.nrows):

            def cell(attr):
                return sheet.cell_value(r, head[attr])

            if cell('REQUEST DATE'):
                partner_id = partner.search(cr, uid, [('name', '=', cell('COMPANY NAME'))], context=context)
                order_vals = {
                    #'name': cell['DC REF NUMBER']),
                    'partner_id': partner_id and partner_id[0] or 1,
                    'partner_invoice_id': partner_id and partner_id[0] or 1,
                    'partner_shipping_id': partner_id and partner_id[0] or 1,
                    'client_order_ref': cell('DC REF NUMBER'),
                    #'client_order_ref': cell['CLIENT NAME']) + ' ' + cell['CLIENT SURNAME']),
                    'date_order': self.get_date(cell('START DATE')),
                    'end_date': self.get_date(cell('START DATE')),
                    'pricelist_id': 1
                }
                order_id = order.create(cr, uid, order_vals, context)
                print ("Created order " + cell('DC REF NUMBER'))

            if cell('SERVICE TYPE'):
                category_id = category.search(cr, uid, [('name', '=', cell("SERVICE TYPE"))])
                supplier_id = partner.search(cr, uid, [('name', '=', cell("SUPPLIER NAME"))])
                order_line_vals = {
                   'order_id': order_id,
                   'category_id': category_id and category_id[0] or False,
                   'name': cell("SERVICE NAME"),
                   'description': cell("SERVICE NAME"),
                   'start_date': self.get_date(cell("START DATE")),
                   'end_date': self.get_date(cell("END DATE")),
                   'supplier_id': supplier_id and supplier_id[0] or 1,
                   'price_unit': self.get_float(cell("SERVICE INVOICED PRICE")),
                   'reservation_number': cell("CONFIRM. NUMBER")
                }
                order_line.create(cr, uid, order_line_vals, context)
        return True

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
