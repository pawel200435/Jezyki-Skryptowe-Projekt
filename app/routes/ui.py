from flask import Blueprint, render_template, request, abort
from app.models import db, Warning, Product, Subscriber
from datetime import datetime
from sync_rss import sync_warnings_to_db
from app.utils.validators import is_valid_email

ui_bp = Blueprint('ui', __name__)

@ui_bp.route('/')
def index():
    """
    Renders the main dashboard page.
    Fetches the 10 most recent food warnings to display on initial application load.
    """
    # Fetch latest warnings sorted by publication date descending
    initial_alerts = Warning.query.order_by(Warning.publication_date.desc()).limit(10).all()

    #time for displaying information about last data refresh
    current_time = datetime.now().strftime('%H:%M')

    # Pass the initial alerts to the main index template
    return render_template('pages/index.html', alerts=initial_alerts, last_sync=current_time)

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
    
    #function which adds email to database
    new_sub = Subscriber(
        email=email
    )
    db.session.add(new_sub)
    db.session.commit()

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
    
    #function which deactivate subscriber
    subscriber = Subscriber.query.filter_by(email = email).first()
    if subscriber:
        subscriber.is_active = False
    db.session.commit()


    return render_template('partials/email_alert.html', 
                               alert_type="blue", 
                               message=f'Anulowano subskrypcje')
    
@ui_bp.route('/ui/export', methods=['POST'])
def export_warnings():
    selected_ids = request.form.getlist('alert_ids')
    
    warnings =  Warning.query.filter(Warning.wID.in_(selected_ids)).all()
    
    #TD: IMPLEMENTS FUNCIONS WHICH EXPORTS WARNINGS TO CSV/JSON FILE
    
    return render_template('partials/toast_success.html', notification = {'message': 'Poprawnie wyeksportowano zaznaczone dane'})

@ui_bp.route('/ui/warning/<int:warning_id>')
def get_warining_details(warning_id):
    warning = Warning.query.filter_by(wID=warning_id).first()
    
    # if waring doesnt exist return 404 error
    if not warning:
        abort(404)
        
    return render_template('partials/warning_detail_modal.html', warning=warning)

@ui_bp.route('/refresh', methods=['POST'])
def refresh_data():
    """
    Triggers the RSS sync script and returns the updated timestamp button.
    """
    sync_warnings_to_db()
    current_time = datetime.now().strftime('%H:%M')
    return render_template('partials/sync_button.html', last_sync=current_time)