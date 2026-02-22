"""
API routes for RESTful endpoints
"""
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app import db
from app.models.lost_item import LostItem
from app.models.found_item import FoundItem
from app.models.match import Match
from app.utils.helpers import role_required

api_bp = Blueprint('api', __name__)

@api_bp.route('/lost-items', methods=['GET'])
@login_required
def get_lost_items():
    """Get lost items (user's own items)"""
    items = LostItem.query.filter_by(user_id=current_user.id).all()
    return jsonify([{
        'id': item.id,
        'item_name': item.item_name,
        'category': item.category,
        'status': item.status,
        'date_lost': item.date_lost.isoformat() if item.date_lost else None,
        'created_at': item.created_at.isoformat() if item.created_at else None
    } for item in items])

@api_bp.route('/found-items', methods=['GET'])
@login_required
@role_required('staff', 'admin')
def get_found_items():
    """Get found items (staff/admin only)"""
    items = FoundItem.query.all()
    return jsonify([{
        'id': item.id,
        'item_name': item.item_name,
        'category': item.category,
        'status': item.status,
        'date_found': item.date_found.isoformat() if item.date_found else None,
        'priority_flag': item.priority_flag
    } for item in items])

@api_bp.route('/matches/<int:lost_item_id>', methods=['GET'])
@login_required
def get_matches(lost_item_id):
    """Get matches for a lost item"""
    lost_item = LostItem.query.get_or_404(lost_item_id)
    
    # Verify ownership
    if lost_item.user_id != current_user.id and not current_user.is_staff():
        return jsonify({'error': 'Unauthorized'}), 403
    
    matches = Match.query.filter_by(lost_item_id=lost_item_id)\
        .order_by(Match.score.desc()).all()
    
    return jsonify([{
        'id': match.id,
        'found_item_id': match.found_item_id,
        'found_item_name': match.found_item.item_name,
        'score': match.score,
        'status': match.status,
        'created_at': match.created_at.isoformat() if match.created_at else None
    } for match in matches])
