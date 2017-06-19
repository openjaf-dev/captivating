__author__ = 'yuriq'

import erppeek

host = 'http://localhost:8069'
db = 'captivating'
login = 'admin'
passwd = '5t4nd4rd'

#host = 'https://captivatingcuba.comelytravel.com'
#db = 'captivatingcuba_comelytravel_com'
#login = 'admin'
#passwd = '5t4nd4rd'

conn = erppeek.Client(host, db, login, passwd)

new_name = 'MEMORIES JIBACOA'
old_name = 'BREEZES JIBACOA'
hotel_model = conn.model('product.hotel')
product_model = conn.model('product.product')
partner_model = conn.model('res.partner')

hotel_id = hotel_model.search([('name', '=ilike', old_name)])

if hotel_id:
    print 'Hotel found', old_name
    product_id = hotel_model.browse(hotel_id).product_id.id
    product_model.write(product_id, {'name': new_name})
    hotel_model.write(hotel_id, {'name': new_name})
    partner_id = partner_model.search([('name', '=ilike', old_name)])
    partner_model.write(partner_id, {'name': new_name})



#partner_model = conn.model('res.partner')

#clients = ['CHARTER TRAVEL']
#for c in clients:
#    ids = partner_model.search([('name', '=ilike', c)])
#    if ids == []:
#        vals = {
#            'name': c,
#            'customer': True,
#            'supplier': False
#        }
#        partner_model.create(vals)
#    else:
#        print 'Client found!: ', c
#
#
suppliers = ['PALACIO TAXI']
for s in suppliers:
    ids = partner_model.search([('name', '=ilike', s)])
    if ids == []:
        vals = {
            'name': s,
            'customer': False,
            'supplier': True
        }
        partner_model.create(vals)
    else:
        print 'Client found!: ', s