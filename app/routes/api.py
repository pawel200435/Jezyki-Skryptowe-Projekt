from flask import Blueprint, request, jsonify
from app.models import db, Subscriber
from sqlalchemy.exc import IntegrityError
import re

api_bp = Blueprint('api', __name__, url_prefix='/api')

def is_valid_email(email):
    email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$' # test@test.com
    return re.match(email_pattern, email) is not None

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

@api_bp.route('/subscribers/<string:email>', methods=['DELETE'])
def delete_subscriber(email):
    """
    Handles a DELETE request that permanently removes an email address from the subscribers table.
    The email address is provided as a URL path parameter.
    Returns a JSON response with the result and appropriate HTTP status code.
    """
    subscriber = Subscriber.query.filter_by(email=email).first()

    if not subscriber:
        return jsonify({'error': f'Email {email} not found in the database'}), 404

    db.session.delete(subscriber)
    db.session.commit()

    return jsonify({'message': f'Email {email} successfully removed from newsletter'}), 200

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