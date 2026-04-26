"""
Admin routes (dashboard, user management, reports)
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from flask_login import login_required, current_user
from app import db
from app.models.user import User
from app.models.lost_item import LostItem
from app.models.found_item import FoundItem
from app.models.match import Match
from app.models.claim import Claim
from app.utils.helpers import role_required
from datetime import datetime, timedelta
from sqlalchemy import func
import csv
import io

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard')
@login_required
@role_required('admin')
def dashboard():
    """Admin dashboard"""
    # Statistics
    total_lost = LostItem.query.count()
    total_found = FoundItem.query.count()
    total_matched = Match.query.filter_by(status='confirmed').count()
    total_claimed = Claim.query.filter_by(release_status='released').count()
    
    # Recent activity
    recent_lost = LostItem.query.order_by(LostItem.created_at.desc()).limit(10).all()
    recent_found = FoundItem.query.order_by(FoundItem.created_at.desc()).limit(10).all()
    
    # Common items (high priority)
    common_items = FoundItem.query.filter_by(priority_flag=True)\
        .order_by(FoundItem.created_at.desc()).limit(10).all()
    
    # Pending claims
    pending_claims = Claim.query.filter_by(release_status='pending')\
        .order_by(Claim.created_at.desc()).limit(10).all()
    
    # Recent matches
    recent_matches = Match.query.order_by(Match.created_at.desc()).limit(10).all()
    
    # User statistics
    total_users = User.query.count()
    total_students = User.query.filter_by(role='student').count()
    total_staff = User.query.filter_by(role='staff').count()

    # Dashboard charts: 14-day activity (UTC, by created_at)
    now = datetime.utcnow()
    trend_labels = []
    trend_lost = []
    trend_found = []
    for i in range(13, -1, -1):
        day = (now - timedelta(days=i)).date()
        day_start = datetime.combine(day, datetime.min.time())
        day_end = day_start + timedelta(days=1)
        trend_labels.append(day.strftime('%b %d'))
        trend_lost.append(
            LostItem.query.filter(
                LostItem.created_at >= day_start,
                LostItem.created_at < day_end,
            ).count()
        )
        trend_found.append(
            FoundItem.query.filter(
                FoundItem.created_at >= day_start,
                FoundItem.created_at < day_end,
            ).count()
        )

    lost_by_cat = dict(
        db.session.query(LostItem.category, func.count(LostItem.id)).group_by(LostItem.category).all()
    )
    found_by_cat = dict(
        db.session.query(FoundItem.category, func.count(FoundItem.id)).group_by(FoundItem.category).all()
    )
    all_categories = set(lost_by_cat.keys()) | set(found_by_cat.keys())
    category_pairs = sorted(
        ((c, lost_by_cat.get(c, 0) + found_by_cat.get(c, 0)) for c in all_categories),
        key=lambda x: x[1],
        reverse=True,
    )[:10]
    category_chart_labels = [p[0] for p in category_pairs]
    category_chart_values = [p[1] for p in category_pairs]

    return render_template('admin/dashboard.html',
                         total_lost=total_lost,
                         total_found=total_found,
                         total_matched=total_matched,
                         total_claimed=total_claimed,
                         recent_lost=recent_lost,
                         recent_found=recent_found,
                         common_items=common_items,
                         pending_claims=pending_claims,
                         recent_matches=recent_matches,
                         total_users=total_users,
                         total_students=total_students,
                         total_staff=total_staff,
                         trend_labels=trend_labels,
                         trend_lost=trend_lost,
                         trend_found=trend_found,
                         category_chart_labels=category_chart_labels,
                         category_chart_values=category_chart_values)

@admin_bp.route('/users')
@login_required
@role_required('admin')
def users():
    """User management"""
    page = request.args.get('page', 1, type=int)
    role_filter = request.args.get('role', 'all')
    
    query = User.query
    if role_filter != 'all':
        query = query.filter_by(role=role_filter)
    
    users = query.order_by(User.created_at.desc())\
        .paginate(page=page, per_page=20, error_out=False)
    
    return render_template('admin/users.html', users=users, role_filter=role_filter)

@admin_bp.route('/create-user', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def create_user():
    """Create new user (admin/staff)"""
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')
        
        if not name or not email or not password or not role:
            flash('All fields are required', 'error')
            return render_template('admin/create_user.html')
        
        if role not in ['admin', 'staff', 'student']:
            flash('Invalid role', 'error')
            return render_template('admin/create_user.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists', 'error')
            return render_template('admin/create_user.html')
        
        user = User(name=name, email=email, role=role)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash('User created successfully', 'success')
        return redirect(url_for('admin.users'))
    
    return render_template('admin/create_user.html')

@admin_bp.route('/reports')
@login_required
@role_required('admin')
def reports():
    """Reports and statistics"""
    # Monthly statistics from Nov 2025 through current month.
    start_month = datetime(2025, 11, 1)
    current = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    cursor = start_month
    months = []
    while cursor <= current:
        if cursor.month == 12:
            next_month = cursor.replace(year=cursor.year + 1, month=1, day=1)
        else:
            next_month = cursor.replace(month=cursor.month + 1, day=1)

        lost_count = LostItem.query.filter(
            LostItem.created_at >= cursor,
            LostItem.created_at < next_month
        ).count()

        found_count = FoundItem.query.filter(
            FoundItem.created_at >= cursor,
            FoundItem.created_at < next_month
        ).count()

        claimed_count = Claim.query.filter(
            Claim.release_date.isnot(None),
            Claim.release_date >= cursor,
            Claim.release_date < next_month
        ).count()

        months.append({
            'month': cursor.strftime('%B %Y'),
            'lost': lost_count,
            'found': found_count,
            'claimed': claimed_count
        })
        cursor = next_month
    
    # Category statistics
    lost_categories = db.session.query(
        LostItem.category,
        func.count(LostItem.id).label('count')
    ).group_by(LostItem.category).all()
    
    found_categories = db.session.query(
        FoundItem.category,
        func.count(FoundItem.id).label('count')
    ).group_by(FoundItem.category).all()

    # Filtered category-by-month analytics
    selected_category = request.args.get('category', 'all')
    selected_month = request.args.get('month', 'all')

    monthly_category_rows = []
    for month in months:
        month_dt = datetime.strptime(month['month'], '%B %Y')
        if month_dt.month == 12:
            next_month = month_dt.replace(year=month_dt.year + 1, month=1, day=1)
        else:
            next_month = month_dt.replace(month=month_dt.month + 1, day=1)

        if selected_month != 'all' and month['month'] != selected_month:
            continue

        lost_query = LostItem.query.filter(
            LostItem.created_at >= month_dt,
            LostItem.created_at < next_month
        )
        found_query = FoundItem.query.filter(
            FoundItem.created_at >= month_dt,
            FoundItem.created_at < next_month
        )
        if selected_category != 'all':
            lost_query = lost_query.filter(LostItem.category == selected_category)
            found_query = found_query.filter(FoundItem.category == selected_category)

        monthly_category_rows.append({
            'month': month['month'],
            'category': selected_category,
            'lost': lost_query.count(),
            'found': found_query.count()
        })

    category_options = sorted({c.category for c in lost_categories} | {c.category for c in found_categories})
    
    return render_template('admin/reports.html',
                         months=months,
                         graph_labels=[m['month'] for m in months],
                         graph_lost=[m['lost'] for m in months],
                         graph_found=[m['found'] for m in months],
                         graph_claimed=[m['claimed'] for m in months],
                         lost_categories=lost_categories,
                         found_categories=found_categories,
                         monthly_category_rows=monthly_category_rows,
                         selected_category=selected_category,
                         selected_month=selected_month,
                         category_options=category_options,
                         month_options=[m['month'] for m in months])

@admin_bp.route('/export-csv')
@login_required
@role_required('admin')
def export_csv():
    """Export data to CSV"""
    export_type = request.args.get('type', 'lost')
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    if export_type == 'lost':
        writer.writerow(['ID', 'User', 'Item Name', 'Category', 'Date Lost', 'Status', 'Created At'])
        items = LostItem.query.all()
        for item in items:
            writer.writerow([
                item.id,
                item.user.email,
                item.item_name,
                item.category,
                item.date_lost,
                item.status,
                item.created_at
            ])
    elif export_type == 'found':
        writer.writerow(['ID', 'Staff', 'Item Name', 'Category', 'Date Found', 'Status', 'Created At'])
        items = FoundItem.query.all()
        for item in items:
            writer.writerow([
                item.id,
                item.staff.email,
                item.item_name,
                item.category,
                item.date_found,
                item.status,
                item.created_at
            ])
    elif export_type == 'claims':
        writer.writerow(['ID', 'Claim Code', 'User', 'Item', 'Status', 'Released By', 'Release Date'])
        claims = Claim.query.all()
        for claim in claims:
            writer.writerow([
                claim.id,
                claim.claim_code,
                claim.user.email,
                claim.lost_item.item_name,
                claim.release_status,
                claim.released_by_user.email if claim.released_by_user else 'N/A',
                claim.release_date or 'N/A'
            ])
    
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode()),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'{export_type}_items_{datetime.now().strftime("%Y%m%d")}.csv'
    )
