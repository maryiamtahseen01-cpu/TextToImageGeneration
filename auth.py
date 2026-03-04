from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app import db, bcrypt
from models import User
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        # Validate input
        if not data or not data.get('email') or not data.get('password') or not data.get('name'):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Check if user already exists
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user:
            return jsonify({'error': 'User already exists'}), 400
        
        # Create new user
        hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
        
        user = User(
            name=data['name'],
            email=data['email'],
            password_hash=hashed_password
        )
        
        db.session.add(user)
        db.session.commit()
        
        # Create access token
        access_token = create_access_token(identity=user.id)
        
        return jsonify({
            'status': 'success',
            'message': 'User created successfully',
            'user': user.to_dict(),
            'token': access_token
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        # Validate input
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password required'}), 400
        
        # Find user
        user = User.query.filter_by(email=data['email']).first()
        
        if not user or not bcrypt.check_password_hash(user.password_hash, data['password']):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        if not user.is_active:
            return jsonify({'error': 'Account is deactivated'}), 403
        
        # Create access token
        access_token = create_access_token(identity=user.id)
        
        return jsonify({
            'status': 'success',
            'message': 'Login successful',
            'user': user.to_dict(),
            'token': access_token
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'status': 'success',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/update-profile', methods=['PUT'])
@jwt_required()
def update_profile():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        if 'name' in data:
            user.name = data['name']
        
        if 'email' in data:
            # Check if email is already taken by another user
            existing_user = User.query.filter_by(email=data['email']).first()
            if existing_user and existing_user.id != user.id:
                return jsonify({'error': 'Email already in use'}), 400
            user.email = data['email']
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Profile updated successfully',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500