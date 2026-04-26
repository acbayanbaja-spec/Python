"""
Staff routes (found item logging, QR verification)
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models.found_item import FoundItem
from app.models.claim import Claim
from app.models.lost_item import LostItem
from app.models.match import Match
from app.services.lost_found_matcher import LostFoundMatcher
from app.services.notification_service import NotificationService
from app.services.interaction_logger import InteractionLogger
from app.services.qr_service import QRService
from app.utils.helpers import save_uploaded_file, role_required
from datetime import datetime

staff_bp = Blueprint('staff', __name__)

@staff_bp.route('/dashboard')
@login_required
@role_required('staff', 'admin')
def dashboard():
    """Staff dashboard"""
    # Statistics
    total_found = FoundItem.query.count()
    available_items = FoundItem.query.filter_by(status='available').count()
    pending_claims = Claim.query.filter_by(release_status='pending').count()
    
    # Recent found items
    recent_items = FoundItem.query.order_by(FoundItem.created_at.desc()).limit(10).all()
    recent_lost_reports = LostItem.query.order_by(LostItem.created_at.desc()).limit(20).all()
    
    # Pending claims
    claims = Claim.query.filter_by(release_status='pending')\
        .order_by(Claim.created_at.desc()).limit(10).all()
    
    # Common items (high priority)
    common_items = FoundItem.query.filter_by(priority_flag=True, status='available')\
        .order_by(FoundItem.created_at.desc()).limit(10).all()
    
    return render_template('staff/dashboard.html',
                         total_found=total_found,
                         available_items=available_items,
                         pending_claims=pending_claims,
                         recent_items=recent_items,
                         recent_lost_reports=recent_lost_reports,
                         claims=claims,
                         common_items=common_items)

def _process_log_found_post():
    """
    Process log-found form submission. On success returns redirect response.
    On validation error returns None and caller should re-render list + form.
    """
    item_name = request.form.get('item_name')
    description = request.form.get('description')
    category = request.form.get('category')
    color = request.form.get('color')
    date_found = request.form.get('date_found')
    location_found = request.form.get('location_found')
    storage_location = request.form.get('storage_location')
    priority_flag = request.form.get('priority_flag') == 'on'
    image = request.files.get('image')

    if not item_name or not category or not date_found:
        flash('Item name, category, and date found are required', 'error')
        return None

    try:
        date_found_obj = datetime.strptime(date_found, '%Y-%m-%d').date()
    except ValueError:
        flash('Invalid date format', 'error')
        return None

    common_categories = ['ID', 'Wallet', 'Phone']
    if category in common_categories:
        priority_flag = True

    image_path = None
    if image and getattr(image, 'filename', None):
        image_path = save_uploaded_file(image)

    found_item = FoundItem(
        staff_id=current_user.id,
        item_name=item_name,
        description=description,
        category=category,
        color=color,
        date_found=date_found_obj,
        location_found=location_found,
        storage_location=storage_location,
        priority_flag=priority_flag,
        image_path=image_path,
        status='available'
    )

    db.session.add(found_item)
    db.session.flush()
    InteractionLogger.log(
        actor_id=current_user.id,
        action_type='found_item_logged',
        title=f"Logged found item: {item_name}",
        description=f"Location: {location_found or 'N/A'}",
        target_user_id=None,
        reference_type='found_item',
        reference_id=found_item.id,
        metadata={'category': category, 'priority_flag': priority_flag},
        commit=False
    )
    db.session.commit()

    matcher = LostFoundMatcher()
    lost_items = LostItem.query.filter_by(status='pending').all()

    found_item_dict = {
        'id': found_item.id,
        'item_name': found_item.item_name,
        'description': found_item.description or '',
        'category': found_item.category,
        'color': found_item.color or '',
        'image_path': found_item.image_path or ''
    }

    for lost_item in lost_items:
        lost_item_dict = {
            'id': lost_item.id,
            'item_name': lost_item.item_name,
            'description': lost_item.description or '',
            'category': lost_item.category,
            'color': lost_item.color or '',
            'image_path': lost_item.image_path or ''
        }

        score = matcher.calculate_match_score(lost_item_dict, found_item_dict)

        if score >= 50.0:
            existing_match = Match.query.filter_by(
                lost_item_id=lost_item.id,
                found_item_id=found_item.id
            ).first()

            if not existing_match:
                match = Match(
                    lost_item_id=lost_item.id,
                    found_item_id=found_item.id,
                    score=score,
                    status='suggested'
                )
                db.session.add(match)

                NotificationService.notify_match_found(
                    lost_item.user_id,
                    lost_item.item_name,
                    score
                )

    db.session.commit()

    flash('Found item logged successfully!', 'success')
    status_filter = request.form.get('list_status') or request.args.get('status', 'all')
    page = request.form.get('list_page', type=int) or 1
    return redirect(url_for('staff.found_items', page=page, status=status_filter) + '#inventory')


@staff_bp.route('/log-found', methods=['GET', 'POST'])
@login_required
@role_required('staff', 'admin')
def log_found():
    """Legacy URL — merged into Found Items."""
    if request.method == 'POST':
        resp = _process_log_found_post()
        if resp:
            return resp
        return redirect(url_for('staff.found_items') + '#log-found-panel')
    return redirect(url_for('staff.found_items') + '#log-found-panel')


@staff_bp.route('/found-items', methods=['GET', 'POST'])
@login_required
@role_required('staff', 'admin')
def found_items():
    """View all found items; log-new form lives on this page."""
    if request.method == 'POST':
        resp = _process_log_found_post()
        if resp:
            return resp

    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', 'all')
    
    query = FoundItem.query
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)
    
    found_items = query.order_by(FoundItem.created_at.desc())\
        .paginate(page=page, per_page=20, error_out=False)
    
    return render_template('staff/found_items.html', found_items=found_items, status_filter=status_filter)


@staff_bp.route('/edit-found-item/<int:item_id>', methods=['GET', 'POST'])
@login_required
@role_required('staff', 'admin')
def edit_found_item(item_id):
    """Edit found item details."""
    item = FoundItem.query.get_or_404(item_id)

    if request.method == 'POST':
        item_name = (request.form.get('item_name') or '').strip()
        category = (request.form.get('category') or '').strip()
        color = (request.form.get('color') or '').strip()
        description = (request.form.get('description') or '').strip()
        location_found = (request.form.get('location_found') or '').strip()
        storage_location = (request.form.get('storage_location') or '').strip()
        date_found = (request.form.get('date_found') or '').strip()
        image = request.files.get('image')

        if not item_name or not category or not date_found:
            flash('Item name, category, and date found are required', 'error')
            return render_template('staff/edit_found_item.html', item=item)

        try:
            item.date_found = datetime.strptime(date_found, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format', 'error')
            return render_template('staff/edit_found_item.html', item=item)

        item.item_name = item_name
        item.category = category
        item.color = color or None
        item.description = description or None
        item.location_found = location_found or None
        item.storage_location = storage_location or None
        item.priority_flag = category in ['ID', 'Wallet', 'Phone'] or (request.form.get('priority_flag') == 'on')

        if image and getattr(image, 'filename', None):
            image_path = save_uploaded_file(image)
            if image_path is None:
                flash('Invalid image format. Allowed: png, jpg, jpeg, gif, webp', 'error')
                return render_template('staff/edit_found_item.html', item=item)
            item.image_path = image_path

        db.session.commit()
        flash('Found item updated successfully.', 'success')
        return redirect(url_for('staff.found_items'))

    return render_template('staff/edit_found_item.html', item=item)


@staff_bp.route('/lost-reports')
@login_required
@role_required('staff', 'admin')
def lost_reports():
    """View all student lost reports with images."""
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', 'all')

    query = LostItem.query
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)

    lost_reports = query.order_by(LostItem.created_at.desc()) \
        .paginate(page=page, per_page=20, error_out=False)
    return render_template('staff/lost_reports.html', lost_reports=lost_reports, status_filter=status_filter)

@staff_bp.route('/verify-claim', methods=['GET', 'POST'])
@login_required
@role_required('staff', 'admin')
def verify_claim():
    """Verify QR claim code"""
    if request.method == 'POST':
        claim_code = request.form.get('claim_code')
        
        if not claim_code:
            flash('Please enter a claim code', 'error')
            return render_template('staff/verify_claim.html')
        
        claim = Claim.query.filter_by(claim_code=claim_code).first()
        
        if not claim:
            flash('Invalid claim code', 'error')
            return render_template('staff/verify_claim.html')
        
        if claim.release_status != 'pending':
            flash(f'Claim already {claim.release_status}', 'warning')
            return render_template('staff/verify_claim.html', claim=claim)
        
        return render_template('staff/verify_claim.html', claim=claim)
    
    return render_template('staff/verify_claim.html')

@staff_bp.route('/release-item/<int:claim_id>', methods=['POST'])
@login_required
@role_required('staff', 'admin')
def release_item(claim_id):
    """Release item to user"""
    claim = Claim.query.get_or_404(claim_id)
    
    if claim.release_status != 'pending':
        flash('Item already processed', 'error')
        return redirect(url_for('staff.verify_claim'))
    
    # Update claim
    claim.release_status = 'released'
    claim.released_by = current_user.id
    claim.release_date = datetime.utcnow()
    
    # Update lost item status
    claim.lost_item.status = 'claimed'
    
    # Update found item status if matched
    match = Match.query.filter_by(
        lost_item_id=claim.item_id,
        status='confirmed'
    ).first()
    
    if match:
        match.found_item.status = 'claimed'
        InteractionLogger.log(
            actor_id=current_user.id,
            action_type='claim_released',
            title=f"Released item to student: {claim.lost_item.item_name}",
            description=f"Claim code: {claim.claim_code}",
            target_user_id=claim.user_id,
            reference_type='claim',
            reference_id=claim.id,
            metadata={'found_item_id': match.found_item_id},
            commit=False
        )
    else:
        InteractionLogger.log(
            actor_id=current_user.id,
            action_type='claim_released',
            title=f"Released item to student: {claim.lost_item.item_name}",
            description=f"Claim code: {claim.claim_code}",
            target_user_id=claim.user_id,
            reference_type='claim',
            reference_id=claim.id,
            metadata={'found_item_id': None},
            commit=False
        )
    
    db.session.commit()
    
    # Notify user
    NotificationService.notify_item_claimed(
        claim.user_id,
        claim.lost_item.item_name
    )
    
    flash('Item released successfully!', 'success')
    return redirect(url_for('staff.dashboard'))


@staff_bp.route('/approve-match/<int:match_id>', methods=['POST'])
@login_required
@role_required('staff', 'admin')
def approve_match(match_id):
    """Staff approval: create claim code only after staff confirms."""
    match = Match.query.get_or_404(match_id)
    if match.status != 'student_confirmed':
        flash('This match cannot be approved in its current state.', 'warning')
        return redirect(url_for('staff.matches'))

    existing_claim = Claim.query.filter_by(item_id=match.lost_item_id).first()
    if existing_claim:
        flash('Claim already exists for this item.', 'info')
        return redirect(url_for('staff.matches'))

    match.status = 'confirmed'
    match.lost_item.status = 'matched'
    match.found_item.status = 'matched'

    claim_code = QRService.generate_claim_code()
    claim = Claim(
        claim_code=claim_code,
        user_id=match.lost_item.user_id,
        item_id=match.lost_item_id,
        release_status='pending'
    )
    db.session.add(claim)
    db.session.flush()
    # Generate QR payload immediately after approval so students can claim right away.
    QRService.generate_qr_code_for_claim(claim.claim_code, claim.id)
    InteractionLogger.log(
        actor_id=current_user.id,
        action_type='staff_match_approved',
        title=f"Approved match for {match.lost_item.item_name}",
        description=f"Claim + QR generated: {claim_code}",
        target_user_id=match.lost_item.user_id,
        reference_type='claim',
        reference_id=claim.id,
        metadata={'match_id': match.id, 'found_item_id': match.found_item_id},
        commit=False
    )
    db.session.commit()
    NotificationService.notify_status_update(match.lost_item.user_id, match.lost_item.item_name, 'Staff approved match. Claim QR is now available.')
    flash('Match approved and claim code created.', 'success')
    return redirect(url_for('staff.matches'))


@staff_bp.route('/reject-match/<int:match_id>', methods=['POST'])
@login_required
@role_required('staff', 'admin')
def reject_match(match_id):
    """Staff rejection for student-confirmed match."""
    match = Match.query.get_or_404(match_id)
    if match.status != 'student_confirmed':
        flash('This match cannot be rejected in its current state.', 'warning')
        return redirect(url_for('staff.matches'))
    match.status = 'rejected'
    match.lost_item.status = 'pending'
    match.found_item.status = 'available'
    db.session.commit()
    NotificationService.notify_status_update(match.lost_item.user_id, match.lost_item.item_name, 'Staff rejected the match request.')
    flash('Match rejected.', 'info')
    return redirect(url_for('staff.matches'))


@staff_bp.route('/delete-found-item/<int:item_id>', methods=['POST'])
@login_required
@role_required('staff', 'admin')
def delete_found_item(item_id):
    """Allow staff to delete found items in any status."""
    item = FoundItem.query.get_or_404(item_id)
    item_name = item.item_name
    db.session.delete(item)
    db.session.commit()
    flash(f"Found item '{item_name}' deleted.", 'success')
    return redirect(url_for('staff.found_items'))


@staff_bp.route('/delete-lost-report/<int:item_id>', methods=['POST'])
@login_required
@role_required('staff', 'admin')
def delete_lost_report(item_id):
    """Allow staff to delete claimed lost reports."""
    item = LostItem.query.get_or_404(item_id)
    if item.status != 'claimed':
        flash('Only claimed lost reports can be deleted.', 'error')
        return redirect(url_for('staff.lost_reports'))
    db.session.delete(item)
    db.session.commit()
    flash('Claimed lost report deleted.', 'success')
    return redirect(url_for('staff.lost_reports', status='claimed'))

@staff_bp.route('/matches')
@login_required
@role_required('staff', 'admin')
def matches():
    """View all matches"""
    matches = Match.query.order_by(Match.score.desc(), Match.created_at.desc()).all()
    return render_template('staff/matches.html', matches=matches)


@staff_bp.route('/delete-match/<int:match_id>', methods=['POST'])
@login_required
@role_required('staff', 'admin')
def delete_match(match_id):
    """Permanently delete a match record."""
    match = Match.query.get_or_404(match_id)
    db.session.delete(match)
    db.session.commit()
    flash('Match deleted.', 'success')
    return redirect(url_for('staff.matches'))
