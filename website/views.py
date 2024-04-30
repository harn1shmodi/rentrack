from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from .models import Property, Tenant, Payment
from . import db
import json
from sqlalchemy import *
views = Blueprint('views', __name__)
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, SelectField
from wtforms.validators import DataRequired, Length
import datetime

class PropertyForm(FlaskForm):
    address = StringField('Address', validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired()])
    state = StringField('State', validators=[DataRequired(), Length(min=2, max=2)])
    zip_code = StringField('Zip Code', validators=[DataRequired()])
    bedrooms = IntegerField('Bedrooms') # Add other fields as needed
    bathrooms = IntegerField('Bathrooms')
    square_footage = IntegerField('Square Footage')
    status = StringField('Status')
    submit = SubmitField('Update Property') 

class AddPropertyForm(FlaskForm):
    address = StringField('Address', validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired()])
    state = StringField('State', validators=[DataRequired(), Length(min=2, max=2)])
    zip_code = StringField('Zip Code', validators=[DataRequired()])
    bedrooms = IntegerField('Bedrooms') 
    bathrooms = IntegerField('Bathrooms')
    square_footage = IntegerField('Square Footage')
    status = StringField('Status')
    submit = SubmitField('Add Property')

class AddTenantForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    phone_number = StringField('Phone Number', validators=[DataRequired()])
    lease_start_date = StringField('Lease Start Date', validators=[DataRequired()])
    lease_end_date = StringField('Lease End Date', validators=[DataRequired()])
    monthly_rent = IntegerField('Monthly Rent', validators=[DataRequired()])
    security_deposit = IntegerField('Security Deposit', validators=[DataRequired()])
    submit = SubmitField('Add Tenant')

class AddPaymentForm(FlaskForm):
    date = StringField('Date', validators=[DataRequired()])
    amount = IntegerField('Amount', validators=[DataRequired()])
    payment_type = StringField('Payment Type', validators=[DataRequired()])
    submit = SubmitField('Add Payment')

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    status_filter = request.args.get('status_filter')  # Get filter value
    #db.session.execute(text('INSERT INTO tenant (first_name, last_name, email, phone_number, lease_start_date, lease_end_date, monthly_rent, security_deposit, property_id) VALUES ("John", "Doe", "jahn@doe.com", "1234567890", "2021-01-01", "2021-12-31", 1000, 1000, 1)'))
    #properties_query = select(Property).where(Property.owner_id == current_user.id)
    properties_query = text("""
            SELECT * 
            FROM property 
            LEFT OUTER JOIN tenant
            ON property.property_id=tenant.property_id
            WHERE owner_id = :owner_id
        """)
    avg_rent_query = text("""
            SELECT ROUND(AVG(monthly_rent), 2)
            FROM tenant
            WHERE property_id IN (SELECT
            property_id
            FROM property
            WHERE owner_id = :owner_id)
        """)
    avg_sqft_query = text("""
            SELECT ROUND(AVG(square_footage), 2)
            FROM property
            WHERE owner_id = :owner_id
        """)
    payment_query = text("""
            SELECT property_id, amount, date, payment_type
            FROM payment
            WHERE property_id IN (SELECT
            property_id
            FROM property
            WHERE owner_id = :owner_id)
        """)
    if status_filter == 'Vacant':
        #properties_query = select(Property).where(and_(Property.status == 'Vacant', Property.owner_id == current_user.id))
        properties_query = text("""
            SELECT * 
            FROM property 
            LEFT OUTER JOIN tenant
            ON property.property_id=tenant.property_id
            WHERE owner_id = :owner_id
            AND status = "Vacant"
        """)
        avg_rent_query = text("""
            SELECT ROUND(AVG(monthly_rent), 2)
            FROM tenant
            WHERE property_id IN (SELECT
            property_id
            FROM property
            WHERE owner_id = :owner_id
            AND status = "Vacant")
        """)
        avg_sqft_query = text("""
                SELECT ROUND(AVG(square_footage), 2)
                FROM property
                WHERE owner_id = :owner_id
                AND status = "Vacant"
            """)
        payment_query = text("""
            SELECT property_id, amount, date, payment_type
            FROM payment
            WHERE property_id IN (SELECT
            property_id
            FROM property
            WHERE owner_id = :owner_id)
        """)

    elif status_filter == 'Occupied':
        #properties_query = select(Property).where(and_(Property.status == 'Occupied', Property.owner_id == current_user.id))
        properties_query = text("""
            SELECT * 
            FROM property 
            LEFT OUTER JOIN tenant
            ON property.property_id=tenant.property_id
            WHERE owner_id = :owner_id
            AND status = "Occupied"
        """)
        avg_rent_query = text("""
            SELECT ROUND(AVG(monthly_rent), 2)
            FROM tenant
            WHERE property_id IN (SELECT
            property_id
            FROM property
            WHERE owner_id = :owner_id
            AND status = "Occupied")
        """)
        avg_sqft_query = text("""
                SELECT ROUND(AVG(square_footage), 2)
                FROM property
                WHERE owner_id = :owner_id
                AND status = "Occupied"
            """)
        payment_query = text("""
            SELECT property_id, amount, date, payment_type
            FROM payment
            WHERE property_id IN (SELECT
            property_id
            FROM property
            WHERE owner_id = :owner_id)
        """)
        
    
    payments = db.session.execute(payment_query, {'owner_id': current_user.id})    
    result = db.session.execute(properties_query, {'owner_id': current_user.id})
    avg_rent = db.session.execute(avg_rent_query, {'owner_id': current_user.id})
    avg_sqft = db.session.execute(avg_sqft_query, {'owner_id': current_user.id})
    status = db.session.execute(text('SELECT DISTINCT status FROM property WHERE owner_id = :owner_id'), {'owner_id': current_user.id})

    return render_template('home.html', properties=result, status=status, avg_rent=avg_rent, avg_sqft=avg_sqft, payments=list(payments)) #current_user.properties

