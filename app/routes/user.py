"""
User routes (student dashboard, lost item reporting)
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.lost_item import LostItem
from app.models.match import Match
from app.models.claim import Claim
from app.models.notification import Notification
from app.services.lost_found_matcher import LostFoundMatcher
from app.services.notification_service import NotificationService
from app.services.qr_service import QRService
from app.utils.helpers import save_uploaded_file
from datetime import datetime

user_bp = Blueprint('user', __name__)

@user_bp.route('/dashboard')
@login_required
def dashboard():
    """Student dashboard"""
    # Get user's lost items
    lost_items = LostItem.query.filter_by(user_id=current_user.id)\
        .order_by(LostItem.created_at.desc()).limit(10).all()
    
    # Get pending matches
    matches = Match.query.join(LostItem)\
        .filter(LostItem.user_id == current_user.id)\
        .filter(Match.status == 'suggested')\
        .order_by(Match.score.desc()).limit(5).all()
    
    # Get unread notifications
    unread_count = NotificationService.get_unread_count(current_user.id)
    
    # Statistics
    total_lost = LostItem.query.filter_by(user_id=current_user.id).count()
    matched_items = LostItem.query.filter_by(user_id=current_user.id, status='matched').count()
    claimed_items = LostItem.query.filter_by(user_id=current_user.id, status='claimed').count()
    
    return render_template('user/dashboard.html',
                         lost_items=lost_items,
                         matches=matches,
                         unread_count=unread_count,
                         total_lost=total_lost,
                         matched_items=matched_items,
                         claimed_items=claimed_items)

@user_bp.route('/report-lost', methods=['GET', 'POST'])
@login_required
def report_lost():
    """Report a lost item"""
    if request.method == 'POST':
        item_name = request.form.get('item_name')
        description = request.form.get('description')
        category = request.form.get('category')
        color = request.form.get('color')
        date_lost = request.form.get('date_lost')
        location_lost = request.form.get('location_lost')
        image = request.files.get('image')
        
        # Validation
        if not item_name or not category or not date_lost:
            flash('Item name, category, and date lost are required', 'error')
            return render_template('user/report_lost.html')
        
        try:
            date_lost_obj = datetime.strptime(date_lost, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format', 'error')
            return render_template('user/report_lost.html')
        
        # Save image if provided
        image_path = None
        if image:
            image_path = save_uploaded_file(image)
        
        # Create lost item
        lost_item = LostItem(
            user_id=current_user.id,
            item_name=item_name,
            description=description,
            category=category,
            color=color,
            date_lost=date_lost_obj,
            location_lost=location_lost,
            image_path=image_path,
            status='pending'
        )
        
        db.session.add(lost_item)
        db.session.commit()
        
        # Run AI matching
        matcher = LostFoundMatcher()
        from app.models.found_item import FoundItem
        found_items = FoundItem.query.filter_by(status='available').all()
        
        # Convert to dict format for matcher
        found_items_dict = [{
            'id': item.id,
            'item_name': item.item_name,
            'description': item.description or '',
            'category': item.category,
            'color': item.color or ''
        } for item in found_items]
        
        lost_item_dict = {
            'id': lost_item.id,
            'item_name': lost_item.item_name,
            'description': lost_item.description or '',
            'category': lost_item.category,
            'color': lost_item.color or ''
        }
        
        matches = matcher.find_matches(lost_item_dict, found_items_dict, threshold=50.0)
        
        # Create match records
        for match_data in matches[:5]:  # Top 5 matches
            match = Match(
                lost_item_id=lost_item.id,
                found_item_id=match_data['found_item_id'],
                score=match_data['score'],
                status='suggested'
            )
            db.session.add(match)
            
            # Notify user
            NotificationService.notify_match_found(
                current_user.id,
                lost_item.item_name,
                match_data['score']
            )
        
        db.session.commit()
        
        flash('Lost item reported successfully! We will notify you if we find a match.', 'success')
        return redirect(url_for('user.dashboard'))
    
    return render_template('user/report_lost.html')

@user_bp.route('/my-items')
@login_required
def my_items():
    """View all lost items"""
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', 'all')
    
    query = LostItem.query.filter_by(user_id=current_user.id)
    
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)
    
    lost_items = query.order_by(LostItem.created_at.desc())\
        .paginate(page=page, per_page=10, error_out=False)
    
    return render_template('user/my_items.html', lost_items=lost_items, status_filter=status_filter)

@user_bp.route('/matches')
@login_required
def matches():
    """Tinder-style view: show suggested matches one by one and list history below"""
    suggested_matches = Match.query.join(LostItem)\
        .filter(LostItem.user_id == current_user.id)\
        .filter(Match.status == 'suggested')\
        .order_by(Match.score.desc(), Match.created_at.desc()).all()

    history_matches = Match.query.join(LostItem)\
        .filter(LostItem.user_id == current_user.id)\
        .filter(Match.status.in_(['confirmed', 'rejected']))\
        .order_by(Match.created_at.desc()).all()
    
    return render_template('user/matches.html',
                           suggested_matches=suggested_matches,
                           history_matches=history_matches)

@user_bp.route('/confirm-match/<int:match_id>', methods=['POST'])
@login_required
def confirm_match(match_id):
    """Confirm a match"""
    match = Match.query.get_or_404(match_id)
    
    # Verify ownership
    if match.lost_item.user_id != current_user.id:
        flash('Unauthorized', 'error')
        return redirect(url_for('user.matches'))
    
    # Update match status
    match.status = 'confirmed'
    
    # Update lost item status
    match.lost_item.status = 'matched'
    
    # Update found item status
    match.found_item.status = 'matched'
    
    # Create claim
    claim_code = QRService.generate_claim_code()
    claim = Claim(
        claim_code=claim_code,
        user_id=current_user.id,
        item_id=match.lost_item.id,
        release_status='pending'
    )
    
    db.session.add(claim)
    db.session.commit()
    
    flash('Match confirmed! You can now generate a claim QR code.', 'success')
    return redirect(url_for('user.claim_qr', claim_id=claim.id))

@user_bp.route('/skip-match/<int:match_id>', methods=['POST'])
@login_required
def skip_match(match_id):
    """Reject/skip a suggested match"""
    match = Match.query.get_or_404(match_id)
    
    # Verify ownership
    if match.lost_item.user_id != current_user.id:
        flash('Unauthorized', 'error')
        return redirect(url_for('user.matches'))
    
    if match.status == 'suggested':
        match.status = 'rejected'
        db.session.commit()
        flash('Match skipped.', 'info')
    
    return redirect(url_for('user.matches'))

@user_bp.route('/claim-qr/<int:claim_id>')
@login_required
def claim_qr(claim_id):
    """Generate and display QR code for claim"""
    claim = Claim.query.get_or_404(claim_id)
    
    # Verify ownership
    if claim.user_id != current_user.id:
        flash('Unauthorized', 'error')
        return redirect(url_for('user.dashboard'))
    
    # Generate QR code
    qr_code = QRService.generate_qr_code_for_claim(claim.claim_code, claim.id)
    
    return render_template('user/claim_qr.html', claim=claim, qr_code=qr_code)

@user_bp.route('/notifications')
@login_required
def notifications():
    """View notifications"""
    notifications = Notification.query.filter_by(user_id=current_user.id)\
        .order_by(Notification.created_at.desc()).all()
    
    return render_template('user/notifications.html', notifications=notifications)

@user_bp.route('/mark-notification-read/<int:notification_id>', methods=['POST'])
@login_required
def mark_notification_read(notification_id):
    """Mark notification as read"""
    NotificationService.mark_as_read(notification_id, current_user.id)
    return redirect(url_for('user.notifications'))
