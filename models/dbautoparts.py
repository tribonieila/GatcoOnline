#from gluon.contrib.appconfig import AppConfig
#db = DAL('postgres://root:admin@localhost:5432/gatcowsp')
from applications.GatcoAutoParts.modules.countries import *
import locale
locale.setlocale(locale.LC_ALL, '') 
db.define_table('billing_address',
    Field('user_id', 'reference auth_user'),
    Field('company', 'string'),
    Field('contact_no', 'string'),
    Field('line_1', 'string'),
    Field('line_2', 'string'),
    Field('town_or_city', 'string'),
    Field('postcode', 'string'),
    Field('country', 'string', requires = IS_IN_SET(COUNTRIES, zero = 'Country')))

db.define_table('delivery_address',
    Field('user_id', 'reference auth_user'),
    Field('line_1', 'string'),
    Field('line_2', 'string'),
    Field('town_or_city', 'string'),
    Field('postcode', 'string'),
    Field('country', 'string', requires = IS_IN_SET(COUNTRIES, zero = 'Country')))

db.define_table('car_brand',
    Field('brand'), format = '%(brand)s')

db.define_table('car_model',
    Field('brand_id', 'reference car_brand', requires = IS_IN_DB(db, db.car_brand, '%(brand)s', zero = 'What auto brand?'),
        represent = lambda id, r: db.car_brand(id).brand, label = 'Auto Brand'),
    Field('model'), format = '%(model)s')

db.define_table('year_model',
    Field('year_model', 'integer'), format = '%(year_model)s')

db.define_table('group_selection',
    Field('group_part'), format = '%(group_part)s')

db.define_table('auto_part',
    Field('brand_id', 'reference car_brand', requires = IS_IN_DB(db, db.car_brand, '%(brand)s', zero = 'What auto brand?'),
        represent = lambda id, r: db.car_brand(id).brand, label = 'Auto Brand'),
    Field('model_id', 'reference car_model', requires = IS_IN_DB(db, db.car_model, '%(model)s', zero = 'What auto model?'),
        represent = lambda id, r: db.car_model(id).model, label = 'Auto Model'),
    Field('year_model_id', 'reference year_model', requires = IS_IN_DB(db, db.year_model, '%(year_model)s', zero = 'What year model?'),
        represent = lambda id, r: db.year_model(id).year_model, label = 'Year Model'),
    Field('group_id', 'reference group_selection', requires = IS_IN_DB(db, db.group_selection, '%(group_part)s', zero = 'Group Selection?'),
        represent = lambda id, r: db.group_selection(id).group_part, label = 'Group Selection'),
    Field('part_no'),
    Field('description'),
    Field('price',  'double', readable = False, writable = False), 
    Field('in_dollar', 'double', label = 'Price (US $)', represent = lambda value, row: DIV(B(str('$ ' + locale.format('%.2f', value,1)), _style = 'text-align:right'))), 
    Field('quantity', 'integer', label = 'Available Qty.',represent = lambda value, row: DIV(locale.format('%d', value or 0, grouping = True), _style = 'text-align: center')))


db.define_table('customer_invoice', 
    Field('user_id', 'reference auth_user'),
    Field('invoice_no', 'string'),
    Field('invoice_date', 'datetime'),
    Field('part_no_id', 'reference auto_part'),
    Field('qty', 'integer'),
    Field('in_dollar', 'double'),
    Field('tracking_no', 'string'), format='%(tracking_no)s')

db.define_table('customer_order',
    Field('user_id', 'reference auth_user'),
    Field('tracking_no', 'integer'),
    Field('part_no', 'string'),
    Field('description_id', 'string'),
    Field('qty', 'integer'),#represent = lambda value, row: locale.format('%.2F', value, grouping = True)),
    Field('price', 'double', represent = lambda value, row: locale.format('%.2F', value, grouping = True)), 
    Field('amount', 'double'),
    Field('tax', 'double'),
    Field('sub_total', 'double'),
    Field('status', requires=IS_IN_SET(['Quotation','Order','Checkout','Available','Not Available'])), #requires = IS_IN_SET({'A':'Apple','B':'Banana','C':'Cherry'},zero=None)
    Field('date_order', 'datetime', default=request.now))

db.define_table('customer_transaction',
    Field('user_id', 'reference auth_user'),
    Field('total_amount', 'double'),
    Field('date_trans', 'datetime', default=request.now))
db.define_table('customer_inq',
    Field('user_id', 'reference auth_user'),
    Field('customer_msg', 'text'),
    Field('date_msg', 'datetime', default = request.now))

db.define_table('order_req',
    Field('auto_part_id', 'reference auto_part'),
    Field('quantity', 'integer' ))

session.show_items = session.show_items or {}

def price_cart():
    itm_price= 0
    itm_tax =0
    itm_subtotal = 0
    qty = 0.0
    itm = 0
    price = 0.0
    rows = []
    total = 0.0
    tot = 0.0
    _row = None
    _col = None
    itm = len(session.show_items)
    for _row, _col in session.show_items.items():       
        row = db.auto_part(_row)
        itm_price = _col * row.in_dollar
        itm_tax = _col * (row.in_dollar * .03)
        itm_subtotal = itm_price + itm_tax
        tot += (itm_price) + (itm_tax)
        price += row.in_dollar  
    return dict(_col=_col, _row=_row, qty = qty, itm = itm, price = price, rows=rows, 
        total = total, tot=tot, itm_price = itm_price, itm_tax = itm_tax, itm_subtotal = itm_subtotal)

def group_rows(rows,table1,*tables):
    last = None
    new_rows = []
    for row in rows:
        row_table1 = row[table1]
        if not last or row_table1.id!=last.id:
            last = row_table1
            new_rows.append(last)
            for t in tables:
                last[t] = []
        for t in tables:
            last[t].append(row[t])
    return new_rows


import random
def get_promo_code(num_chars):
    code_chars = '123456789ABCDEFGHIJKLMNPQRSTUVWXYZ'
    code = ''
    for i in range(0, num_chars):
        slice_start = random.randint(0, len(code_chars) -1)
        code += code_chars[slice_start: slice_start + 1]
    return code