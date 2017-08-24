# -*- coding: utf-8 -*-
import xlrd, xlwt, sys, os
import xlutils.copy
from xlwt import *
import erppeek

file_name = 'files/hotels-2017-2018-USD.xls'

book = xlrd.open_workbook(file_name)
print "Loaded file: ", file_name

#updates sheet
updates = {}
dates = {}

style = xlwt.XFStyle()
style.num_format_str = 'M/D/YYYY'

host = 'http://localhost:8069'
db = 'cap(26-06-2017)'
login = 'admin'
passwd = '5t4nd4rd'

#host = 'http://95.211.225.143:8069'
#db = 'captivatingcuba_comelytravel_com'
#login = 'admin'
#passwd = '5t4nd4rd'

print "Connecting to {} ...".format(host)
conn = erppeek.Client(host, db, login, passwd)
print "Connected!"
hotel_model = conn.model('product.hotel')
hotel_set = set()
#for hotel in hotel_model.browse([]):
#    hotel_set.add(hotel.name)
#    print "Hotel added!", hotel.name

print "Reading hotel list ..."
hotel_res = conn.read('product.hotel', [], ['name'])
for res in hotel_res:
	hotel_set.add(res['name'])
print "Hotel set created!"

hotel_fixes = {
	'CABO SAN ANTONIO': 'VILLA GAVIOTA CABO SAN ANTONIO',
	'MARIA LA GORDA': 'MARIA LA GORDA (CIB)',
	'SAN DIEGO DE LOS BAÑOS': 'MIRADOR DE SAN DIEGO',
	'NACIONAL':'HOTEL NACIONAL DE CUBA',
	'NH CAPRI':'CAPRI',
	'PRESIDENTE':'ROC PRESIDENTE',
	'RIVIERA':'HABANA RIVIERA',
	'ST JOHNS':'SAINT JOHNS',
	'CLUB ACUARIO':'ACUARIO',
	'COMODORO': 'HOTEL COMODORO',
	'MEMORIES MIRAMAR': 'MEMORIES MIRAMAR HAVANA',
	'PANORAMA':'H10 HABANA PANORAMA',
	'QUINTA AVENIDA':'QUINTA AVENIDA HABANA',
	"O'FARRILL": 'PALACIO OFARRIL',
	'PALACIO MARQUES DE PRADO AMENO': 'MARQUES DE PRADO AMENO',
	'PALACIO MARQUES DE SAN FELIPE Y SANTIAGO DE BEJUCAL': 'PALACIO MARQUES DE SAN FELIPE',
	'PARQUE CENTRAL': 'IBEROSTAR PARQUE CENTRAL',
	'SEVILLA': 'MERCURE SEVILLA',
	'VALENCIA': 'HOSTAL VALENCIA',
	'TELEGRAPHO':'TELEGRAFO',
	'AGUAS AZULES': 'CLUB AMIGO AGUAS AZULES',
	'ARENAS BLANCAS':'BARCELO ARENAS BLANCAS',
	'ARENAS DORADAS':'ROC ARENAS DORADAS',
	'BARLOVENTO':'ROC BARLOVENTO',
	'BE LIVE VARADERO':'BE LIVE EXPERIENCE VARADERO',
	'INTERNACIONAL':'INTERNACIONAL VARADERO',
	'KAREY': 'CLUB KAREY',
	'KAWAMA': 'KAWAMA HOTEL & VILLAS',
	'MELIA PENINSULA': 'MELIA PENINSULA VARADERO',
	'PRINCESA DEL MAR': 'PARADISUS PRINCESA DEL MAR',
	'PUNTARENAS':'PUNTARENA',
	'SOL SIRENAS CORAL':'SOL SIRENAS - CORAL',
	'DON PEDRO':'BATEY DON PEDRO',
	'GUAMA':'VILLA GUAMA',
	'HOSTAL EL RIJO':'HOSTAL DEL RIJO',
	'ANCON':'CLUB AMIGO ANCON',
	'BRISAS TRINIDAD': 'BRISAS TRINIDAD DEL MAR',
	'COSTA SUR': 'CLUB AMIGO COSTA SUR',
	'FINCA MARIA DOLORES':'FINCA MA. DOLORES',
	'YAGUANABO':'VILLA YAGUANABO',
	'LA GRANJITA': 'VILLA LA GRANJITA',
	'PINARES DE MAYARI':'VILLA PINARES DE MAYARI',
	'CLUB AMIGO ATLANTICO GUARDALAVACA': 'CLUB AMIGO ATLANTICO-GUARDALAVACA',
	'SOL RIO LUNA MARES': 'SOL RIO DE LUNA Y MARES',
	'CASAGRANDA':'HOTEL CASA GRANDA',
	'EL SALTON': 'VILLA EL SALTON',
	'GRAN PIEDRA':'LA GRAN PIEDRA',
	'REX': 'HOTEL REX',
	'SIERRA MAR LOS GALEONES':'BRISAS SIERRA MAR - LOS GALEONES',
	'IMPERIAL':'HOTEL ENCANTO IMPERIAL',
	'VILLA GAVIOTA':'VILLA GAVIOTA SANTIAGO DE CUBA',
	'ROYALTON': 'ROYALTON BAYAMO',
	'MAREA DEL PORTILLO':'CLUB AMIGO MAREA DEL PORTILLO',
	'HOSTAL LA HABANERA':'LA HABANERA',
	'HOSTAL LA RUSA':'LA RUSA',
	'BLAU COLONIAL': 'COLONIAL CAYO COCO',
	'PLAYA CAYO COCO': 'PLAYA COCO',
	'DHAWA': 'HOTEL DHAWA CAYO SANTA MARIA',
	'MEMORIES PARAISO': 'MEMORIES PARAISO AZUL',
	'COLONY':'CIB EL COLONY',
	'CAMAGUEY':'GRAN HOTEL CAMAGUEY',
	'PLAYA BLANCA':'IBEROSTAR PLAYA BLANCA',

}

