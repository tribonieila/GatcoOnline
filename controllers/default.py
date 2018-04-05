# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
#########################################################################
CURRENCY = '$'

def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simply replace the two lines below with:
    return auth.wiki()
    """
    
    return dict(message=T('Welcome to Audi Volkswagon Porsche'))

def query():
    grid = SQLFORM.grid(query)
    return locals()



def form():
    form = FORM(DIV(DIV(INPUT(_type='text', _class='form-control', _placeholder='Search for...', _name='keywords', _value=request.get_vars.keywords, _id='keywords'),
        SPAN(INPUT(_type='submit', _value='Go!', _class='btn btn-default'), _class='input-group-btn'), _class='input-group'), _class='col-lg-6'),
        _action='url', _method='GET')
    return locals()


def search_form(self,url):
    form = FORM()#(DIV(INPUT(_type='text', _class='form-control', _placeholder='Search for...', _name='keywords', _value=request.get_vars.keywords, _id='keywords'),
    #    SPAN(INPUT(_type='submit', _value='Go!', _class='btn btn-default'), _class='input-group-btn'), 
    #    _action='url', _method='GET')), _class='col-lg-6')
    return form 

def search_query(search_text):
    words= search_text.split(' ') if search_text else []
    query = db.auto_part.id<0
    queries=[]
    queries.append(db.auto_part.id>0)
    for word in words:
        key,value=word.split(':') if ':' in word else ['',word]
        if key=='part_no':
            queries.append(db.auto_part.part_no.contains(value))
        elif key=='description':
            queries.append(db.tauto_part.description.contains(value))
        else:
            queries.append(db.auto_part.part_no.contains(value)|db.auto_part.description.contains(value))
    if len(queries) > 0:
        query = reduce(lambda part_no,description:(part_no&description),queries)
    return query

def index2():
    search_text=request.get_vars.keywords
    query=search_query(search_text)
    fields=[db.auto_part.part_no, db.auto_part.description, db.auto_part.price]
    table=SQLFORM.grid(query, search_widget=search_form, fields=fields, csv = False)
    return locals()

def converttodollar():
    db(db.auto_part.id > 0).update(in_dollar = db.auto_part.price / 3.65)
    return locals()

def display_form():
    model = [OPTION(texts.model, _value=texts.id) for texts in db(db.car_model.brand_id == 1).select(db.car_model.ALL)]  
    form=FORM('Model:', SELECT(*model, _name='model', _type="text", _placeholder="200"),
              INPUT(_type='submit'))
    if form.accepts(request,session):
        response.flash = 'form accepted'
    elif form.errors:
        response.flash = 'form has errors'
    else:
        response.flash = 'please fill the form'
    return dict(form=form)


links = [lambda row: A(SPAN(_class='glyphicon glyphicon-shopping-cart'),
    ' Add to cart', _title='Add to cart', _class='btn btn-default btn-xs', 
    callback=URL('add_item', vars=dict(id=row.id, action='add'))),
lambda row: A(SPAN(_class='glyphicon glyphicon-info-sign'),
    ' View the info', _class='btn btn-default btn-xs',  _tabindex='0', _role='button', 
    _title='Part Info',**{'_data-toggle':'popover','_data-trigger':'focus', '_data-html':'true','_data-content': view_info(row.id)})] 

def view_info(z = request.args(0)):
    for x in db(db.auto_part.id == z).select():
        i = TABLE(*[
            TR(TD('Brand: '), TD(x.brand_id.brand)),
            TR(TD('Model: '), TD(x.model_id.model)),
            TR(TD('Year: '), TD(x.year_model_id.year_model)),
            TR(TD('Group: '), TD(x.group_id.group_part))])
    table = str(XML(i, sanitize=False))
    return table

add=[lambda row: A(SPAN(_class = 'glyphicon glyphicon-shopping-cart'), 
    ' Add to cart', _title='Add to cart', _class='btn btn-primary btn-xs', 
    callback=URL('cart/add', vars=dict(id=row.id, **{'data-target':'cart'})))] 

def clear_session():
    session.show_items.clear()
    return locals()
fields = [db.auto_part.part_no, db.auto_part.description, db.auto_part.quantity]
def audi():
    grid = LEGEND('Introducing our featured auto parts')
    query = db.car_model.brand_id == 1
    form = SQLFORM.factory(
        Field('model', requires = IS_IN_DB(db(query), db.car_model,'%(model)s', zero = 'What model?')),
        Field('year', 'integer', widget=lambda f, v: SQLFORM.widgets.integer.widget(f, v, _placeholder=T("2006-1980"))),
        Field('part', requires = IS_IN_DB(db, db.group_selection, '%(group_part)s', zero = 'What auto part?')))
    if form.process().accepted:
        year = db(db.year_model.year_model == form.vars.year).select(db.year_model.id).first()
        query = db.auto_part.brand_id == 1
        query &= db.auto_part.model_id == form.vars.model
        query &= db.auto_part.year_model_id == year
        query &= db.auto_part.group_id == form.vars.part      
        grid += SQLFORM.grid(query, fields = fields, search_widget = search_form, details = False,csv = False, links = links, 
            deletable=False, editable=False, create=False, user_signature=False)
        return dict(form = form, grid = grid)
    
    grid += SQLFORM.grid(db.auto_part.brand_id == 1, fields = fields, search_widget = search_form, details = False, 
        user_signature=False, csv = False, links = links, deletable=False, editable=False, create=False, maxtextlength=40) 
 
    if request.args(0) == 'view':
        response.view = 'default/view_info.load'
    return dict(form = form, grid = grid)



def audis():
    keywords = '/'.join(request.args) if request.args else None
    query = db.auto_part.brand_id == 1    
    

    if len(request.args):
        page=int(request.args[0])
    else:
        page=0
    items_per_page=20
    limitby=(page*items_per_page,(page+1)*items_per_page + 1)

    if request.vars.id:
        query &= db.auto_part.id == request.vars.id

    else:
        if keywords:
            query &= db.auto_part.part_no.startswith(keywords)

        if request.vars.q:
            query &= reduce(lambda a,b:a&b,[db.auto_part.part_no.contains(k) for k in request.vars.q])
            query |= reduce(lambda a,b:a&b,[db.auto_part.description.contains(k) for k in request.vars.q])
    
    rows = db(query).select(orderby=db.auto_part.id, limitby=limitby)

    return locals()

def show_thankyou_notes():
    items = DIV(TABLE(TR(TD(SPAN(_class='glyphicon glyphicon-gift', **{'_aria-hidden':'true'}), _style="width:8%"),
        TD(B('Thank You For Your Shopping!'))),
    TR(TD(),TD("Anim pariatur cliche reprehenderit, enim eiusmod high life \
        accusamus terry richardson ad squid."))), _class='alert alert-info', _role='alert')
    return items    

def show_empty_items():
    items = DIV(TABLE(TR(TD(SPAN(_class='glyphicon glyphicon-gift', **{'_aria-hidden':'true'}), _style="width:8%"),
        TD(B('Your shopping cart is empty!'))),
    TR(TD(),TD('How dare it be?! Why not add some stuff to it?'))), _class='alert alert-default', _role='alert')
    return items

def show_empty_quotation():
    items = DIV(TABLE(TR(TD(SPAN(_class='glyphicon glyphicon-gift', **{'_aria-hidden':'true'}), _style="width:8%"),
        TD(B("You have empty quotaton!"))),
    TR(TD(),TD('Add items to shopping cart'))), _class='alert alert-default', _role='alert')
    return items

def show_not_login():
    items = DIV(TABLE(TR(TD(SPAN(_class='glyphicon glyphicon-gift', **{'_aria-hidden':'true'}), _style="width:8%"),
        TD(B(" You Must Be Login!"))),
    TR(TD(),TD('Thank you for visiting.'))), _class='alert alert-default', _role='alert')
    return items

def show_empty_cart():
    items = DIV(TABLE(TR(TD(SPAN(_class='glyphicon glyphicon-shopping-cart', **{'_aria-hidden':'true'}), _style="width:8%"),
        TD(B('Your Shopping Cart Is Empty!'))),
    TR(TD(),TD('Add items to shopping cart'))), _class='alert alert-default', _role='alert')
    return items

def add_item():
    id = int(request.vars.id)
    session.show_items[id] = session.show_items.get(id, 0) + 1
    response.js= "web2py_component('%s','show_items')" % URL('default','show_items') 
    return show_items

def show_items():
    if auth.user:
        cart = A('View my cart', _class='btn btn-default', _href=URL('default','show_cart'))
        chko = A('Checkout', _class='btn btn-default btn-sm', _href=URL('default', 'checkout'))
    else:
        cart = A('View my cart', _class='btn btn-default', _href=URL('default','show_cart'))
        chko = A('Checkout', _class='btn btn-default btn-sm disabled', _href=URL('default', 'checkout'))
    if not session.show_items: 
        return show_empty_items()
    else:
        l = len(session.show_items)
        result = price_cart()   
        if l > 1:
            itm = str(l) + ' Items in your shopping cart'
        else:
            itm = str(l) + ' Item in your shopping cart'
        items = DIV(TABLE(TR(TD(SPAN(_class='glyphicon glyphicon-gift', **{'_aria-hidden':'true'}), _style="width:10%"),TD(B(itm))),
            #TR(TD(),TD(B(' '+'$ '+str(locale.format('%.2F',result['price'], grouping = True )))+' (ex. tax & delivery)')),
            TR(TD(),TD(BR(),cart))),       
            _class="alert", _role="alert", _id="items")
    return items

def show_carts():
    #<button type="button" class="btn btn-primary" data-toggle="modal" data-target=".bs-example-modal-sm">Small modal</button>        
    # **{'_data-toggle':'tooltip', '_data-placement':'right', '_title':'send to your email'},
    if auth.user: 
        inq = A('Ask for a quotation?',  _title='item(s) above will send directly to our workshop for pricing, make sure your E-Mail is true.',callback=URL('inquer'),  _class='btn btn-default')
        coc = INPUT(_type='text',  _class='form-control', _placeholder='Coupon Code?')
        #tip = I(' If you click assistant button. Item(s) above will send directly to our workshop, make sure your details below are true.  ', _style='float:left')
    else: 
        inq = A('Ask for a quotation?', _title = 'send the list for inquery first', callback=URL('inquer'),  _class='btn btn-default', _disabled="disabled")
        coc = INPUT(_type='text', id="disabledInput", _disabled='disabled', _class='form-control', _placeholder='Coupon Code?')
        #tip = ''
    chk = DIV(LABEL(INPUT( _type='checkbox'),'Ask for assistant?',**{'_data-toggle':'collapse', '_data-target':'#collapseEmail'}),_class="checkbox")
    eml = DIV(DIV(DIV(INPUT(_type='text', _class='form-control', _placeholder='your email here...'),
    SPAN(BUTTON(_class='btn btn-default',_type='button'),_class='input-group-btn'),_class='input-group'),_class='col-lg-6'),_class='collapse', _id='collapseExample')
    if not session.show_items: 
        return show_empty_cart()
    else:
        tot = 0
        row = []
        n = 1
        head = THEAD(TR(TH('No.'),TH('Qty'),TH('Part No.'), TH('Description'),TH()))#,TH('Price'),TH('Tax'),TH('Sub-Total'), TH()))       
        for x, y in session.show_items.items(): 
            z = db.auto_part(x)
            add = A(SPAN(_class='glyphicon glyphicon-plus-sign'), ' Add Qty.', _title = 'add quantity', callback=URL('show_cart_ctrl', vars=dict(id=z.id,action='add')),_class='btn btn-default btn-xs')
            sub = A(SPAN(_class='glyphicon glyphicon-minus-sign'),' Sub Qty.', _title = 'sub quantity', callback=URL('show_cart_ctrl', vars=dict(id=z.id,action='sub')),_class='btn btn-default btn-xs')
            clr = A(SPAN(_class='glyphicon glyphicon-remove-sign'),' Del Item', _title = 'delete item', callback=URL('show_cart_ctrl', vars=dict(id=z.id,action='clr')),_class='btn btn-default btn-xs')
            itm_price = y * z.in_dollar
            itm_tax = y * (z.in_dollar * .03)
            itm_subtotal = itm_price + itm_tax
            
            row.append(TR(TD(str(n)+'.'), TD(y), TD(z.part_no), TD(z.description), #TD('$ ' + str(locale.format('%.2F',itm_price, grouping = True)),_align='right'), 
                #TD('$ ' + str(locale.format('%.2F',itm_tax, grouping = True)),_align='right'),TD('$ ' + str(locale.format('%.2F',itm_subtotal, grouping = True)),_align='right'),
                TD(add, sub, clr, _align='right')))
            n += 1
            tot += (y*z.in_dollar)+(y*(z.in_dollar*.03))    
        body = TBODY(*row)
        '''
        foot = TR(TD(B('Total'), _align='right', _colspan='5'),
            TD(B('$ '+str(locale.format('%.2F',tot, grouping = True))),_align='right'),
            TD(inq))
        '''
        foot = TR(TD(_colspan='4'), TD(inq,  _align='right'))
        table = TABLE(*[head, body, foot],  _width="100%", _class = 'table')

        return table


def on():
    if auth.user: response.flash = str(auth.user.email)
    return locals()

def inquer():
    if mail:
        if mail.send(to=['hilario@gatco.qa'],
            subject='Customer Inquery',
            message=('Plain text body', str(inq()))):
            save_quotation()
            response.flash = 'email sent'

        else:
            response.flash = 'email not send'
    else:
        response.flash = 'unable to send email'
    return locals()

def inq():
    if not session.show_items: 
        return show_empty_cart()
    else:    
        qty = 1
        tax = 23.34
        tot = 0
        row = []
        item = price_cart()
        rows = price_cart()
        head = THEAD(TR(TH('Qty'),TH('Part No.'), TH('Description'),TH('Price'),TH('Tax'),TH('Sub-Total'), TH()))       
        for x, y in session.show_items.items(): 
            z = db.auto_part(x)
            itm_price = y * z.in_dollar
            itm_tax = y * (z.in_dollar * .03)
            itm_subtotal = itm_price + itm_tax
            row.append(TR(TD(y), TD(z.part_no), TD(z.description),TD('$ ' + str(locale.format('%.2F',itm_price, grouping = True)),_align='right'), 
                TD('$ ' + str(locale.format('%.2F',itm_tax, grouping = True)),_align='right'),TD('$ ' + str(locale.format('%.2F',itm_subtotal, grouping = True)),_align='right'),
                TD()))
            tot += (y*z.in_dollar)+(y*(z.in_dollar*.03))    

        body = TBODY(*row)
        foot = TR(TD(B('Total'), _align='right', _colspan='5'),TD(B('$ '+str(locale.format('%.2F',tot, grouping = True))),_align='right'),
            TD())
        table = TABLE(TR(TD('Customer: '), TD(auth.user.last_name +' ' + auth.user.first_name)),
            TR(TD('Email: '), TD(auth.user.email)))
        table += TABLE(*[head, body, foot],  _width="100%", _class = 'table')
        
        return table


def save_quotation():
    track_no = 100
    if db(db.customer_order).isempty():      
        for x, y in session.show_items.items():
            z = db.auto_part(x)
            itm_price = y * z.in_dollar
            itm_tax = y * (z.in_dollar * .03)
            itm_subtotal = itm_price + itm_tax
            db.customer_order.insert(user_id=auth.user.id, tracking_no=track_no, part_no=z.part_no, description_id=z.description,
                qty=y, price=z.in_dollar, amount=itm_price, tax=itm_tax, sub_total = itm_subtotal, status='Quotation', date_order=request.now)
            #response.flash = '1st Track Inserted'
    else:
        tracking_no = db.customer_order.tracking_no.max()
        tracking_no = db().select(tracking_no).first()[tracking_no]
        tracking_no += 1
        for x, y in session.show_items.items():
            z = db.auto_part(x)
            itm_price = y * z.in_dollar
            itm_tax = y * (z.in_dollar * .03)
            itm_subtotal = itm_price + itm_tax
            db.customer_order.insert(user_id=auth.user.id, tracking_no=tracking_no, part_no=z.part_no, description_id=z.description,
                qty=y, price=z.in_dollar, amount=itm_price, tax=itm_tax, sub_total = itm_subtotal, status='Quotation', date_order=request.now)
            #response.flash = '2nd Track Inserted'
    return locals()
def quotation():
    return locals()

def q():
    query = db.customer_order.user_id == auth.user.id
    query &= db.customer_order.status == 'Quotation'
    query = db(query).select(db.customer_order.ALL)
    if query:
        response.flash = 'true'
    #if not query:
    #    response.flash = 'true'
    return locals()

def quotations():
    
    if auth.user: #if db(db.customer_order).isempty():     
        if db(db.customer_order.user_id == auth.user.id).isempty():
            #response.flash = 'empty'
            table = show_empty_quotation()
        else:
            x =  []
            ta = 0
            ctr=0
            
            query = db.customer_order.user_id == auth.user.id #) & (db.customer_order.status == 'Quotation')
            query &= db.customer_order.status != 'Order'
            head = THEAD(TR(TH('Date'),TH('Part No.'),TH('Description'), TH('Qty.'), TH('Price'), TH('Amount'), TH('Tax'), TH('SubTotal')))
            total_amount='- -'
            for y in db(query).select(db.customer_order.ALL, groupby = db.customer_order.tracking_no, orderby=~db.customer_order.tracking_no):           
                x.append(TR(TD(y.date_order),TD(_colspan='7')))
                for r in db(db.customer_order.tracking_no == y.tracking_no).select(db.customer_order.ALL):
                    #ctr += 1
                    #total_amount=db.customer_order.sub_total.sum().coalesce_zero()
                    #total_amount=db(db.customer_order.tracking_no==y.tracking_no).select(total_amount).first()[total_amount]

                    #status = db.customer_order.status == 'Available'
                   
                    if r.status == 'Available':
                        total_amount=0
                        price = locale.format('%.2F',r.price, grouping=True)
                        amount = locale.format('%.2F', r.amount,grouping=True)
                        tax = locale.format('%.2F', r.tax,grouping=True)
                        sub_total = r.sub_total# or '- -', grouping=True)
                        #DIV(DIV(DIV(LABEL(INPUT(_type='checkbox', _name='checkbox'),'Deliver to a different address?',**{'_data-toggle':'collapse', '_data-target':'#collapseDelAdd'}),_class='checkbox'),_class='col-md-12'),_class='row'),BR(),
                        chk = LABEL(INPUT(_type='checkbox',_onclick="{{callback=URL('add_to_checkout')}}"))
                        foot = TR(TD(_colspan='8'),TD(A('Proceed to checkout',_href='#')),_align='right')
                        #if sub_total == '- -':
                        #    sub_total = sub_total
                        #else:                      
                        #    total_amount += sub_total
                    else: 
                        price = '- -'
                        amount = '- -'
                        tax = '- -'
                        sub_total = '- -'
                        chk = INPUT( _type='checkbox', _disabled="disabled")
                        foot = TR(TD(_colspan='8'),TD(A('Proceed to checkout')),_align='right')
                    x.append(TR(TD(),TD(r.part_no),TD(r.description_id), TD(r.qty),TD(price, _align='right'), TD(amount, _align='right'),TD(tax, _align='right'), TD(sub_total, _align='right')))
                
                total_amount = db.customer_order.sub_total.sum().coalesce_zero()
                total_amount = db((db.customer_order.tracking_no == y.tracking_no) & (db.customer_order.status == 'Available')).select(total_amount).first()[total_amount]
                if total_amount == False: 
                    ps=P('Checkout?',  _class='text-muted')
                else: 
                    total_amount = locale.format('%.2F', total_amount, grouping =True)
                    ps=A('Checkout?', _href=URL('checkout'))
                
                x.append(TR(TD(B('Total Amount'), _colspan='7', _align='right'),TD(B('$ ',total_amount),_align='right'),TD()))
                
                
                body = TBODY(x)

                table = TABLE(*[head,body],_class='table')
    else:
        table = show_not_login()
    return table 
def add_to_checkout():
    response.flash = 'add to checkout'
    return locals() 
def pay():
    
    tot = price_cart()
    #total_amount=db(    )
    #from gluon.contrib.stripe import Stripe
    form = SQLFORM.factory(
        Field('card_number', 'integer'),
        Field('card_exp_month', 'integer'),
        Field('card_exp_year', 'integer'),
        Field('card_cvc_check', 'integer', comment = 'This is the 3 digit number on the back of your card.'))
    #if form.process().accepted:
    if form.accepts(request.vars, session): 
        response.flash = str(request.args(0))
        db.customer_transaction.insert(user_id=auth.user.id, total_amount=request.args(0), date_trans=request.now)

        response.flash = 'success'
        session.show_items.clear()
        redirect(URL('thankyou'))   

        #session.your_name = form.vars.your_name
        #session.your_image = form.vars.your_image
    elif form.errors:
        response.flash = 'form has errors'    
    return dict(form = form)


def show_cart_ctrl():
    id = int(request.vars.id)
    x = session.show_items.get(id)
    #response.flash = str(y)
    if request.vars.action == 'add': 
        session.show_items[id]=session.show_items.get(id,0)+1
    if request.vars.action == 'sub':
        session.show_items[id]=max(0,session.show_items.get(id,0)-1)
    if request.vars.action == 'clr':
        del session.show_items[id]    
    response.js =  "jQuery('#items').get(0).reload();"
    response.js +=  "jQuery('#show_carts').get(0).reload();"
    
    #response.js= "web2py_component('%s','show_carts')" % URL('default','show_carts') 
    #response.js= "$.web2py.component('%s',target='show_carts')" % URL('default','show_carts.load') 
    #response.js = "web2py_component('%s',target='show_carts')" % URL('default','show_carts') 
    #response.js += "web2py_component('%s',target='items')" % URL('default','show_items') 
    #response.js =  remake_reload_script('#show_carts', '#show_items')
    return show_cart()



def volkswagen():
    grid = LEGEND('Introducing our featured auto parts')  
    query = db.car_model.brand_id == 2
    form = SQLFORM.factory(
        Field('model', requires = IS_IN_DB(db(query), db.car_model, '%(model)s', zero = 'What model?')),
        Field('year', 'integer', widget=lambda f, v: SQLFORM.widgets.integer.widget(f, v, _placeholder=T("2006-1980"))),
        Field('part', requires = IS_IN_DB(db, db.group_selection, '%(group_part)s', zero = 'What auto part?')))
    if form.process().accepted:
        year = db(db.year_model.year_model == form.vars.year).select(db.year_model.id).first()
        query = db.auto_part.brand_id == 2
        query &= db.auto_part.model_id == form.vars.model
        query &= db.auto_part.year_model_id == year
        query &= db.auto_part.group_id == form.vars.part   
 
        grid += SQLFORM.grid(query, fields = fields, search_widget = search_form, details = False,csv = False, links = links,
            deletable=False, editable=False, create=False,)
        return dict(form = form, grid = grid)
    
    grid += SQLFORM.grid(db.auto_part.brand_id == 2, fields = fields, search_widget = search_form, details = False, csv = False, 
        deletable=False, editable=False, create=False, links = links, maxtextlength=40) 
 
    return dict(form = form, grid = grid)

def porsche():
    grid = LEGEND('Introducing our featured auto parts')  
    query = db.car_model.brand_id == 3
    form = SQLFORM.factory(
        Field('model', requires = IS_IN_DB(db(query), db.car_model, '%(model)s', zero = 'What model?')),
        Field('year', 'integer', widget=lambda f, v: SQLFORM.widgets.integer.widget(f, v, _placeholder=T("2006-1980"))),
        Field('part', requires = IS_IN_DB(db, db.group_selection, '%(group_part)s', zero = 'What auto part?')))
    if form.process().accepted:
        year = db(db.year_model.year_model == form.vars.year).select(db.year_model.id).first()
        query = db.auto_part.brand_id == 3
        query &= db.auto_part.model_id == form.vars.model
        query &= db.auto_part.year_model_id == year
        query &= db.auto_part.group_id == form.vars.part      
        grid += SQLFORM.grid(query, fields = fields, search_widget = search_form, details = False,csv = False, links = links,
            deletable=False, editable=False, create=False,)
        return dict(form = form, grid = grid)
    grid += SQLFORM.grid(db.auto_part.brand_id == 3, fields = fields, search_widget = search_form, details = False, csv = False, 
        deletable=False, editable=False, create=False, links = links, maxtextlength=40) 
    return dict(form = form, grid = grid)


'''
<div class="form-group" id="no_table_model__row">
    <label class="control-label col-sm-3" for="no_table_model" id="no_table_model__label">Model</label>
    <div class="col-sm-9">
        <select class="generic-widget form-control" id="no_table_model" name="model">
        <option value="">What model?</option>
        <option value="8">100</option>
        <option value="9">200</option>
        </select>
        <span class="help-block"></span></div></div><div class="form-group" id="no_table_year__row"><label class="control-label col-sm-3" for="no_table_year" id="no_table_year__label">Year</label><div class="col-sm-9"><input class="integer form-control" id="no_table_year" name="year" placeholder="2006-1980" value="" type="text"><span class="help-block"></span></div></div><div class="form-group" id="no_table_part__row"><label class="control-label col-sm-3" for="no_table_part" id="no_table_part__label">Part</label><div class="col-sm-9"><select class="generic-widget form-control" id="no_table_part" name="part"><option value="">What auto part?</option><option value="12">Accessories Infotainment</option><option value="10">Body</option><option value="8">Brakes</option><option value="11">Electric</option><option value="1">Engine</option><option value="4">Front Axle</option><option value="2">Fuel Exhaust Cooling</option><option value="3">Gearbox</option><option value="9">Pedals</option><option value="6">Rear Axle</option><option value="5">Steering</option><option value="7">Wheels</option></select><span class="help-block"></span></div></div><div class="form-group" id="submit_record__row"><div class="col-sm-9 col-sm-offset-3"><input class="btn btn-primary btn-default" value="Submit" type="submit"></div></div><div style="display:none;"><input name="_formkey" value="19ef4aed-0cda-47dd-9961-15affe7b8360" type="hidden"><input name="_formname" value="no_table/create" type="hidden"></div>
'''
def category():
    model = [OPTION(m) for m in db(db.auto_part.brand_id == 1).select(db.auto_part.brand)]
    form = DIV(DIV(SPAN(_class='glyphicon glyphicon-filter'), SPAN(B(' Category')),_class='panel-heading'),
        DIV(FORM(DIV(
            DIV(LABEL('Model:', _class='control-label col-sm-3'),DIV(SELECT(*model, _class='form-control'),_class='col-sm-9'),_class='row'),BR(),
            DIV(LABEL('Year:', _class='control-label col-sm-3'),DIV(INPUT(_type='text', _class='form-control', _placeholder='2006-1980'),_class='col-sm-9'),_class='row'),BR(),
            DIV(LABEL('Part:', _class='control-label col-sm-3'),DIV(SELECT(_class='form-control'),_class='col-sm-9'),_class='row'),BR(),
            DIV(INPUT(_type='submit', _value='Submit', _class='btn btn-default btn-sm'), _align='right',_class='col-sm-9 col-sm-offset-3'),
            _class='form-group')), _class='panel-body'),_class='panel panel-default')
    return form

def c():
    c = [OPTION(x) for x in COUNTRIES] 
    if auth.user:
        #form = H4('Complete your details below to complete your order')
        form = FORM(FIELDSET(TABLE(TR(TD(DIV(DIV(DIV(SPAN('First Name',_class='label label-default'),INPUT(_value=auth.user.first_name, _type='text', _class='form-control'),_class='col-md-6'),
        DIV(SPAN('Last Name',_class='label label-default'),INPUT(_value=auth.user.last_name, _type='text', _class='form-control'),_class='col-md-6'),_class='row'),

        DIV(DIV(SPAN('Your E-Mail Address',_class='label label-default'),INPUT(_value=auth.user.email, _type='text', _class='form-control'),_class='col-md-12'),   

        DIV(SPAN('Company Name (optional)',_class='label label-default'),INPUT(_name='billing_address_company', _type='text', _class='form-control'),_class='col-md-12'),
        
        DIV(SPAN('Your Contact Phone Number',_class='label label-default'),INPUT(_name='billing_address_contact_no',_type='text', _class='form-control'),_class='col-md-12'),_class='row'), _class='container-fluid'), _width='50%', _valign='top'),

        TD(DIV(DIV(DIV(SPAN('Billing Address',_class='label label-default'),INPUT(_name='billing_address_line_1',_type='text', _placeholder='line 1 address', _class='form-control'),_class='col-md-12'), _class='row'),BR(),
        DIV(DIV(INPUT(_name='billing_address_line_2',_type='text', _placeholder='line 2 address', _class='form-control'), _class='col-md-12'), _class='row'),BR(),
        DIV(DIV(INPUT(_name='billing_address_town_or_city',_type='text', _placeholder='town or city', _class='form-control'),_class='col-md-12'), _class='row'),BR(),
        DIV(DIV(INPUT(_name='billing_address_postcode', _type='text', _placeholder='post code', _class='form-control'),_class='col-md-12'), _class='row'),BR(),
        DIV(DIV(SELECT(*c, _name='billing_address_country',   _class='form-control'),_class='col-md-12'), _class='row'), 

        DIV(DIV(DIV(LABEL(INPUT(_type='checkbox', _name='checkbox'),'Deliver to a different address?',**{'_data-toggle':'collapse', '_data-target':'#collapseDelAdd'}),_class='checkbox'),_class='col-md-12'),_class='row'),BR(),

        DIV(DIV(DIV(DIV(
        DIV(SPAN(('Delivery Address'),_class='label label-default'),INPUT(_name='delivery_address_line_1',_type='text', _class='form-control', _placeholder='line 1 address'),_class='col-md-12'), _class='row'),BR(),   
        DIV(DIV(INPUT(_type='text', _name='delivery_address_line_2', _class='form-control', _placeholder='line 2 address'),_class='col-md-12'), _class='row'), BR(),
        DIV(DIV(INPUT(_type='text', _name='delivery_address_town_or_city', _class='form-control', _placeholder='town or city'),_class='col-md-12'), _class='row'), BR(),
        DIV(DIV(INPUT(_type='text', _name='delivery_address_postcode', _class='form-control', _placeholder='postcode'),_class='col-md-12'), _class='row'), BR(),
        DIV(DIV(SELECT(COUNTRIES, _name='delivery_address_country', _class='form-control', _placeholder='country'),_class='col-md-12'), _class='row'), BR(),
        _class='collapse', _id='collapseDelAdd'),_class='col-md-12'), _class='row'),
        DIV(INPUT(_type='submit',_value='Submit'),_class='row', _align='right'),
        _class='container-fluid'),_width='50%', _valign='top')),_width="100%"),DIV(_class="form-group")))
        
        if form.process().accepted:
            if form.vars.checkbox:
                db.delivery_address.insert(user_id=auth.user.id, line_1=form.vars.delivery_address_line_1, line_2=form.vars.delivery_address_line_2,
                    town_or_city=form.vars.delivery_address_town_or_city, postcode=form.vars.delivery_address_postcode, country=form.vars.delivery_address_country)
            db.billing_address.insert(user_id=auth.user.id, company=form.vars.billing_address_company, contact_no=form.vars.billing_address_contact_no,
                line_1=form.vars.billing_address_line_1, line_2=form.vars.billing_address_line_2, town_or_city=form.vars.billing_address_town_or_city, postcode=form.vars.billing_address_postcode,
                country=form.vars.billing_address_country)
            
            response.flash = 'save '
    else: 
        form = LEGEND(H4('Please kindly login or sign up to complete your orders.'))
        form += dis_form()
    return form




def dis_form():
    form = FORM(FIELDSET(TABLE(TR(TD(DIV(DIV(DIV(SPAN('First Name',_class='label label-default'),INPUT(_text='text', _class='form-control'),_class='col-md-6'),
    DIV(SPAN('Last Name',_class='label label-default'),INPUT(_text='text', _class='form-control'), _class='col-md-6'), _class='row'),
    DIV(DIV(SPAN('Your E-Mail Address',_class='label label-default'),INPUT(_text='text', _class='form-control'),_class='col-md-12'),
    DIV(SPAN('Company Name (optional)',_class='label label-default'),INPUT(_text='text', _class='form-control'),_class='col-md-12'),    
    DIV(SPAN('Your Contact Phone Number',_class='label label-default'),INPUT(_text='text', _class='form-control'),_class='col-md-12'),_class='row'), _class='container-fluid'), _width='50%', _valign='top'),
    TD(DIV(DIV(DIV(SPAN('Billing Address',_class='label label-default'),INPUT(_text='text', _class='form-control', _placeholder='address 1'),_class='col-md-12'), _class='row'),BR(),
    DIV(DIV(INPUT(_id='auth_user.address_1', _text='text', _class='form-control', _placeholder='address 2'),_class='col-md-12'), _class='row'),BR(),
    DIV(DIV(INPUT(_text='text', _class='form-control', _placeholder='town or city'),_class='col-md-12'), _class='row'),BR(),
    DIV(DIV(INPUT(_text='text', _class='form-control', _placeholder='postcode'),_class='col-md-12'), _class='row'),BR(),
    DIV(DIV(INPUT(_text='text', _class='form-control', _placeholder='country'),_class='col-md-12'), _class='row'),        
    _class='container-fluid'),_width='50%', _valign='top')),_width="100%"),DIV(_class="form-group"),_disabled=True))    
    return form

def d():
    c = [OPTION(x) for x in COUNTRIES]  
    if auth.user:
        
        form=FORM('Country:  ', SELECT(*c, value=auth.user.country, _id='auth_user_country',_name='country'))

    return locals()

def contact_us():
    return locals()
def test():
    if auth.user:
        usr = FORM(FIELDSET(DIV(INPUT(_type='text', _value=auth.user.last_name))))
        bil = FORM(FIELDSET(DIV(INPUT(_type='text', _id='company', _name='company', _value=''),INPUT(_type='submit', _value='submit'))))
        if bil.process().accepted:
            response.flash = 'save'
            db.billing_address.insert(user_id=auth.user.id, company=bil.vars.company)
        #usr = SQLFORM(db.auth_user, record=auth.user_id)
        #bil = SQLFORM(db.billing_address)
        #dea = SQLFORM(db.delivery_address)
    return locals()    
def inquerys():
    form = SQLFORM.factory(
    Field('name', requires=IS_NOT_EMPTY()),
    Field('email', requires =[ IS_EMAIL(error_message='invalid email!'), IS_NOT_EMPTY() ]))
    if form.process().accepted:
        #session.name = auth_user.last_name + ' ' + auth_user.last_name
        #session.email = auth_user.email
        #session.subject = form.vars.subject
        #session.message = form.vars.message
        if mail:
            if mail.send(to=['hilario@gatco.qa'],
                subject='Customer Inquery',
                #message= "Hello this is an email send from minerva.com from contact us form.\nName:"+ session.name+" \nEmail : " + session.email +"\nSubject : "+session.subject +"\nMessage : "+session.message+ ".\n "
                #message = ('Plain text body', str(inq()))
                message = ('Plain text body', str(inq()))
            ):
                response.flash = 'email sent sucessfully.'
            else:
                response.flash = 'fail to send email sorry!'
        else:
            response.flash = 'Unable to send the email : email parameters not defined'
    elif form.errors:
            response.flash='form has errors.'
    return dict(form=form)

def email_form():
    form = FORM(DIV(DIV(SPAN(_class='glyphicon glyphicon-envelope'),B(' E-Mail Us'),_class='panel-heading'),
        DIV(DIV(SPAN(SPAN(_class='glyphicon glyphicon-user'),_class='input-group-addon'),
            INPUT(_type='text', _class='form-control', _placeholder='Your Name', _id='your_name', _name='your_name'),_class='input-group'),BR(),
        DIV(SPAN(SPAN(_class='glyphicon glyphicon-envelope'),_class='input-group-addon'),
            INPUT(_type='text', _class='form-control', _placeholder='Your E-Mail Address',_id='your_email', _name='your_email'),_class='input-group'),BR(),
        DIV(SPAN(SPAN(_class='glyphicon glyphicon-list'),_class='input-group-addon'),
            SELECT('General Question', 'Feedback', 'Customer Service', value='General Question',_name='subject', _type='text', _class='form-control'),
            SPAN(('Subject'),_class='input-group-addon', _id='basic-addon1'),_class='input-group'),BR(),
        TEXTAREA(_class='form-control', _placeholder='Your Message', _id='message', _name='message',_rows='3'),BR(),
        INPUT(_type='submit', _class='btn btn-default', _value='Submit'),
            _class='panel-body'),_class='panel panel-default'))
    if form.process().accepted:
        #msg = DIV(form.vars.your_name),BR(),DIV(form.vars.your_email),BR(),DIV(form.vars.subject),BR(),DIV(form.vars.message)
        msg = TABLE(TR(TD('NAME: '), TD(form.vars.your_name)),TR(TD('E-MAIL: '), TD(form.vars.your_email)), TR(TD('SUBJECT:'),TD(form.vars.subject)),TR(TD('MESSAGES:'),TD(form.vars.message)))

        if mail:
            if mail.send(to=['hilario@gatco.qa'],
                subject=form.vars.subject,
                message=('Plain text body', str(msg))):
                response.flash = 'email sent successfully.'
            else:
                response.flash = 'fail to send email sorry!'
        else:
            response.flash = 'unable to send the email : email parameters not defined'
    elif form.errors:
        response.flash = 'form has errors.'

    return form

def cc_sif_form():
    form = DIV(DIV(SPAN(_class='glyphicon glyphicon-heart'),B(' Customer Care'),_class='panel-heading'),
        DIV(DIV(A(H4('Shipping Info',_class='list-group-item-heading'),P('Anim pariatur cliche reprehenderit, enim eiusmod high life accusamus terry richardson ad squid. 3 wolf moon officia aute, non cupidatat skateboard dolor brunch.',
            _class='list-group-item-text'),_href='shipping_info',_class='list-group-item'),
        A(H4('FAQ',_class='list-group-item-heading'),P('Anim pariatur cliche reprehenderit, enim eiusmod high life accusamus terry richardson ad squid. 3 wolf moon officia aute, non cupidatat skateboard dolor brunch.',
            _class='list-group-item-text'),_href='faq',_class='list-group-item'),
        _class='list-group'),_class='panel-body'),_class='panel panel-default')
    return form

def cc_cf_form():
    form = DIV(DIV(SPAN(_class='glyphicon glyphicon-heart'),B(' Customer Care'),_class='panel-heading'),
        DIV(DIV(A(H4('E-Mail Us',_class='list-group-item-heading'),P('Anim pariatur cliche reprehenderit, enim eiusmod high life accusamus terry richardson ad squid. 3 wolf moon officia aute, non cupidatat skateboard dolor brunch.',
            _class='list-group-item-text'),_href='contact_us',_class='list-group-item'),
        A(H4('FAQ',_class='list-group-item-heading'),P('Anim pariatur cliche reprehenderit, enim eiusmod high life accusamus terry richardson ad squid. 3 wolf moon officia aute, non cupidatat skateboard dolor brunch.',
            _class='list-group-item-text'),_href='faq',_class='list-group-item'),
        _class='list-group'),_class='panel-body'),_class='panel panel-default')
    return form    

def faq():
    return locals()

def shipping_info():
    return locals()

def car_brand():
    form = SQLFORM(db.car_brand)
    grid = SQLFORM.grid(db.car_brand)
    return locals()

def car_model():
    form = SQLFORM(db.car_model)
    grid = SQLFORM.grid(db.car_model)
    return locals()

def year_model():
    form = SQLFORM(db.year_model)
    return locals()    

def part_status():
    form = SQLFORM(db.part_status)
    return locals()

def auto_part():
    form = SQLFORM(db.auto_part)
    return locals()

def card_infos():
    infos = DIV(TABLE(TR(TD(SPAN(_class='glyphicon glyphicon-lock', **{'aria-hidden':'true'}), _style="width:8%"),
        TD(B('Are my card details safe?'))),
        TR(TD(),TD("Yes! This site is hosted using industry-standard encryption & we don't store your card details on our servers.")),
        BR(),
        TR(TD(SPAN(_class='glyphicon glyphicon-plane', **{'aria-hidden':'true'})),TD(B('How long will my order take to arrive?'))),
        TR(TD(),TD('This will depend on what delivery method you select opposite. If ordered before 4pm, all orders are despatched the same day.')),
        BR(),
        TR(TD(SPAN(_class='glyphicon glyphicon-credit-card', **{'aria-hidden':'true'})),TD(B('What payment methods do you accept?'))),
        TR(TD(),TD('We accept Visa, Mastercard & American Express credit/debit cards.'))), 
    _class="alert", _role="alert")
    return infos

def other_infos():
    infos = DIV(TABLE(TR(TD(SPAN(_class='glyphicon glyphicon-cog', **{'aria-hidden':'true'}), _style="width:8%"),
        TD(B('Free technical support'))),
        TR(TD(),TD('Well help you get your car working. Just call or e-mail us.')),
        BR(),
        TR(TD(SPAN(_class='glyphicon glyphicon-grain', **{'aria-hidden':'true'})),TD(B('Quality assurance'))),
        TR(TD(),TD('We check all the auto parts we ship so you can rely on us.')),
        BR(),
        TR(TD(SPAN(_class='glyphicon glyphicon-plane', **{'aria-hidden':'true'})),TD(B('Next day delivery'))),
        TR(TD(),TD('Order before 4pm and your order will be with you the next business day.'))), 
    _class="alert", _role="alert")
    return infos

def cartx():
    amt = 0
    if not session.cart:
        session.flash = 'Add something to shopping cart'
    else:
        itm = len(session.cart)
        if itm > 1:
            itm = ' Items in your shopping cart'
        else: itm = ' Item in your shopping cart'
        xcart=[]    
        for k, v in session.cart.items(): 

            #if len((session.cart) > 1)): href="{{=URL('function', vars=request.vars)}}"
                #print str(len(session.cart)) + ' Items in your shopping cart'
            for x in db(db.auto_part.id == k).select(db.auto_part.ALL):
                amt += x.in_dollar 
                xcart.append(x.in_dollar)  
                t = TABLE(TR(TD(B(str(len(session.cart))) + itm),
                    TR(TD(B('$ ' + str(amt)) + ' (ex. tax & delivery)'))))
    u = TABLE(TR(TD(A('View my cart', _class='btn btn-primary', _href=URL('default', 'cart'))),TD(A('Checkout',
                        _class='btn btn-success', _href=URL('default', 'checkout')))))
    return dict(cart=cart, xcart = 0, t = 0, u=0)

def carts():
    if not session.cart:
        session.flash = 'Add something to shopping cart'
    return locals()

def checkout():
    db.auth_user.password.writable = False   
    form = SQLFORM(db.auth_user, record=auth.user_id)
    if form.process().accepted:
        session.flash = 'form accepted'
        redirect(URL('pay'))
    elif form.errors:
        response.flash = str(form.errors)
    #return dict(form = form)
    return locals()

#@auth.requires_login()
def show_cart():
    #if auth.user: response.flash = 'yehey'
    #else: response.flash = 'huh!'
    #response.js =  remake_reload_script('#show_cart', '#show_items')
    #response.js = "web2py_component('%s',target='items')" % URL('default','show_items') 
    #response.js += "web2py_component('%s',target='show_carts')" % URL('default','show_carts.load') 
    return locals()

def order():
    if auth.user:
        
        ref_row = []
        ref_head = THEAD(TR(TH('Date'),TH('Doc.No.'), TH('Doc.Type')))
        ref_body = TBODY(*ref_row)
        ref_table = TABLE(*[ref_head, ref_body], _width = '100%', _class='table')
        tot = 0
        inv_row = []
        inv_head = THEAD(TR(TH('Part No.'), TH('Description'), TH('Qty'), TH('Price'), TH('Amount'),TH('Tax'), TH('SubTotal')))
        query = db.customer_order.user_id == auth.user_id
        query &= db.customer_order.status == 'Order'
        chk = db(query).isempty()
        if chk:
            response.flash = 'no order yet'
        for x in db(query).select(db.customer_order.ALL, orderby=db.customer_order.date_order):
            inv_row.append(TR(TD(x.part_no), TD(x.description_id), TD(x.qty), TD(locale.format('%.2F', x.price or 0.0, grouping = True)), TD(locale.format('%.2F', x.amount or 0.0, grouping = True)),TD(locale.format('%.2F',x.tax or 0.0, grouping = True)), TD(locale.format('%.2F',x.sub_total or 0.0, grouping = True))))
            tot += x.sub_total
        inv_foot = TR(TD(B('TOTAL AMOUNT'), _colspan='6', _align='right'), TD(B(str('$ ' + locale.format('%.2F', tot or 0.0, grouping = True)))))
        inv_body = TBODY(*inv_row)
        inv_table = TABLE(*[inv_head, inv_body, inv_foot], _width = '100%', _class='table')
        
        #ref_table = ''
        #inv_table = SQLFORM.grid(db.customer_order.user_id == auth.user, orderby = ~db.customer_order.date_order)
    else:
        ref_table = show_empty_cart()
        inv_table = show_empty_items()
    return dict(ref_table = ref_table, inv_table = inv_table)

      
def remake_reload_script(tag, timeout=None): # tag = '#show_2'
    return '''
        var jelement = $("%s");
        var element = jelement.get(0);
        var statement = "jQuery('%s').get(0).reload();";
        clearInterval(element.timing); // stop auto-reloading
        ''' % (tag, tag) + \
        (timeout and '''
        element.timeout = %s000;
        element.timing = setInterval(statement, %s000); // start reloading
        ''' % (timeout, timeout) or '')

def thankyou():
    return locals()

def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/manage_users (requires membership in
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """

    return dict(form=auth())

@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


