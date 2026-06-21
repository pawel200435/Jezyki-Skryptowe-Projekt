from flask import Blueprint, request, jsonify, abort
from app.models import db, Subscriber, Warning, Product
from sqlalchemy.exc import IntegrityError
from app.utils.validators import is_valid_email, validate_and_parse_dates

api_bp = Blueprint('api', __name__, url_prefix='/api')

def warning_to_dict(warning):
    return {
        'id': warning.wID,
        'title': warning.title,
        'link': warning.link,
        'publication_date': warning.publication_date.isoformat() if warning.publication_date else None,
        'danger': warning.danger,
        'brand': warning.brand,
        'recommendations': warning.recommendations,
        'products': [
            {'name': p.product_name, 'batch': p.batch}
            for p in warning.products
        ],
        'images': [
            {'url': i.img_url, 'alt': i.alt_desc}
            for i in warning.images
        ]
    }

@api_bp.route('/subscribers', methods=['POST'])
def add_subscriber():
    """
    Handles a POST request that adds a new email address to the subscribers table.
    Expects a JSON body with an 'email' field.
    Returns a JSON response with the result and appropriate HTTP status code.
    """
    data = request.get_json()

    if not data or 'email' not in data:
        return jsonify({'error': 'Email is required'}), 400

    email = data.get('email').strip()

    if not email or not is_valid_email(email):
        return jsonify({'error': 'Invalid email address'}), 400

    new_subscriber = Subscriber(email=email)
    db.session.add(new_subscriber)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Email already exists in the database'}), 409

    return jsonify({'message': f'Email {email} successfully added to newsletter'}), 201

@api_bp.route('/subscribers/<string:email>/force', methods=['DELETE'])
def hard_delete_subscriber(email):
    """
    Handles a DELETE request that permanently removes an email address from the database.
    Returns a JSON response with the result and appropriate HTTP status code.
    """
    subscriber = Subscriber.query.filter_by(email=email).first()

    if not subscriber:
        return jsonify({'error': f'Email {email} not found in the database'}), 404

    db.session.delete(subscriber)
    db.session.commit()

    return jsonify({'message': f'Email {email} permanently deleted from the database'}), 200

@api_bp.route('/subscribers/<string:email>', methods=['DELETE'])
def deactivate_subscriber(email):
    """
    Handles a DELETE request that performs a soft delete.
    Instead of removing the record, it sets the subscriber's status to inactive.
    Returns a JSON response with the result and appropriate HTTP status code.
    """
    subscriber = Subscriber.query.filter_by(email=email).first()

    if not subscriber:
        return jsonify({'error': f'Email {email} not found in the database'}), 404
    
    if not subscriber.is_active:
        return jsonify({'message': f'Email {email} is already deactivated'}), 200
    
    subscriber.is_active = False
    db.session.commit()
    return jsonify({'message': f'Email {email} successfully deactivated (soft delete)'}), 200

@api_bp.route('/subscribers/<string:email>', methods=['PUT'])
def update_subscriber(email):
    """
    Handles a PUT request that updates an existing email address in the subscribers table.
    The current email address is provided as a URL path parameter.
    Expects a JSON body with a 'new_email' field.
    Returns a JSON response with the result and appropriate HTTP status code.
    """
    data = request.get_json()

    if not data or 'new_email' not in data:
        return jsonify({'error': 'New email is required'}), 400

    new_email = data.get('new_email').strip()

    if not new_email or not is_valid_email(new_email):
        return jsonify({'error': 'Invalid email address'}), 400

    subscriber = Subscriber.query.filter_by(email=email).first()

    if not subscriber:
        return jsonify({'error': f'Email {email} not found in the database'}), 404

    subscriber.email = new_email

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Email already exists in the database'}), 409

    return jsonify({'message': f'Email successfully updated from {email} to {new_email}'}), 200

@api_bp.route('/warnings', methods=['GET'])
def get_alerts():
    """
    Handles a GET request that returns all alerts from the database in JSON format.
    Results are sorted by publication date descending (newest first).
    Returns a JSON array of all warning records.
    """
    alerts = Warning.query.order_by(Warning.publication_date.desc()).all()

    return jsonify([warning_to_dict(alert) for alert in alerts]), 200

@api_bp.route('/warnings/search', methods=['GET'])
def filter_alerts():
    """
    Handles a GET request that filters alerts based on query parameters.
    Supports filtering by: danger, brand, product_name, date_from, date_to.
    Multiple filters can be combined in a single request.
    Returns a JSON array of matching warning records.
    """
    danger = request.args.get('danger', '').strip()
    brand = request.args.get('brand', '').strip()
    product_name = request.args.get('product_name', '').strip()
    date_from_str = request.args.get('date_from', '').strip()
    date_to_str = request.args.get('date_to', '').strip()

    #dates validation
    date_from_obj, date_to_obj, error_msg = validate_and_parse_dates(date_from_str, date_to_str)
    if error_msg:
        return jsonify({'error': error_msg}), 400

    query = Warning.query

    if danger:
        query = query.filter(Warning.danger.ilike(f'%{danger}%'))
    if brand:
        query = query.filter(Warning.brand.ilike(f'%{brand}%'))
    if product_name:
        query = query.outerjoin(Product).filter(Product.product_name.ilike(f'%{product_name}%'))
    if date_from_obj:
        query = query.filter(Warning.publication_date >= date_from_obj)
    if date_to_obj:
        query = query.filter(Warning.publication_date <= date_to_obj)

    alerts = query.order_by(Warning.publication_date.desc()).all()

    return jsonify([warning_to_dict(alert) for alert in alerts]), 200


@api_bp.route('/warnings/<int:warning_id>')
def get_warning_by_id(warning_id):
    """
    Retrieves a specific warning by its ID.
    Returns 404 if the warning does not exist.
    """
    warning = Warning.query.filter_by(wID = warning_id).first()
    if warning is None:
        abort(404)

    return jsonify(warning_to_dict(warning)), 200

@api_bp.route('/warnings/<int:warning_id>/products')
def get_warning_products(warning_id):
    """
    Retrieves products associated with a specific warning ID.
    Supports optional filtering by product_name via query parameters.
    Returns both the warning context and the filtered products.
    """
    warning = Warning.query.filter_by(wID = warning_id).first()
    if warning is None:
        abort(404)
    
    product_name = request.args.get('product_name', '').strip()

    query = Product.query.filter_by(wID=warning_id)
    if product_name:
        query = query.filter(Product.product_name.ilike(f'%{product_name}%'))

    filtered_products = query.all()
    response_data = {
        'warning_id': warning.wID,
        'warning_title': warning.title,
        'warning_link': warning.link,
        'filtered_products': [{'name': p.product_name, 'batch': p.batch} for p in filtered_products]
    }
    
    return jsonify(response_data), 200

@api_bp.route('/warnings/<int:warning_id>/images')
def get_warning_images(warning_id):
    """
    Retrieves only the images associated with a specific warning ID.
    """
    warning = Warning.query.filter_by(wID = warning_id).first()
    if warning is None:
        abort(404)
    
    images_data = [{'url': img.img_url, 'alt': img.alt_desc} for img in warning.images]
    
    return jsonify({
        'warning_id': warning.wID,
        'image_count': len(images_data),
        'images': images_data
    }), 200