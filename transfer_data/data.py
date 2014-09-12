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
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields, osv
from openerp.osv.orm import TransientModel
import base64
import datetime
import xlrd

DATETIME_FORMAT = "%Y-%m-%d"
HOTEL_TYPES = {
    'Ciudad': 'city', 'Playa': 'beach', 'Cayos': 'beach', 'Rural': 'nature'
}
CAR_DAYS = {
    7: '3-6 Days', 8: '7-13 Days', 9: '14-29 Days'
}
TRANSMISSION = {
    'Mecánica': 'Mechanic', 'Automática': 'Automatic'
}
INCLUDE = 'Incluido'
CP = 'CP (Continental Plan)'
MAP = 'MAP (Modified American Plan)'
AP = 'AP (American Plan)'
AI = 'All Inclusive'
HOTEL_FIEDLS = ['suppinfo_id', 'room_type_id', 'meal_plan_id']
PROGRAM_FIEDLS = ['suppinfo_id', 'room_type_id', 'meal_plan_id', 'min_pax', 'max_pax']
TRANSFER_FIELDS = ['suppinfo_id', 'vehicle_type_id', 'guide_id']
CAR_FIELDS = ['suppinfo_id', 'transmission_id', 'days_id']
BASE_DATE = 693594
STD_SUPPLIER = 'Cubanacan'


