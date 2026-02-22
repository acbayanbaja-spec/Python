"""
Authentication routes (login, register, logout)
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, make_response
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models.user import User
from app.utils.helpers import role_required

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration (students only)"""
    if current_user.is_authenticated:
        return redirect(url_for('user.dashboard'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validation
        if not name or not email or not password:
            flash('All fields are required', 'error')
            return render_template('auth/register.html')
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('auth/register.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters', 'error')
            return render_template('auth/register.html')
        
        # Check if user exists
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return render_template('auth/register.html')
        
        # Create new user (student role by default)
        user = User(name=name, email=email, role='student')
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        # Redirect based on role
        if current_user.is_admin():
            return redirect(url_for('admin.dashboard'))
        elif current_user.is_staff():
            return redirect(url_for('staff.dashboard'))
        else:
            return redirect(url_for('user.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = request.form.get('remember') == 'on'
        
        if not email or not password:
            flash('Email and password are required', 'error')
            return render_template('auth/login.html')
        
        try:
            user = User.query.filter_by(email=email).first()
            
            if user and user.check_password(password):
                login_user(user, remember=remember)
                flash(f'Welcome back, {user.name}!', 'success')
                
                # Redirect based on role
                next_page = request.args.get('next')
                if next_page:
                    return redirect(next_page)
                
                if user.is_admin():
                    return redirect(url_for('admin.dashboard'))
                elif user.is_staff():
                    return redirect(url_for('staff.dashboard'))
                else:
                    return redirect(url_for('user.dashboard'))
            else:
                flash('Invalid email or password', 'error')
        except Exception as e:
            from flask import current_app
            current_app.logger.error(f"Database error during login: {e}")
            flash('Database connection error. Please try again later.', 'error')
    
    # Add cache-busting headers to prevent browser caching
    response = make_response(render_template('auth/login.html'))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@auth_bp.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('auth.login'))