for hotel in hotel_fixes.keys():
    if hotel not in hotel_set:
        print 'Hotel not found', hotel

class Row:
    def __init__(self, idx):
        self.idx = idx
        self.name = ''
        self.supplier = ''
        self.init_date = ''
        self.end_date = ''
        self.price = 0

    def __str__(self):
        return "{0} - {1} - {2} - {3} - {4}".format(self.idx, self.name, self.supplier, self.init_date, self.end_date)

class Sheet:
    def __init__(self, idx):
        self.idx = idx
        self.rows = []

    def __str__(self):
        return "{0} - {1}".format(self.idx, len(self.rows))

col_name_idx = 0
col_supplier_idx = 1
col_init_date_idx = 4
col_end_date_idx = 5
col_price = 7

sheets = []

print "Reading values ..."
for sheet_idx in range(0, len(book.sheets())):
    sheet = book.sheet_by_index(sheet_idx)
    sheet_obj = Sheet(sheet_idx)
    use_sheet = False
    for row in range(1, sheet.nrows):
        used_row = False
        row_obj = Row(row)
        if sheet.cell(row, col_name_idx).ctype == 1:
            used_row = True
            use_sheet = True
            try:
                row_obj.name = sheet.cell(row, col_name_idx).value.strip().encode('utf8')
            except AttributeError:
                row_obj.name = str(sheet.cell(row, col_name_idx).value.strip())

            if sheet.cell(row, col_supplier_idx).ctype != 1:
                row_obj.supplier = ''
            else:
                row_obj.supplier = sheet.cell(row, col_supplier_idx).value.strip().encode('utf8')

            # if sheet.cell(row, 1).value in ['DC', '']:
            #     updates[sheet_idx] = updates.get(sheet_idx, [])+[row]

        if sheet.cell(row, col_init_date_idx).ctype == 3 and sheet.cell(row, col_end_date_idx).ctype == 3:
            used_row = True
            use_sheet = True
            row_obj.init_date = sheet.cell(row, col_init_date_idx).value
            row_obj.end_date = sheet.cell(row, col_end_date_idx).value
            # dates[sheet_idx] = dates.get(sheet_idx, []) + [row]

        if sheet.cell(row, col_price).ctype != 2:
            row_obj.price = 0.0
            used_row = True
            used_sheet = True
        else:
            row_obj.price = sheet.cell(row, col_price).value

        if used_row:
            sheet_obj.rows.append(row_obj)
    if use_sheet:
        sheets.append(sheet_obj)

print "Correcting values ..."
for sheet in sheets:
    for row in sheet.rows:
        if row.name != '' and row.name not in hotel_set:
            if row.name in hotel_fixes.keys():
                #print 'hotel corrected: from {0} to {1}'.format(row.name, hotel_fixes[row.name])
                row.name = hotel_fixes[row.name]
            else:
                #print 'hotel - {0} not corrected'.format(row.name)
                pass
        if row.name != '':
            if row.name not in hotel_set:
                print 'hotel not found: ', row.name
        if row.supplier in ['DC']:
            #print "correcting supplier from {0} to {1}".format(row.supplier, row.name)
            row.supplier = row.name
        if row.supplier == 'SCUK':
            #print "correcting supplier from {0} to {1}".format(row.supplier, 'San Cristobal UK')
            row.supplier = 'SAN CRISTOBAL UK'


new_book = xlutils.copy.copy(book)

for sheet_obj in sheets:
    sheet_xls = new_book.get_sheet(sheet_obj.idx)
    for row in sheet_obj.rows:
        sheet_xls.write(row.idx, col_name_idx, row.name)
        sheet_xls.write(row.idx, col_supplier_idx, row.supplier)
        sheet_xls.write(row.idx, col_init_date_idx, row.init_date, style)
        sheet_xls.write(row.idx, col_end_date_idx, row.end_date, style)
        sheet_xls.write(row.idx, col_price, row.price)

splitted_name = os.path.splitext(os.path.basename(file_name))
new_book.save("{}ok{}".format(splitted_name[0], splitted_name[1]))

#print book.sheet_by_index(0).cell(0, 0).value


#print "Replacing DC by Hotel name"
#for sheet_idx, rows in updates.iteritems():
#	for row in rows:
#		value = book.sheet_by_index(sheet_idx).cell(row, 0).value
#		new_book.get_sheet(sheet_idx).write(row, 1, value)
#
#print "Fixing dates ..."
#for sheet_idx, rows in dates.iteritems():
#	for row in rows:
#		value = book.sheet_by_index(sheet_idx).cell(row, 0).value
#		new_book.get_sheet(sheet_idx).write(row, 1, value, style)
#
#new_book.save('hoteles-15-16ok.xls')

#print book.sheet_by_index(0).cell(0, 0).value
