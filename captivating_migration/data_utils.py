import stringmatcher
import datetime
import base64

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

class data_utils(object):
    
    def get_category(self, cr, uid, name, context=None):
        categ = self.pool.get('product.category')
        to_search = [('name', '=', CATEGORIES.get(name, name))]
        categ_id = categ.search(cr, uid, to_search, context=context)
        return categ_id and categ_id[0] or 7 

    def get_product(self, cr, uid, categ_id, name, display_warning, context=None):
        product = self.pool.get('product.product')
        product_ids = product.search(cr, uid, [('name', '=', name), ('categ_id', '=', categ_id)], context=context)
        ratio = None
        product_id = None
        if product_ids:
            product_id = product_ids[0]
        else:
            product_ids, r = self.get_match(cr, uid, product, name, [('categ_id', '=', categ_id)], context)
            if r == 1.0:
                product_id = product_ids[0]
            elif r > 0.8 and display_warning and product_ids:
                product_id = product_ids[0]
                ratio = r
            else:
                category = self.pool.get('product.category')
                categ = category.browse(cr, uid, categ_id)
                cname = categ.name == 'Miscellaneous' and 'misc' or categ.name.lower() 
                model = self.pool.get('product.' + cname)
                vals = {'name': name, 'categ_id': categ_id}
                model_id = model.create(cr, uid, vals, context)
                model_obj = model.browse(cr, uid, model_id, context)
                product_id = model_obj.product_id.id
        return product_id, ratio

    def get_partner(self, cr, uid, name, customer, display_warning, context=None):
        partner = self.pool.get('res.partner')
        partner_ids = partner.search(cr, uid, [('name', '=', name)], context=context)
        ratio = None
        partner_id = None
        if partner_ids:
            partner_id = partner_ids[0]
            ratio = 1.0
        else:
            partner_ids, r = self.get_match(cr, uid, partner, name, [('supplier', '=', not customer)], context)
            if r == 1.0:
                partner_id = partner_ids[0]
            elif r > 0.8 and display_warning:
                partner_id = partner_ids[0]
                ratio = r
            else:
                vals = {
                    'name': name,
                    'customer': customer,
                    'supplier': not customer
                }
                partner_id = partner.create(cr, uid, vals, context)
        return partner_id, ratio

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
           return model_object.search(cr, uid, [('name', '=', seq_closer)], context=context), ratio
       else:
           return None, None
             
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
