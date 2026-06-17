from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

db = SQLAlchemy()

class Warning(db.Model):
    __tablename__ = "warnings"
    wID = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    link = db.Column(db.String(500), nullable=False)
    publication_date = db.Column(db.DateTime)
    danger = db.Column(db.Text)
    brand = db.Column(db.String(255))
    recommendations = db.Column(db.Text)

    # relations: One Warning -> Many Products, One Warning -> Many Images
    # cascade="all, delete-orphan" ensures that if a warning is deleted, its products and images are also removed
    products = db.relationship('Product', backref='warning', lazy=True, cascade="all, delete-orphan")
    images = db.relationship('Image', backref='warning', lazy=True, cascade="all, delete-orphan")
    #warning.products, warning.images returns list of products/images

class Product(db.Model):
    __tablename__ = 'products'
    pID = db.Column(db.Integer, primary_key=True)
    wID = db.Column(db.Integer, db.ForeignKey('warnings.wID'), nullable=False)
    product_name = db.Column(db.String(500), nullable=False)
    batch = db.Column(db.String(255))

class Image(db.Model):
    __tablename__ = 'images'
    iID = db.Column(db.Integer, primary_key=True)
    wID = db.Column(db.Integer, db.ForeignKey('warnings.wID'), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    alt_desc = db.Column(db.String(500))

class Subscriber(db.Model):
    __tablename__ = 'subscribers'
    sID = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    enrollment_date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    is_active = db.Column(db.Boolean, default=True)

