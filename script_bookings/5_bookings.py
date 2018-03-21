# -*- encoding: utf-8 -*-
__author__ = 'yuriq'

import datetime, erppeek, json


BASE_DATE = 693594

f = open('orders_mod.txt')
orders = json.load(f)
f.close()

# Importing to openerp
### server
host = 'http://178.62.38.154:8079'
db = 'captivatingcuba_comelytravel_com'

###local
# host = 'http://localhost:8069'
# db = 'captivating'

login = 'admin'
passwd = '5t4nd4rd'

conn = erppeek.Client(host, db, login, passwd)

def model_search(model, field, value):
    ids = model.search([(field, '=ilike', value)])
    if len(ids) == 0:
        print 'Warning: value not found - ', field, value
        return None
    elif len(ids) > 1:
        print 'Warning: ambiguous value', field, value
        return None
    return ids[0]

def get_order_end_date(o):
    max_d = o['order_lines'][0]['end_date']
    for ol in o['order_lines']:
        if ol['end_date'] > max_d:
            max_d = ol['end_date']
    return max_d

def get_product_category(category):
    if category == 'Miscellaneous':
        category = 'misc'
    return conn.model('product.'+category.lower())

def get_category(category):
    if category == 'Miscellaneous':
        category = 'misc'
    return category.lower()

def get_cost_price():
    return 0.0

def get_sale_price():
    return 0.0

order_model = conn.model('sale.order')
order_line_model = conn.model('sale.order.line')
partner_model = conn.model('res.partner')
category_model = conn.model('product.category')
supplier_model = conn.model('res.partner')

for order in orders:
    partner_id = partner_model.search([('name', '=ilike', order['client'].upper())])

    if not partner_id:
        vals = {
        'name': order['client'].upper(),
        'customer': True,
        'supplier': False}
        partner_id = partner_model.create(vals).id
    else:
        partner_id = partner_id[0]

    # Check if the order already exists
    order_ids = order_model.search([('client_order_ref', '=ilike', order['reference'])])
    if order_ids:
        print 'Warning: order already in the system ', order['reference']
        continue

    pax_ids = []
    for pax in order['paxs']:
        pax_id = model_search(partner_model, 'name', pax)
        if not pax_id:
            pax_id = partner_model.create({'name': pax}).id
        pax_ids.append(pax_id)

    partner_obj = partner_model.browse(partner_id)
    pricelist_id = partner_obj.property_product_pricelist.id

    order_vals = {
        'partner_id': partner_id,
        'partner_invoice_id': partner_id,
        'partner_shipping_id': partner_id,
        'client_order_ref': order['reference'],
        'date_order': order['start_date'],
        'end_date': get_order_end_date(order),
        'pax_ids': [(6, 0, (pax_ids))],
        'pricelist_id': pricelist_id,
        'note': order['comments']
    }

    order_id = order_model.create(order_vals).id
    print 'Order created: ', order['reference']

    res_price = {}

    for ol in order['order_lines']:

        category_id = model_search(category_model, 'name', ol['product_category'])
        if not category_id:
            print 'Warning: Category not found  ', ' - ', ol['product_category'], ' - ', order['reference'], ' - ', ol['product_name']
            continue

        product_category_model = get_product_category(ol['product_category'])
        product_id = model_search(product_category_model, 'name', ol['product_name'].upper())
        if not product_id:
            try:
                product_id = product_category_model.create({'name': ol['product_name'].upper(), 'categ_id': category_id}).id
            except :
                parent_product_id = conn.model('product.product').create({'name': ol['product_name'], 'categ_id': category_id}).id
                product_id = product_category_model.create({'name': ol['product_name'], 'categ_id': category_id, 'product_id': parent_product_id}).id
            print 'Product Created ', ' - ', ol['product_category'], ' - ', ol['product_name']

        product_obj = product_category_model.browse(product_id)
        supplier_ids = product_obj.seller_ids
        if len(supplier_ids) > 1:
            print 'Multiple suppliers for: ', ol['product_name']
            continue
        elif len(supplier_ids) == 1:
            supplier_id = supplier_ids[0].name.id
        else:
            supplier_id = model_search(supplier_model, 'name', ol['supplier'])

        # price vals
        order_obj = order_model.browse(order_id)
        pricelist = pricelist_id or False
        product = product_obj.product_id.id or False
        qty = 1
        uom = product_obj.product_id.uom_id.id or False
        qty_uos = 1
        uos = False
        name = product_obj.product_id.name or ''
        partner_id = partner_id or False
        date_order = ol['start_date'] or False
        end_date_order = ol['end_date'] or False
        fiscal_position = False
        lang = False
        update_tax = True
        packaging = False
        flag = False
        category = get_category(ol['product_category'])
        adults = len(pax_ids)
        price, cost_price, currency_cost_id = order_line_model.product_price(pricelist, product, qty, uom, qty_uos, uos,
                                                                             name, partner_id, supplier_id, lang,
                                                                             update_tax, date_order, packaging,
                                                                             fiscal_position, flag,
                                                                             category, end_date_order, adults)
        price_unit = price or 1.0
        price_unit_cost = cost_price or 1.0

        order_line_vals = {
           'order_id': order_id,
           'category_id': category_id,
           'product_id': product_obj.product_id,
           'name': ol['product_name'],
           'description': ol['product_category'] + ' ' + ol['product_name'],
           'start_date': ol['start_date'],
           'end_date': ol['end_date'],
           'supplier_id': supplier_id,
           'price_unit': price_unit,
           'price_unit_cost': price_unit_cost,
           'currency_cost_id': currency_cost_id,
           'reservation_number': ol['confirmation'],
           'category': category,
           'product_uos_qty': 1,
           'adults': adults
        }
        
        order_line_model.create(order_line_vals)
        print "  Order line created: ", ol['product_category'], ' ', ol['product_name']

print 'Done!'
