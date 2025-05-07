from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Product, Cart, Order

bp = Blueprint('user', __name__)


@bp.route('/cart')
@login_required
def cart():
    cart_items = Cart.query.filter_by(user_id=current_user.id) \
        .join(Product) \
        .add_columns(
        Product.id,
        Product.name,
        Product.price,
        Product.image,
        Cart.quantity
    ).all()

    subtotal = sum(item.price * item.quantity for item in cart_items)
    tax = subtotal * 0.1  # Example 10% tax
    total = subtotal + tax

    return render_template('user/cart.html',
                           cart_items=cart_items,
                           subtotal=subtotal,
                           tax=tax,
                           total=total)


@bp.route('/add-to-cart/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)

    # Check if product is already in cart
    cart_item = Cart.query.filter_by(
        user_id=current_user.id,
        product_id=product_id
    ).first()

    if cart_item:
        cart_item.quantity += 1
    else:
        cart_item = Cart(
            user_id=current_user.id,
            product_id=product_id,
            quantity=1
        )
        db.session.add(cart_item)

    db.session.commit()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        cart_count = Cart.query.filter_by(user_id=current_user.id).count()
        return jsonify({
            'success': True,
            'cart_count': cart_count,
            'message': f'{product.name} added to cart!'
        })

    flash(f'{product.name} added to cart!', 'success')
    return redirect(request.referrer or url_for('user.products'))


@bp.route('/update-cart/<int:cart_id>', methods=['POST'])
@login_required
def update_cart(cart_id):
    cart_item = Cart.query.filter_by(
        id=cart_id,
        user_id=current_user.id
    ).first_or_404()

    action = request.form.get('action')

    if action == 'increment':
        cart_item.quantity += 1
    elif action == 'decrement':
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
        else:
            db.session.delete(cart_item)
    elif action == 'remove':
        db.session.delete(cart_item)
    else:
        quantity = request.form.get('quantity', type=int)
        if quantity and quantity > 0:
            cart_item.quantity = quantity

    db.session.commit()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        cart_count = Cart.query.filter_by(user_id=current_user.id).count()
        subtotal = sum(item.product.price * item.quantity
                       for item in current_user.cart_items)
        tax = subtotal * 0.1
        total = subtotal + tax

        return jsonify({
            'success': True,
            'cart_count': cart_count,
            'subtotal': f'{subtotal:.2f}',
            'tax': f'{tax:.2f}',
            'total': f'{total:.2f}'
        })

    flash('Cart updated!', 'success')
    return redirect(url_for('user.cart'))


@bp.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    if not current_user.cart_items:
        flash('Your cart is empty!', 'warning')
        return redirect(url_for('user.products'))

    if request.method == 'POST':
        payment_method = request.form.get('payment_method')

        # Create orders from cart items
        for cart_item in current_user.cart_items:
            order = Order(
                user_id=current_user.id,
                product_id=cart_item.product_id,
                quantity=cart_item.quantity,
                total_price=cart_item.product.price * cart_item.quantity,
                payment_method=payment_method,
                status='completed'
            )
            db.session.add(order)

            # Update product quantity
            cart_item.product.quantity -= cart_item.quantity

        # Clear cart
        Cart.query.filter_by(user_id=current_user.id).delete()

        db.session.commit()
        return redirect(url_for('user.order_confirmation'))

    cart_items = current_user.cart_items
    subtotal = sum(item.product.price * item.quantity for item in cart_items)
    tax = subtotal * 0.1
    total = subtotal + tax

    return render_template('user/checkout.html',
                           cart_items=cart_items,
                           subtotal=subtotal,
                           tax=tax,
                           total=total)


@bp.route('/order-confirmation')
@login_required
def order_confirmation():
    return render_template('user/order_confirmation.html')