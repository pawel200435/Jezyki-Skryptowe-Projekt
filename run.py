import os
import webview
from flask import Flask
from dotenv import load_dotenv

load_dotenv()
# enums import
from app.enums.TemplatesNames import TemplatesNames
from app.enums.WindowProperties import WindowProperties

# database instance import
from app.models import db

# improt blueprints with subpages
from app.routes.ui import ui_bp

# direct paths config
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
TEMPLATE_FOLDER_PATH = os.path.join(BASE_DIR, 'app', 'templates')
STATIC_FOLDER_PATH = os.path.join(BASE_DIR, 'app', 'static')

app = Flask(
    __name__, 
    template_folder=TEMPLATE_FOLDER_PATH,
    static_folder=STATIC_FOLDER_PATH
)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database with the current Flask app instance
db.init_app(app) 

# getting paths from ui.py
app.register_blueprint(ui_bp)

if __name__ == '__main__':
    #creating desktop window
    webview.create_window(
        title=WindowProperties.NAME.value, 
        url=app,
        width=WindowProperties.WIDTH.value,
        height=WindowProperties.HEIGHT.value,
        resizable=WindowProperties.RESIZABLE.value,
        min_size=WindowProperties.MIN_SIZE.value
    )

    webview.start()