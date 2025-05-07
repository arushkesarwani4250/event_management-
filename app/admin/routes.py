from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import User
from app.admin.forms import EditUserForm

bp = Blueprint('admin', __name__)


@bp.route('/users')
@login_required
def users():
    if current_user.role != 'admin':
        flash('Access denied: Admin role required', 'danger')
        return redirect(url_for('main.index'))

    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=users)


@bp.route('/edit-user/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_user(id):
    if current_user.role != 'admin':
        flash('Access denied: Admin role required', 'danger')
        return redirect(url_for('main.index'))

    user = User.query.get_or_404(id)
    form = EditUserForm(obj=user)

    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.role = form.role.data
        user.active = form.active.data

        db.session.commit()
        flash('User updated successfully!', 'success')
        return redirect(url_for('admin.users'))

    return render_template('admin/edit_user.html', form=form, user=user)


@bp.route('/toggle-user/<int:id>')
@login_required
def toggle_user(id):
    if current_user.role != 'admin':
        flash('Access denied: Admin role required', 'danger')
        return redirect(url_for('main.index'))

    user = User.query.get_or_404(id)
    user.active = not user.active
    db.session.commit()

    status = 'activated' if user.active else 'deactivated'
    flash(f'User {user.username} has been {status}', 'success')
    return redirect(url_for('admin.users'))