from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from models import PromptHistory
from datetime import datetime, timedelta

history_bp = Blueprint('history', __name__)

@history_bp.route('', methods=['GET'])
@jwt_required()
def get_history():
    try:
        user_id = get_jwt_identity()
        
        # Get filter parameters
        tab = request.args.get('tab', 'all')
        search = request.args.get('search', '')
        
        # Base query
        query = PromptHistory.query.filter_by(user_id=user_id)
        
        # Apply tab filter
        now = datetime.utcnow()
        if tab == 'today':
            today = now.date()
            query = query.filter(db.func.date(PromptHistory.created_at) == today)
        elif tab == 'yesterday':
            yesterday = (now - timedelta(days=1)).date()
            query = query.filter(db.func.date(PromptHistory.created_at) == yesterday)
        elif tab == 'week':
            week_ago = now - timedelta(days=7)
            query = query.filter(PromptHistory.created_at >= week_ago)
        # 'all' shows everything
        
        # Apply search filter
        if search:
            query = query.filter(PromptHistory.prompt.ilike(f'%{search}%'))
        
        # Get results
        history = query.order_by(PromptHistory.created_at.desc()).all()
        
        return jsonify({
            'status': 'success',
            'history': [item.to_dict() for item in history]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@history_bp.route('', methods=['DELETE'])
@jwt_required()
def clear_history():
    try:
        user_id = get_jwt_identity()
        
        # Delete all history for user
        PromptHistory.query.filter_by(user_id=user_id).delete()
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'History cleared successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@history_bp.route('/<int:history_id>', methods=['DELETE'])
@jwt_required()
def delete_history_item(history_id):
    try:
        user_id = get_jwt_identity()
        history_item = PromptHistory.query.filter_by(id=history_id, user_id=user_id).first()
        
        if not history_item:
            return jsonify({'error': 'History item not found'}), 404
        
        db.session.delete(history_item)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'History item deleted'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500