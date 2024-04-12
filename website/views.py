from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from .models import Property
from . import db
import json

views = Blueprint('views', __name__)
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, SelectField
from wtforms.validators import DataRequired, Length

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


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    return render_template("home.html", user=current_user)

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
        return redirect(url_for('views.home')) 
    return render_template('add.html', form=form)

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
        
        db.session.commit()
        flash('Property updated successfully!', 'success')
        return redirect(url_for('views.home')) 
    return render_template('edit.html', form=form, property=property_to_edit)

