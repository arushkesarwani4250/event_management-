from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from werkzeug.security import check_password_hash
from app.auth.forms import LoginForm, RegistrationForm, AdminRegistrationForm
from app.models import User
from app.extensions import db, login_manager

# Initialize Blueprint
auth_bp = Blueprint('auth', __name__)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('user.products'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')

            # Redirect based on user role
            if user.role == 'admin':
                return redirect(next_page or url_for('admin.dashboard'))
            elif user.role == 'vendor':
                return redirect(next_page or url_for('vendor.dashboard'))
            else:
                return redirect(next_page or url_for('user.products'))
        else:
            flash('Invalid email or password', 'danger')

    return render_template('auth/login.html', form=form)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('user.products'))

    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        user = User(
            username=form.username.data,
            email=form.email.data,
            password_hash=hashed_password,
            role='user'  # Default role
        )
        db.session.add(user)
        db.session.commit()

        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', form=form)


@auth_bp.route('/admin/register', methods=['GET', 'POST'])
def admin_register():
    # Prevent if admin already exists
    if User.query.filter_by(role='admin').first():
        flash('Admin account already exists', 'warning')
        return redirect(url_for('auth.login'))

    form = AdminRegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        admin = User(
            username=form.username.data,
            email=form.email.data,
            password_hash=hashed_password,
            role='admin'
        )
        db.session.add(admin)
        db.session.commit()

        flash('Admin account created! Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/admin_register.html', form=form)


@auth_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))