@views.route('/property/add', methods=['GET', 'POST'])
@login_required
def add_property():
    form = AddPropertyForm()
    if form.validate_on_submit():
        new_property = Property(
            address=form.address.data,
            city=form.city.data,
            state=form.state.data,
            zip_code=form.zip_code.data,
            bedrooms=form.bedrooms.data,
            bathrooms=form.bathrooms.data,
            square_footage=form.square_footage.data,
            status=form.status.data,
            owner_id=current_user.id
        )
        db.session.add(new_property)
        db.session.commit()
        flash('Property added successfully!', 'success')
        if new_property.status == 'Vacant':
            return redirect(url_for('views.home'))
        else:
            return redirect(url_for('views.add_tenant', property_id=new_property.property_id)) 
    return render_template('add.html', form=form)

@views.route('/<int:property_id>/add_tenant', methods=['GET', 'POST'])
@login_required
def add_tenant(property_id):
    form = AddTenantForm()
    if form.validate_on_submit():
        new_tenant = Tenant(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            phone_number=form.phone_number.data,
            lease_start_date=datetime.datetime.strptime(form.lease_start_date.data, '%m/%d/%Y').date(),
            lease_end_date=datetime.datetime.strptime(form.lease_end_date.data, '%m/%d/%Y').date(),
            monthly_rent=form.monthly_rent.data,
            security_deposit=form.security_deposit.data,
            property_id=property_id
        )
        db.session.add(new_tenant)
        db.session.commit()
        flash('Tenant added successfully!', 'success')
        return redirect(url_for('views.home')) 
    return render_template('add_tenant.html', form=form)

@views.route('/<int:property_id>/<int:tenant_id>/add_payment', methods=['GET', 'POST'])
@login_required
def add_payment(property_id, tenant_id):
    form = AddPaymentForm()
    if form.validate_on_submit():
        new_payment = Payment(
            date=datetime.datetime.strptime(form.date.data, '%m/%d/%Y').date(),
            amount=form.amount.data,
            payment_type=form.payment_type.data,
            property_id=property_id,
            tenant_id=tenant_id
        )
        db.session.add(new_payment)
        db.session.commit()
        flash('Payment added successfully!', 'success')
        return redirect(url_for('views.home')) 
    return render_template('add_payment.html', form=form)

@views.route('/delete-property', methods=['POST'])
def delete_property():  
    prop = json.loads(request.data) # this function expects a JSON from the INDEX.js file 
    print(prop)
    propId = prop['propId']
    prop = Property.query.get(propId)
    if prop:
        if prop.owner_id == current_user.id:
            db.session.delete(prop)
            db.session.commit()

    return jsonify({})

@views.route("/property/<int:property_id>/edit'", methods=['GET', 'POST'])
def edit_property(property_id):
    property_to_edit = Property.query.get_or_404(property_id)  
    form = PropertyForm(obj=property_to_edit)  # Populate the form

    if form.validate_on_submit():
        property_to_edit.address = form.address.data
        property_to_edit.city = form.city.data
        property_to_edit.state = form.state.data
        property_to_edit.zip_code = form.zip_code.data
        property_to_edit.bedrooms = form.bedrooms.data
        property_to_edit.bathrooms = form.bathrooms.data
        property_to_edit.square_footage = form.square_footage.data
        property_to_edit.status = form.status.data
        
        if property_to_edit.status == 'Vacant':
            tenant_query = text('DELETE FROM tenant WHERE property_id = :property_id')
            db.session.execute(tenant_query, {'property_id': property_id})
            payments = Payment.query.filter_by(property_id=property_id).all()
            payments_query = text('DELETE FROM payment WHERE property_id = :property_id')
            db.session.execute(payments_query, {'property_id': property_id})
            db.session.commit()
            flash('Property updated successfully!', 'success')
            return redirect(url_for('views.home')) 
        else:
            db.session.commit()
            return redirect(url_for('views.add_tenant', property_id=property_id))

    return render_template('edit.html', form=form, property=property_to_edit)

