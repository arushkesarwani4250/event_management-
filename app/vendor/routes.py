from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Product
from app.vendor.forms import ProductForm
from werkzeug.utils import secure_filename
import os

bp = Blueprint('vendor', __name__)


@bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'vendor':
        flash('Access denied: Vendor role required', 'danger')
        return redirect(url_for('main.index'))

    products = Product.query.filter_by(vendor_id=current_user.id).count()
    pending = Product.query.filter_by(vendor_id=current_user.id, status='pending').count()
    approved = Product.query.filter_by(vendor_id=current_user.id, status='approved').count()

    return render_template('vendor/dashboard.html',
                           product_count=products,
                           pending_count=pending,
                           approved_count=approved)


@bp.route('/products')
@login_required
def products():
    if current_user.role != 'vendor':
        flash('Access denied: Vendor role required', 'danger')
        return redirect(url_for('main.index'))

    page = request.args.get('page', 1, type=int)
    products = Product.query.filter_by(vendor_id=current_user.id) \
        .order_by(Product.created_at.desc()) \
        .paginate(page=page, per_page=10)

    return render_template('vendor/products.html', products=products)


@bp.route('/add-product', methods=['GET', 'POST'])
@login_required
def add_product():
    if current_user.role != 'vendor':
        flash('Access denied: Vendor role required', 'danger')
        return redirect(url_for('main.index'))

    form = ProductForm()
    if form.validate_on_submit():
        product = Product(
            name=form.name.data,
            description=form.description.data,
            price=form.price.data,
            quantity=form.quantity.data,
            vendor_id=current_user.id,
            status='pending'  # Needs admin approval
        )

        # Handle file upload
        if form.image.data:
            filename = secure_filename(form.image.data.filename)
            filepath = os.path.join('app/static/images/products', filename)
            form.image.data.save(filepath)
            product.image = filename

        db.session.add(product)
        db.session.commit()
        flash('Product added successfully! Waiting for admin approval.', 'success')
        return redirect(url_for('vendor.products'))

    return render_template('vendor/add_product.html', form=form)


@bp.route('/edit-product/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_product(id):
    if current_user.role != 'vendor':
        flash('Access denied: Vendor role required', 'danger')
        return redirect(url_for('main.index'))

    product = Product.query.get_or_404(id)
    if product.vendor_id != current_user.id:
        flash('You can only edit your own products', 'danger')
        return redirect(url_for('vendor.products'))

    form = ProductForm(obj=product)
    if form.validate_on_submit():
        product.name = form.name.data
        product.description = form.description.data
        product.price = form.price.data
        product.quantity = form.quantity.data

        if form.image.data:
            # Remove old image if exists
            if product.image:
                old_path = os.path.join('app/static/images/products', product.image)
                if os.path.exists(old_path):
                    os.remove(old_path)

            # Save new image
            filename = secure_filename(form.image.data.filename)
            filepath = os.path.join('app/static/images/products', filename)
            form.image.data.save(filepath)
            product.image = filename

        db.session.commit()
        flash('Product updated successfully!', 'success')
        return redirect(url_for('vendor.products'))

    return render_template('vendor/edit_product.html', form=form, product=product)


@bp.route('/delete-product/<int:id>', methods=['POST'])
@login_required
def delete_product(id):
    if current_user.role != 'vendor':
        flash('Access denied: Vendor role required', 'danger')
        return redirect(url_for('main.index'))

    product = Product.query.get_or_404(id)
    if product.vendor_id != current_user.id:
        flash('You can only delete your own products', 'danger')
        return redirect(url_for('vendor.products'))

    # Remove associated image
    if product.image:
        filepath = os.path.join('app/static/images/products', product.image)
        if os.path.exists(filepath):
            os.remove(filepath)

    db.session.delete(product)
    db.session.commit()
    flash('Product deleted successfully!', 'success')
    return redirect(url_for('vendor.products'))