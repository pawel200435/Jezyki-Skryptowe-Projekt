import os
from flask import Flask
from app.models import db 
from dotenv import load_dotenv

load_dotenv() #Loading from .env

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    db.create_all() #Reads models.py and create tables that do not exist in the database
    print("Succesfully created tables")