class transfer_data(TransientModel):
    _name = 'transfer.data'
    _columns = {
        'product':
            fields.selection([('transfer', 'Transfer')], 'Product'),
        'extended':
            fields.boolean('Extended'),
        'file':
            fields.binary('File'),
        'sheet':
            fields.integer('Sheet'),
        'difference':
            fields.float('Difference'),
        'result':
            fields.text('Result')
    }

    _defaults = {
        'difference': 0.0
    }

    def import_file(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids[0], context)
        if obj.file:
            origin = base64.decodestring(obj.file)
            try:
                data = self.read_from_calc(origin, obj.sheet)
            except:
                raise osv.except_osv('Error!', 'The file is not valid.')
            method = 'load_' + obj.product
            if obj.extended:
                method += '_extended'
            res = getattr(self, method)(cr, uid, data, context)
            if res:
                msg = 'Products not found: \n'
                msg += str(res).replace(',', '\n')
            else:
                msg = 'The operation was successful.'
            self.write(cr, uid, obj.id, {'result': msg}, context)
            return {
                'name': 'Import Products',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'transfer.data',
                'res_id': obj.id,
                'target': 'new',
                'context': context,
            }
        else:
            raise osv.except_osv('Error!', 'You must select a file.')

    def read_from_calc(self, data, sheet, context=None):
        document = xlrd.open_workbook(file_contents=data)
        data = document.sheet_by_index(sheet)
        return data

    def get_id_by_name(self, cr, uid, model, name, context=None):
        context = context or {}
        obj = self.pool.get(model)
        obj_id = obj.search(cr, uid, [('name', '=', name)], context=context)
        if not obj_id and context.get('create', False):
            vals = {'name': name}
            if context.get('values', False):
                vals.update(context['values'])
            obj_id = [obj.create(cr, uid, vals, context)]
        return obj_id and obj_id[0] or False

    def get_categ_id(self, cr, uid, categ, context=None):
        product = self.pool.get('product.product')
        ctx = context.copy()
        ctx.update({'product_type': categ})
        return product._get_category(cr, uid, ctx)

    def get_value(self, value):
        try:
            return float(value)
        except:
            return False

    def get_date(self, value):
        d = BASE_DATE + int(value)
        return datetime.datetime.fromordinal(d)

    def find_by_code(self, cr, uid, code, model, context=None):
        obj = self.pool.get(model)
        val = obj.search(cr, uid, [('code', '=', code)], context=context)[0]
        return val

    ''' Transfers '''

    def load_transfer(self, cr, uid, data, context=None):
        product_transfer = self.pool.get('product.transfer')
        product_supplierinfo = self.pool.get('product.supplierinfo')
        pricelist_partnerinfo = self.pool.get('pricelist.partnerinfo')
        not_found = []

        dict_options = self.prepare_load(cr, uid, context)
        for d in range(6, data.nrows):
            name = (data.cell_value(d, 0) + ' - ' + data.cell_value(d, 1)).encode('UTF-8')
            transfer_ids = product_transfer.search(cr, uid, [('name', 'in', [name, name + ''])], context=context)
            if transfer_ids:
                transfer = product_transfer.browse(cr, uid, transfer_ids[0], context)
                seller_ids = [s.id for s in transfer.seller_ids]
                if seller_ids:
                    product_supplierinfo.unlink(cr, uid, seller_ids, context)
                svals = {
                    'name': self.get_id_by_name(cr, uid, 'res.partner', STD_SUPPLIER, context),
                    'product_id': transfer.product_id.product_tmpl_id.id,
                    'min_qty': 0
                }
                suppinfo_id = product_supplierinfo.create(cr, uid, svals, context)
                for k, v in dict_options.iteritems():
                    price = float(data.cell_value(d, k))
                    pvals = {
                        'start_date': datetime.datetime(2013, 11, 1),
                        'end_date': datetime.datetime(2014, 10, 31),
                        'price': price,
                        'min_quantity': 0,
                        'suppinfo_id': suppinfo_id
                    }
                    pvals.update(v)
                    pricelist_partnerinfo.create(cr, uid, pvals, context)
            else:
                not_found.append(name)
        return not_found

    def prepare_load(self, cr, uid, context):
        model = 'option.value'
        taxi = self.find_by_code(cr, uid, 'tx', model, context)
        microbus = self.find_by_code(cr, uid, 'mc', model, context)
        minibus = self.find_by_code(cr, uid, 'mn', model, context)
        omnibus = self.find_by_code(cr, uid, 'om', model, context)
        one = self.find_by_code(cr, uid, '1-2', model, context)
        three = self.find_by_code(cr, uid, '3-5', model, context)
        six = self.find_by_code(cr, uid, '6-8', model, context)
        nine = self.find_by_code(cr, uid, '9-12', model, context)
        one_three = self.find_by_code(cr, uid, '13-20', model, context)
        two_one = self.find_by_code(cr, uid, '21-30', model, context)
        three_one = self.find_by_code(cr, uid, '31-43', model, context)
        with_guide = self.find_by_code(cr, uid, 'wig', model, context)
        without_guide = self.find_by_code(cr, uid, 'wog', model, context)

        dict_options = {
            3: {'vehicle_type_id': taxi, 'vehicle_capacity_id': one, 'guide_id': without_guide},
            #4:
            5: {'vehicle_type_id': taxi, 'vehicle_capacity_id': one, 'guide_id': with_guide},
            #6:
            7: {'vehicle_type_id': microbus, 'vehicle_capacity_id': three, 'guide_id': without_guide},
            8: {'vehicle_type_id': microbus, 'vehicle_capacity_id': six, 'guide_id': without_guide},
            9: {'vehicle_type_id': microbus, 'vehicle_capacity_id': three, 'guide_id': with_guide},
            10: {'vehicle_type_id': microbus, 'vehicle_capacity_id': six, 'guide_id': with_guide},
            11: {'vehicle_type_id': minibus, 'vehicle_capacity_id': nine, 'guide_id': with_guide},
            12: {'vehicle_type_id': minibus, 'vehicle_capacity_id': one_three, 'guide_id': with_guide},
            13: {'vehicle_type_id': omnibus, 'vehicle_capacity_id': two_one, 'guide_id': with_guide},
            14: {'vehicle_type_id': omnibus, 'vehicle_capacity_id': three_one, 'guide_id': with_guide}
        }
        return dict_options
