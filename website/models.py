from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from sqlalchemy.schema import Index

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, index=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    properties = db.relationship('Property')

class Property(db.Model):
    property_id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(255))
    city = db.Column(db.String(255))
    state = db.Column(db.String(255))
    zip_code = db.Column(db.String(255))
    bedrooms = db.Column(db.Integer)
    bathrooms = db.Column(db.Integer)
    square_footage = db.Column(db.Integer)
    status = db.Column(db.String(255))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)

    def __repr__(self):
        return '<Property %r>' % self.property_id
    
class Tenant(db.Model):
    tenant_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    email = db.Column(db.String(255))
    phone_number = db.Column(db.String(255))
    lease_start_date = db.Column(db.Date)
    lease_end_date = db.Column(db.Date)
    monthly_rent = db.Column(db.Float)
    security_deposit = db.Column(db.Float)
    property_id = db.Column(db.Integer, db.ForeignKey('property.property_id'))

    def __repr__(self):
        return '<Tenant %r>' % self.tenant_id
    
class Payment(db.Model):
    payment_id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenant.tenant_id'))
    property_id = db.Column(db.Integer, db.ForeignKey('property.property_id'))
    date = db.Column(db.Date)
    amount = db.Column(db.Float)
    payment_type = db.Column(db.String(255))

    def __repr__(self):
        return '<Payment %r>' % self.payment_id