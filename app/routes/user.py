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
from app.services.interaction_logger import InteractionLogger
from app.services.qr_service import QRService
from app.utils.helpers import save_uploaded_file
from datetime import datetime

user_bp = Blueprint('user', __name__)


def _process_report_lost_post():
    """
    Handle report-lost form. Returns redirect on success, None on validation error
    (caller re-renders my-items with flash).
    """
    item_name = (request.form.get('item_name') or '').strip()
    description = (request.form.get('description') or '').strip()
    category = (request.form.get('category') or '').strip()
    color = (request.form.get('color') or '').strip()
    date_lost = (request.form.get('date_lost') or '').strip()
    location_lost = (request.form.get('location_lost') or '').strip()
    image = request.files.get('image')

    if not item_name or not category or not date_lost:
        flash('Item name, category, and date lost are required', 'error')
        return None

    try:
        date_lost_obj = datetime.strptime(date_lost, '%Y-%m-%d').date()
    except ValueError:
        flash('Invalid date format', 'error')
        return None

    image_path = None
    if image and image.filename:
        image_path = save_uploaded_file(image)
        if image_path is None:
            flash('Invalid image format. Allowed: png, jpg, jpeg, gif, webp', 'error')
            return None

    lost_item = LostItem(
        user_id=current_user.id,
        item_name=item_name,
        description=description or None,
        category=category,
        color=color or None,
        date_lost=date_lost_obj,
        location_lost=location_lost or None,
        image_path=image_path,
        status='pending'
    )

    db.session.add(lost_item)
    db.session.flush()
    InteractionLogger.log(
        actor_id=current_user.id,
        action_type='lost_item_reported',
        title=f"Reported lost item: {item_name}",
        description=f"Category: {category}",
        target_user_id=current_user.id,
        reference_type='lost_item',
        reference_id=lost_item.id,
        metadata={'date_lost': str(date_lost_obj), 'location_lost': location_lost or None},
        commit=False
    )

    matcher = LostFoundMatcher()
    from app.models.found_item import FoundItem
    found_items = FoundItem.query.filter_by(status='available').all()

    found_items_dict = [{
        'id': item.id,
        'item_name': item.item_name,
        'description': item.description or '',
        'category': item.category,
        'color': item.color or '',
        'image_path': item.image_path or ''
    } for item in found_items]

    lost_item_dict = {
        'id': lost_item.id,
        'item_name': lost_item.item_name,
        'description': lost_item.description or '',
        'category': lost_item.category,
        'color': lost_item.color or '',
        'image_path': lost_item.image_path or ''
    }

    matches = matcher.find_matches(lost_item_dict, found_items_dict, threshold=50.0)

    for match_data in matches[:5]:
        match = Match(
            lost_item_id=lost_item.id,
            found_item_id=match_data['found_item_id'],
            score=match_data['score'],
            status='suggested'
        )
        db.session.add(match)

    db.session.commit()
    try:
        NotificationService.notify_staff_new_lost_item(
            student_name=current_user.name,
            item_name=lost_item.item_name,
            category=lost_item.category,
            location=lost_item.location_lost
        )
    except Exception:
        from flask import current_app
        current_app.logger.exception('Staff notification failed in report_lost')

    for match_data in matches[:5]:
        try:
            NotificationService.notify_match_found(
                current_user.id,
                lost_item.item_name,
                match_data['score']
            )
        except Exception:
            from flask import current_app
            current_app.logger.exception('Notification insert failed in report_lost')

    flash('Lost item reported successfully! We will notify you if we find a match.', 'success')
    status_filter = request.form.get('list_status') or request.args.get('status', 'all')
    page = request.form.get('list_page', type=int) or 1
    return redirect(url_for('user.my_items', page=page, status=status_filter) + '#inventory')


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
    interaction_history = InteractionLogger.get_user_history(current_user.id, limit=25)
    
    return render_template('user/dashboard.html',
                         lost_items=lost_items,
                         matches=matches,
                         unread_count=unread_count,
                         total_lost=total_lost,
                         matched_items=matched_items,
                         claimed_items=claimed_items,
                         interaction_history=interaction_history)

@user_bp.route('/report-lost', methods=['GET', 'POST'])
@login_required
def report_lost():
    """Legacy URL — reporting is merged into My Items."""
    try:
        if request.method == 'POST':
            resp = _process_report_lost_post()
            if resp:
                return resp
            return redirect(url_for('user.my_items') + '#report-lost-panel')
        return redirect(url_for('user.my_items') + '#report-lost-panel')
    except Exception:
        db.session.rollback()
        from flask import current_app
        current_app.logger.exception('Error in report_lost route')
        flash('Something went wrong while submitting your report. Please try again.', 'error')
        return redirect(url_for('user.my_items'))


@user_bp.route('/my-items', methods=['GET', 'POST'])
@login_required
def my_items():
    """View all lost items; report form lives on this page."""
    try:
        if request.method == 'POST':
            resp = _process_report_lost_post()
            if resp:
                return resp
    except Exception:
        db.session.rollback()
        from flask import current_app
        current_app.logger.exception('Error in my_items POST')
        flash('Something went wrong while submitting your report. Please try again.', 'error')

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
    db.session.flush()
    InteractionLogger.log(
        actor_id=current_user.id,
        action_type='match_confirmed',
        title=f"Confirmed match for {match.lost_item.item_name}",
        description=f"Match confidence: {match.score:.2f}%",
        target_user_id=current_user.id,
        reference_type='match',
        reference_id=match.id,
        metadata={'found_item_id': match.found_item_id, 'score': match.score},
        commit=False
    )
    InteractionLogger.log(
        actor_id=current_user.id,
        action_type='claim_created',
        title=f"Generated claim request for {match.lost_item.item_name}",
        description=f"Claim code: {claim_code}",
        target_user_id=current_user.id,
        reference_type='claim',
        reference_id=claim.id,
        metadata={'claim_code': claim_code},
        commit=False
    )
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
        InteractionLogger.log(
            actor_id=current_user.id,
            action_type='match_rejected',
            title=f"Rejected suggested match for {match.lost_item.item_name}",
            description=f"Found item candidate: {match.found_item.item_name}",
            target_user_id=current_user.id,
            reference_type='match',
            reference_id=match.id,
            metadata={'score': match.score},
            commit=False
        )
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
    InteractionLogger.log(
        actor_id=current_user.id,
        action_type='claim_qr_viewed',
        title=f"Viewed QR code for claim {claim.claim_code}",
        description=f"Item: {claim.lost_item.item_name}",
        target_user_id=current_user.id,
        reference_type='claim',
        reference_id=claim.id,
        metadata={'release_status': claim.release_status},
        commit=True
    )
    
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
