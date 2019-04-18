__author__ = 'yuriq'

import json

f = open('orders_orig.txt')
orders = json.load(f)
f.close()

# Fixing hotel names
HOTELS = {
    'PARQUE CENTRAL': 'IBEROSTAR PARQUE CENTRAL',
    'CASA PARTICULAR PLAYA LARGA - ERNESTO DELGADO Y YODAINES': 'CASA PARTICULAR PLAYA LARGA - CASA ERNESTO DELGADO',
    'CASA PARTICULAR SANTIAGO DE CUBA - CASA YULIET RAMOS': 'CASA PARTICULAR SANTIAGO DE CUBA - CASA YULIET',
    'CASA PARTICULAR TRINIDAD - DEBORAH Y JOSE': 'CASA PARTICULAR TRINIDAD - CASA DEBORAH Y JOSE',
    'CASA PARTICULAR SUPERIOR TRINIDAD - CASA REAL 54': 'CASA PARTICULAR TRINIDAD - CASA REAL 54',
    'CASA PARTICULAR HAVANA - SUPERIOR - CASA HOSTAL HAVANA 101': 'CASA PARTICULAR HAVANA - CASA HOSTAL HABANA 101',
    'CASA PARTICULAR CIENFUEGOS - VILLA MARIA': 'CASA PARTICULAR CIENFUEGOS - CASA VILLA MARIA',
    'SEVILLA': 'MERCURE SEVILLA',
    'NACIONAL': 'HOTEL NACIONAL DE CUBA',
    'PRINCESA DEL MAR': 'PARADISUS PRINCESA DEL MAR',
    'CASA PARTICULAR TRINIDAD - OSMARY ALBERTO': 'CASA PARTICULAR TRINIDAD - CASA OSMARY ALBERTO',
    'CASA PARTICULAR TRINIDAD - SUPERIOR - CASA PABLO Y VIVIAN': 'CASA PARTICULAR TRINIDAD - CASA PABLO Y VIVIAN',
    'CASA PARTICULAR TRINIDAD - BRISAS DE ALAMEDA': 'CASA PARTICULAR TRINIDAD - CASA BRISAS ALAMEDA',
    'CASA PARTICULAR HAVANA - SUPERIOR - HOSTAL HABANA 101': 'CASA PARTICULAR HAVANA - CASA HOSTAL HABANA 101',
    'CASA PARTICULAR TRINIDAD - SUPERIOR - CASA MARIA Y ENDDY': 'CASA PARTICULAR TRINIDAD - CASA MARIA Y ENDDY',
    'CASA PARTICULAR TRINIDAD - DELUXE - CASA MARIA Y ENDY': 'CASA PARTICULAR TRINIDAD - CASA MARIA Y ENDDY',
    'COSTA SUR': 'CLUB AMIGO COSTA SUR',
    'VALENCIA': 'HOSTAL VALENCIA',
    'VALENCIA': 'CASA PARTICULAR BARACOA - TERRAZA DE BARACOA',
    'CASA PARTICULAR TRINIDAD - HOSTAL LOLA': 'CASA PARTICULAR TRINIDAD - CASA LOLA',
    'VILLA YAGANABO': 'VILLA YAGUANABO',
    'CASA PARTICULAR HAVANA - DELUXE - SUENO CUBANO': 'CASA PARTICULAR HAVANA - HOSTAL SUENO CUBANO',
    'CASA PARTICULAR HAVANA - CASA VIEJA': 'CASA PARTICULAR HAVANA - HOSTAL CASA VIEJA',
    'CASA PARTICULAR HAVANA - BUENOS AIRES': 'CASA PARTICULAR HAVANA - CASA BUENOS AIRES',
    'CASA PARTICULAR SANTA CLARA - CASONA JOVER': 'CASA PARTICUAR SANTA CLARA - CASONA JOVER',
    'CASA PARTICUAR SANTIAGO - CASA MIRIAM': 'CASA PARTICULAR SANTIAGO DE CUBA - CASA MIRIAM',
    'CASA PARTICULAR TRINIDAD - SUPERIOR - CASA REAL 54': 'CASA PARTICULAR TRINIDAD - CASA REAL 54',
    'CASA PARTICULAT HAVANA - DELUXE - CASA VITRALES': 'CASA PARTICULAR HAVANA - CASA VITRALES',
    'CASA PARTICULAR HAVANA - VITRALES': 'CASA PARTICULAR HAVANA - CASA VITRALES',

}

# Others
OTHERS = {
	'CUBA REPRESENTATIVE SERVICE FEE': 'CUBA REPRESENTATION SERVICE FEE'} 
	
for o in orders:
    for ol in o['order_lines']:
        if ol['product_name'].upper() in HOTELS.keys():
            print "Correcting ", ol['product_name'], 'to ', HOTELS[ol['product_name']]
            ol['product_name'] = HOTELS[ol['product_name']]
        if ol['product_name'].upper() in OTHERS.keys():
            print "Correcting ", ol['product_name'], 'to ', OTHERS[ol['product_name']]
            ol['product_name'] = OTHERS[ol['product_name']]
            

# Fixing tourist cards
for o in orders:
    for ol in o['order_lines']:
        if ol['product_category'] == 'Tourist Card':
            ol['product_name'] = 'Tourist Card'
            ol['start_date'] = o['start_date']

# Fixing categories
CATEGORIES = {
    'Car hire': 'Car',
    'Car Hire': 'Car',
    'Rep Fee': 'Miscellaneous',
    'Cuba Representation Service Fee': 'Miscellaneous',
    'Extra': 'Miscellaneous',
    'Tour': 'Package',
    'tour': 'Package',
    'Cycling Tour': 'Package',
    'Casa': 'Hotel',
    'casa': 'Hotel',
    'Tourist Card': 'Miscellaneous',
    'Excursion': 'Activity'
}

for o in orders:
    for ol in o['order_lines']:
        if ol['product_category'] in CATEGORIES.keys():
            ol['product_category'] = CATEGORIES[ol['product_category']]
            
PARTNERS = {
	'Direct Customer Eur': 'DESTINATION CUBA'
}

for o in orders:
	if o['client'] in PARTNERS.keys():
		print "Correcting ", o['client'], 'to ', PARTNERS[o['client']]
		o['client'] = PARTNERS[o['client']]


f = open('orders_mod.txt', 'w+')
json.dump(orders, f)
f.close()
