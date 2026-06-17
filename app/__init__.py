import os
from flask import Flask
from dotenv import load_dotenv
# database instance import
from app.models import db
# improt blueprints
from app.routes.ui import ui_bp

def create_app():
    """
    Application Factory: creates and configures flask application
    """
    load_dotenv()
    CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))
    TEMPLATE_FOLDER_PATH = os.path.join(CURRENT_DIR, 'templates')
    STATIC_FOLDER_PATH = os.path.join(CURRENT_DIR, 'static')

    app = Flask(
        __name__,
        template_folder=TEMPLATE_FOLDER_PATH,
        static_folder=STATIC_FOLDER_PATH
    )

    #DB configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize the database with the current Flask app instance
    db.init_app(app) 
    # Register blueprints
    app.register_blueprint(ui_bp)

    return app