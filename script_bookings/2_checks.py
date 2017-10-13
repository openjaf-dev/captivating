__author__ = 'yuriq'

import erppeek, json

f = open('orders_orig.txt')
orders = json.load(f)
f.close()

# Importing to openerp

### local
#host = 'http://localhost:8069'
#db = 'captivating'

### server
host = 'http://178.62.38.154:8079'
db = 'captivatingcuba_comelytravel_com'


#host = 'http://95.211.225.143:8069'

login = 'admin'
passwd = '5t4nd4rd'

conn = erppeek.Client(host, db, login, passwd)

def model_search(model, field, value):
    return model.search([(field, '=ilike', value)])

def check_uniqueness(ids):
    if len(ids) == 0:
        return 'Not found'
    elif len(ids) > 1:
        return 'Ambiguous'
    else:
        return 'Found'

#Checking clients

print "Checking Clients"
clients = set()
for o in orders:
    clients.add(o['client'].upper())

partner_model = conn.model('res.partner')
for s in clients:
    ids = model_search(partner_model, 'name', s)
    uniqueness = check_uniqueness(ids)
    if uniqueness == 'Not found':
        print '  ', s, ': ', uniqueness

# Checking Categories

print "Checking Categories"
categories = set()
for o in orders:
    for ol in o['order_lines']:
        categories.add(ol['product_category'])

product_category_model = conn.model('product.category')
for c in categories:
    ids = model_search(product_category_model, 'name', c)
    uniqueness = check_uniqueness(ids)
    if uniqueness == 'Not found':
        print '  ', c, ': ', uniqueness

# Checking Suppliers

print "Checking Suppliers"
suppliers = set()
for o in orders:
    for ol in o['order_lines']:
        suppliers.add(ol['supplier'].upper())

partner_model = conn.model('res.partner')
for s in suppliers:
    ids = model_search(partner_model, 'name', s)
    uniqueness = check_uniqueness(ids)
    if uniqueness == 'Not found':
        print '  ', s, ': ', uniqueness


# Checking Products

print "Checking Products"
products = {}
for o in orders:
    for ol in o['order_lines']:
        if products.has_key(ol['product_category']):
            products[ol['product_category']].add(ol['product_name'].upper())
        else:
            products[ol['product_category']] = set()


product_model = conn.model('product.product')
for category in products.keys():
    for p in products[category]:
        ids = model_search(product_model, 'name', p)
        uniqueness = check_uniqueness(ids)
        if uniqueness == 'Not found':
            print '    ', category, ' ', p, ' ', uniqueness

# Checking Paxs duplicates within an order

for o in orders:
	p_set = set(o['paxs'])
	if len(p_set) != len(o['paxs']):
		duplicates = [p for p in o['paxs'] if o['paxs'].count(p) > 1]
		print 'Error: duplicate names', o['reference'], duplicates

