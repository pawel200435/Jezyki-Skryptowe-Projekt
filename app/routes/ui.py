from flask import Blueprint, render_template, request, abort
from app.models import db, Warning, Product, Subscriber
from datetime import datetime
from sync_rss import sync_warnings_to_db
from app.utils.validators import is_valid_email
from sqlalchemy import or_, collate

ui_bp = Blueprint('ui', __name__)

BATCH_SIZE = 10

def get_sort_clause(sort_param):
    sort_options = {
        'date_desc': Warning.publication_date.desc(),
        'date_asc': Warning.publication_date.asc(),
        'brand_asc': collate(Warning.brand, 'utf8mb4_polish_ci').asc(),
        'brand_desc': collate(Warning.brand, 'utf8mb4_polish_ci').desc(),
        'product_asc': db.func.min(collate(Product.product_name, 'utf8mb4_polish_ci')).asc(),
        'product_desc': db.func.max(collate(Product.product_name, 'utf8mb4_polish_ci')).desc(),
    }
    return sort_options.get(sort_param, Warning.publication_date.desc())

def build_sorted_query(sort_param):
    """
    Builds a Warning query with the appropriate sort order.
    Product sorting requires an outerjoin and group_by to handle one-to-many relationship.
    """
    if sort_param in ('product_asc', 'product_desc'):
        return Warning.query.outerjoin(Product).group_by(Warning.wID).order_by(get_sort_clause(sort_param))
    return Warning.query.order_by(get_sort_clause(sort_param))

@ui_bp.route('/')
def index():
    """
    Renders the main dashboard page.
    Fetches the 10 most recent food warnings to display on initial application load.
    """
    initial_alerts = Warning.query.order_by(Warning.publication_date.desc()).limit(BATCH_SIZE).all()

    #time for displaying information about last data refresh (auto refresh on app start)
    current_time = datetime.now().strftime('%H:%M')

    total = Warning.query.count()
    has_more = total > BATCH_SIZE

    return render_template('pages/index.html', alerts=initial_alerts, last_sync=current_time,
                           has_more=has_more, next_offset=BATCH_SIZE, current_sort='date_desc')

@ui_bp.route('/search')
def search_alerts():
    """
    Handles live-search requests and filtering triggered by HTMX.
    Filters warnings by product name, brand or danger and returns an HTML partial block.
    Supports sorting via the 'sort' query parameter.
    """
    search_query = request.args.get('q','').strip()
    date_from = request.args.get('date_from', '').strip()
    date_to = request.args.get('date_to', '').strip()
    sort_param = request.args.get('sort', 'date_desc')
    offset = request.args.get('offset', 0, type=int)

    #get all warnings also ones without products 
    query = Warning.query.outerjoin(Product)

    if search_query:
        # Filter database records by product_name, brand or danger (ilike is case-insensitive)
        query = query.filter(or_(
            Product.product_name.ilike(f'%{search_query}%'),
            Warning.brand.ilike(f'%{search_query}%'),
            Warning.danger.ilike(f'%{search_query}%')
        ))

    #Date >= FROM
    if date_from:
        query = query.filter(Warning.publication_date >= date_from)    
    #Date <= TO
    if date_to:
        query = query.filter(Warning.publication_date <= f"{date_to} 23:59:59")
    
    if sort_param in ('product_asc', 'product_desc'):
            query = query.group_by(Warning.wID)
    query = query.order_by(get_sort_clause(sort_param))

    total_matching = query.distinct().count()
    filtered_alerts = query.order_by(Warning.publication_date.desc()).distinct().offset(offset).limit(BATCH_SIZE).all()

    has_more = (offset + BATCH_SIZE) < total_matching
    next_offset = offset + BATCH_SIZE

    #check if request is from load-more
    if request.headers.get('HX-Target') == 'load-more-row':
        return render_template('partials/load_more_response.html', 
                               alerts=filtered_alerts, has_more=has_more, 
                               next_offset=next_offset, current_sort=sort_param)
    #if request is from filtering/searching returns all table
    else:
        return render_template('partials/search_results.html', 
                               alerts=filtered_alerts, has_more=has_more, 
                               next_offset=next_offset, current_sort=sort_param)


@ui_bp.route('/ui/newsletter/subscribe', methods=['POST'])
def subscirbe():
    email = request.form.get('email').strip()
    
    if not email or not is_valid_email(email):
        return render_template('partials/email_alert.html', 
                               alert_type="red", 
                               message="Podano niepoprawny adres e-mail!")
    
    #checking if subsciber exist and reactivate him
    subscriber = Subscriber.query.filter_by(email = email).first()
    if subscriber:
        subscriber.is_active = True

    else:
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
    # this commented return is for excpetion while export failure
    # return render_template('partials/toast_failure.html', notification = {'message': 'Wystąpił błąd przy eksporcie danych'})
    
    return render_template('partials/toast_success.html', notification = {'message': 'Poprawnie wyeksportowano zaznaczone dane'})

@ui_bp.route('/ui/warning/<int:warning_id>')
def get_warining_details(warning_id):
    warning = Warning.query.filter_by(wID=warning_id).first()
    
    # if waring doesnt exist return 404 error
    if not warning:
        abort(404)
        
    return render_template('partials/warning_detail_modal.html', warning=warning)

@ui_bp.route('/ui/refresh', methods=['POST'])
def refresh_data():
    """
    Triggers the RSS sync script and returns the updated timestamp button.
    """
    sync_warnings_to_db()
    current_time = datetime.now().strftime('%H:%M')
    
    sync_button_html = render_template('partials/sync_button.html', last_sync=current_time)
    
    latest_warnings = Warning.query.order_by(Warning.publication_date.desc()).limit(BATCH_SIZE).all()
    total = Warning.query.count()
    has_more = total > BATCH_SIZE
    results_html = render_template('partials/search_results.html', alerts=latest_warnings, oob=True,
                                   has_more=has_more, next_offset=BATCH_SIZE, current_sort='date_desc')
    return sync_button_html + results_html