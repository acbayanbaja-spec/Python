"""
Staff routes (found item logging, QR verification)
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models.found_item import FoundItem
from app.models.claim import Claim
from app.models.lost_item import LostItem
from app.services.lost_found_matcher import LostFoundMatcher
from app.services.notification_service import NotificationService
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
                         claims=claims,
                         common_items=common_items)

@staff_bp.route('/log-found', methods=['GET', 'POST'])
@login_required
@role_required('staff', 'admin')
def log_found():
    """Log a found item"""
    if request.method == 'POST':
        item_name = request.form.get('item_name')
        description = request.form.get('description')
        category = request.form.get('category')
        color = request.form.get('color')
        date_found = request.form.get('date_found')
        location_found = request.form.get('location_found')
        storage_location = request.form.get('storage_location')
        priority_flag = request.form.get('priority_flag') == 'on'
        image = request.files.get('image')
        
        # Validation
        if not item_name or not category or not date_found:
            flash('Item name, category, and date found are required', 'error')
            return render_template('staff/log_found.html')
        
        try:
            date_found_obj = datetime.strptime(date_found, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format', 'error')
            return render_template('staff/log_found.html')
        
        # Auto-flag common categories
        common_categories = ['ID', 'Wallet', 'Phone']
        if category in common_categories:
            priority_flag = True
        
        # Save image if provided
        image_path = None
        if image:
            image_path = save_uploaded_file(image)
        
        # Create found item
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
        db.session.commit()
        
        # Run AI matching against pending lost items
        matcher = LostFoundMatcher()
        lost_items = LostItem.query.filter_by(status='pending').all()
        
        found_item_dict = {
            'id': found_item.id,
            'item_name': found_item.item_name,
            'description': found_item.description or '',
            'category': found_item.category,
            'color': found_item.color or ''
        }
        
        for lost_item in lost_items:
            lost_item_dict = {
                'id': lost_item.id,
                'item_name': lost_item.item_name,
                'description': lost_item.description or '',
                'category': lost_item.category,
                'color': lost_item.color or ''
            }
            
            score = matcher.calculate_match_score(lost_item_dict, found_item_dict)
            
            if score >= 50.0:
                # Check if match already exists
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
                    
                    # Notify user
                    NotificationService.notify_match_found(
                        lost_item.user_id,
                        lost_item.item_name,
                        score
                    )
        
        db.session.commit()
        
        flash('Found item logged successfully!', 'success')
        return redirect(url_for('staff.dashboard'))
    
    return render_template('staff/log_found.html')

@staff_bp.route('/found-items')
@login_required
@role_required('staff', 'admin')
def found_items():
    """View all found items"""
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', 'all')
    
    query = FoundItem.query
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)
    
    found_items = query.order_by(FoundItem.created_at.desc())\
        .paginate(page=page, per_page=20, error_out=False)
    
    return render_template('staff/found_items.html', found_items=found_items, status_filter=status_filter)

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
    from app.models.match import Match
    match = Match.query.filter_by(
        lost_item_id=claim.item_id,
        status='confirmed'
    ).first()
    
    if match:
        match.found_item.status = 'claimed'
    
    db.session.commit()
    
    # Notify user
    NotificationService.notify_item_claimed(
        claim.user_id,
        claim.lost_item.item_name
    )
    
    flash('Item released successfully!', 'success')
    return redirect(url_for('staff.dashboard'))

@staff_bp.route('/matches')
@login_required
@role_required('staff', 'admin')
def matches():
    """View all matches"""
    matches = Match.query.order_by(Match.score.desc(), Match.created_at.desc()).all()
    return render_template('staff/matches.html', matches=matches)
