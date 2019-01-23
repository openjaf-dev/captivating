__author__ = 'yuriq'

import xlrd, datetime, json

BASE_DATE = 693594

# file_name = 'files/2019_feb_CC.xls'
file_name = 'files/2019_feb_UK.xls'

book = xlrd.open_workbook(file_name, formatting_info=True)

sheet = book.sheets()[-1]


def get_date(d):
    try:
        n = int(d) + BASE_DATE
        return str(datetime.datetime.fromordinal(n).date())
    except:
        raise Exception('Wrong date format')

# Reading xls and storing bookings on list orders

orders = []
order = None

for r in range(1, sheet.nrows):

    order_line = {'product_category': '', 'product_name': '', 'supplier': '', 'start_date': '', 'end_date': '', 'confirmation': ''}

    def cell(c):
        return sheet.cell_value(r, c)

    if cell(0):
        if order:
            orders.append(order)
        order = {'reference': '', 'start_date': '', 'arrival_flight': '', 'client': '', 'paxs': [], 'order_lines': [], 'comments': ''}
        order['reference'] = cell(0)

    if cell(1):
        order['start_date'] = get_date(cell(1))

    if cell(2):
        order['client'] = cell(2)

    if cell(4):
        order['paxs'].append(cell(4))

    if cell(5):
        order_line['product_category'] = cell(5)

    if cell(6):
        order_line['product_name'] = cell(6).upper()

    if cell(7):
        order_line['supplier'] = cell(7)

    if cell(8):
        order_line['start_date'] = get_date(cell(8))
    else:
        order_line['start_date'] = order['start_date']

    if cell(9):
        order_line['end_date'] = get_date(cell(9))
    else:
        order_line['end_date'] = order['start_date']

    if cell(10):
        order['arrival_flight'] = cell(10)
    else:
        order['arrival_flight'] = ''

    if cell(11):
        order_line['confirmation'] = cell(11)
    else:
        order_line['confirmation'] = ''

    if cell(12):
        order['comments'] = cell(12)

    order['order_lines'].append(order_line)

orders.append(order)

f = open('orders_orig.txt', 'w+')
json.dump(orders, f)
f.close()
