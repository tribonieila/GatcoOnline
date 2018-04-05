@auth.requires_membership('Manager')
def auto_parts():
    db.auto_part.id.readable = False
    grid = SQLFORM.grid(db.auto_part,
        user_signature=False, csv = False, maxtextlength=40) 
    #grid.element('.web2py_counter',replace=None)
    return dict(grid = grid)

@auth.requires_membership('Manager')
def customer():
	return locals()

CD = A("Deliver Address", _href=URL("#"))
IR = A("Billing Address", _href=URL("#"))

links = [lambda row: A('Quotation Request', _href=URL('quotation_request'))]
@auth.requires_membership('Manager')
def view_customer():
	n = 0
	row = []
	s = []
	#{{=A('click me', callback=URL('myaction'), target="t")}}
	#<div id="t"><div>
	# callback=URL('show'), _target='#collapseExample'
	#links = A('Show Request',_class = 'btn btn-default btn-xs',_href='#collapseExample',_role='button', **{'_data-toggle':'collapse', '_aria-controls':'collapseExample'})
	#links = DIV(LABEL(INPUT(_type='checkbox'),'Deliver to a different address?',
	#	**{'_data-toggle':'collapse', '_data-target':'#collapseExample'}), _class='checkbox')
	#links = A('Show Request',_class = 'btn btn-default btn-xs',callback=URL('show'), _target='collapseExample',_role='button', **{'_data-toggle':'collapse', '_aria-controls':'collapseExample'})
	#fields = [db.auth_user.last_name, db.auth_user.first_name, db.auth_user.email, db.billing_address.contact_no, db.billing_address.country]
	
	query = db(db.auth_user.id != 1).select(db.auth_user.ALL)#last_name, 
		#db.auth_user.first_name, db.auth_user.email)
	head = THEAD(TR(TH('No'),TH('Last Name'), TH('First Name'), TH('E-Mail'), TH(_colspan='3')))
	for rows in query:
		n += 1
		QR = A("Quotation Request", _href=URL('quotation_request', args=rows.id))
		row.append(TR(TD(n),TD((rows.last_name).upper()), TD((rows.first_name).upper()), 
			TD(rows.email), TD(CD), TD(IR), TD(QR)))
		body = TBODY(*row)
	table = TABLE(*[head, body], _class='table table-condensed')
	return table

def quotation_request():
	return locals()

def quotation_requests():
	table = None
	row_id = request.args(0)
	#response.flash = row_id
	x =  []
	ta = 0
	z=[]
	

	head = THEAD(TR(TH('Doc.No.'),TH('Date'),TH('Part No.'),TH('Description'), TH('Qty.'), TH('Price'), TH('Amount'), TH('Tax'), TH('SubTotal'),TH('Status'), TH()))
	for y in db(db.customer_order.user_id==row_id).select(db.customer_order.ALL, groupby = db.customer_order.tracking_no, orderby=~db.customer_order.tracking_no):
		x.append(TR(TD(y.tracking_no),TD(y.date_order),TD(_colspan='8'),TD()))
		for r in db(db.customer_order.tracking_no == y.tracking_no).select(db.customer_order.ALL):
			ps=A('Post Price', callback=URL('post_price', args=r.id))
			#x.append(TR(TD(),TD(),TD(r.part_no),TD(r.description_id), TD(r.qty),TD(locale.format('%.2F', r.price, grouping=True),_align='right'), TD(locale.format('%.2F',r.amount,grouping=True),_align='right'),TD(locale.format('%.2F',r.tax),_align='right'), TD(locale.format('%.2F',r.sub_total,grouping=True),_align='right'), TD(r.status), TD(ps)))
			x.append(TR(TD(),TD(),TD(r.part_no),TD(r.description_id), TD(r.qty),TD(r.price), TD(r.amount),TD(r.tax), TD(r.sub_total), TD(r.status,_id='status'), TD(ps)))
			total_amount=db.customer_order.sub_total.sum().coalesce_zero()
			total_amount=db(db.customer_order.tracking_no==y.tracking_no).select(total_amount).first()[total_amount]

		x.append(TR(TD(B('Total Amount: '),_colspan='8',_align='right'),TD(B('$ ', locale.format('%.2F',total_amount, grouping=True))),TD(),TD()))
		body = TBODY(x)
		table = show_customer_details()
		table += TABLE(*[head,body],_class='table')
	return table

def post_price():
	query = db(db.customer_order.id == request.args(0)).select().first()
	post = query.update_record(status='Available')
	response.js =  "jQuery('#status').get(0).reload();"
	return post
def show():
	form = DIV(DIV(DIV('tOE THE AL LD'),_class='well'),_class='collapse', _id='collapseExample')
	return form

def show_customer_details():
	y = []
	query = db(db.auth_user.id == request.args(0)).select(db.auth_user.ALL)
	for x in query:
		y.append(TR(TD('Customer: '), TD(x.last_name,' ', x.first_name)))
		body = TBODY(y)
		table = TABLE(*[body],_class='table')
	return locals()