from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from models import Template

templates_bp = Blueprint('templates', __name__)

@templates_bp.route('', methods=['GET'])
@jwt_required()
def get_templates():
    try:
        user_id = get_jwt_identity()
        
        templates = Template.query.filter_by(user_id=user_id)\
            .order_by(Template.created_at.desc())\
            .all()
        
        return jsonify({
            'status': 'success',
            'templates': [template.to_dict() for template in templates]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@templates_bp.route('', methods=['POST'])
@jwt_required()
def create_template():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or not data.get('name') or not data.get('prompt'):
            return jsonify({'error': 'Name and prompt are required'}), 400
        
        template = Template(
            user_id=user_id,
            name=data['name'],
            prompt=data['prompt'],
            style=data.get('style', 'realistic'),
            size=data.get('size', '512x512')
        )
        
        db.session.add(template)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Template saved successfully',
            'template': template.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@templates_bp.route('/<int:template_id>', methods=['GET'])
@jwt_required()
def get_template(template_id):
    try:
        user_id = get_jwt_identity()
        template = Template.query.filter_by(id=template_id, user_id=user_id).first()
        
        if not template:
            return jsonify({'error': 'Template not found'}), 404
        
        return jsonify({
            'status': 'success',
            'template': template.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@templates_bp.route('/<int:template_id>', methods=['PUT'])
@jwt_required()
def update_template(template_id):
    try:
        user_id = get_jwt_identity()
        template = Template.query.filter_by(id=template_id, user_id=user_id).first()
        
        if not template:
            return jsonify({'error': 'Template not found'}), 404
        
        data = request.get_json()
        
        if 'name' in data:
            template.name = data['name']
        if 'prompt' in data:
            template.prompt = data['prompt']
        if 'style' in data:
            template.style = data['style']
        if 'size' in data:
            template.size = data['size']
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Template updated successfully',
            'template': template.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@templates_bp.route('/<int:template_id>', methods=['DELETE'])
@jwt_required()
def delete_template(template_id):
    try:
        user_id = get_jwt_identity()
        template = Template.query.filter_by(id=template_id, user_id=user_id).first()
        
        if not template:
            return jsonify({'error': 'Template not found'}), 404
        
        db.session.delete(template)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Template deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500