from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

db = SQLAlchemy()

class Ostrzezenie(db.Model):
    __tablename__ = 'ostrzezenia'
    idO = db.Column(db.Integer, primary_key=True)
    gis_id = db.Column(db.String(500), unique=True)
    tytul = db.Column(db.String(255), nullable=False)
    link_zrodlowy = db.Column(db.String(500))
    data_publikacji = db.Column(db.DateTime)
    zagrozenie = db.Column(db.Text)
    produkt = db.Column(db.String(255))
    marka = db.Column(db.String(255))
    numer_partii = db.Column(db.Text)
    producent = db.Column(db.Text)
    zalecenia = db.Column(db.Text)

    zdjecia = db.relationship('Zdjecie', backref='ostrzezenie', lazy=True, cascade="all, delete-orphan")
    #ostrzezenie.zdjecia and zdjecie.ostrzezenie (getting a list of records)

class Zdjecie(db.Model):
    __tablename__ = 'zdjecia'
    idZ = db.Column(db.Integer, primary_key=True)
    ostrzezenie_id = db.Column(db.Integer, db.ForeignKey('ostrzezenia.idO'), nullable=False)
    url_zdjecia = db.Column(db.String(500), nullable=False)
    opis_alternatywny = db.Column(db.String(500))

class Subskrybent(db.Model):
    __tablename__ = 'subskrybenci'
    idS = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    data_zapisu = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    czy_aktywny = db.Column(db.Boolean, default=True)