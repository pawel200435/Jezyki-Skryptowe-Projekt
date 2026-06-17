from flask import Blueprint, render_template, request
from app.models import Warning, Product
import re

ui_bp = Blueprint('ui', __name__)

def is_valid_email(email):
    email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$' # test@test.com
    return re.match(email_pattern, email) is not None

@ui_bp.route('/')
def index():
    """
    Renders the main dashboard page.
    Fetches the 10 most recent food warnings to display on initial application load.
    """
    # Fetch latest warnings sorted by publication date descending
    initial_alerts = Warning.query.order_by(Warning.publication_date.desc()).limit(10).all()

    # Pass the initial alerts to the main index template
    return render_template('pages/index.html', alerts=initial_alerts)

@ui_bp.route('/search')
def search_alerts():
    """
    Handles live-search requests triggered by HTMX.
    Filters warnings by product name and returns an HTML partial block.
    """
    search_query = request.args.get('q','').strip()
    if search_query:
        # Filter database records by product_name (ilike is case-insensitive)
        filtered_alerts = Warning.query.join(Product).filter(Product.product_name.ilike(f'%{search_query}%')).all()
    else:
        # If the search field is cleared, get the 10 most recent warnings
        filtered_alerts = Warning.query.order_by(Warning.publication_date.desc()).limit(10).all()
    
    return render_template('partials/search_results.html', alerts=filtered_alerts)

@ui_bp.route('/ui/newsletter/subscribe', methods=['POST'])
def subscirbe():
    email = request.form.get('email').strip()
    
    if not email or not is_valid_email(email):
        return render_template('partials/email_alert.html', 
                               alert_type="red", 
                               message="Podano niepoprawny adres e-mail!")
    
    #TD: function which adds email to database
    return render_template('partials/email_alert.html', 
                               alert_type="green", 
                               message=f'Dodano adress do newslettera')
    
@ui_bp.route('/ui/newsletter/unsubscribe', methods=['POST'])
def unsubscirbe():
    email = request.form.get('email').strip()
    
    if not email or not is_valid_email(email):
        return render_template('partials/email_alert.html', 
                               alert_type="red", 
                               message="Podano niepoprawny adres e-mail!")
    
    #TD: function which removes email to database
    return render_template('partials/email_alert.html', 
                               alert_type="blue", 
                               message=f'Wypisano adres z newslettera')