"""Order creation, management, and tracking routes"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session as flask_session
from flask_login import login_required, current_user
from database.postgres import SessionLocal
from database.models import Order, OrderItem, Restaurant, Payment, OrderStatus, PaymentStatus
from app.orders.forms import OrderForm

bp = Blueprint('orders', __name__, url_prefix='/orders')


@bp.route('', methods=['GET'])
@login_required
def list_orders():
    """
    Display user's order history.
    
    Shows all orders for the logged-in user sorted by most recent first.
    
    Returns:
        Rendered HTML template with user's orders
    """
    session = SessionLocal()
    try:
        # Get all orders for current user
        orders = session.query(Order).filter_by(
            user_id=current_user.id
        ).order_by(Order.created_at.desc()).all()
        
        return render_template(
            'orders/list.html',
            orders=orders
        )
    
    finally:
        session.close()


@bp.route('/<int:order_id>', methods=['GET'])
@login_required
def detail(order_id):
    """
    Display detailed information for a specific order.
    
    Shows order items, restaurant info, status, and delivery details.
    Verifies user owns the order before displaying.
    
    Args:
        order_id: ID of the order to display
    
    Returns:
        Rendered HTML template with order details or 404 if not found
    """
    session = SessionLocal()
    try:
        # Get order and verify ownership
        order = session.query(Order).filter_by(
            id=order_id,
            user_id=current_user.id
        ).first()
        
        if not order:
            return render_template('errors/404.html'), 404
        
        # Get restaurant info
        restaurant = session.query(Restaurant).filter_by(
            id=order.restaurant_id
        ).first()
        
        # Get payment info
        payment = session.query(Payment).filter_by(
            order_id=order_id
        ).first()
        
        return render_template(
            'orders/detail.html',
            order=order,
            restaurant=restaurant,
            payment=payment
        )
    
    finally:
        session.close()


@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """
    Create new order from shopping cart.
    
    GET: Display order creation form with cart review
    POST: Process order creation with validation
    
    Returns:
        Rendered form template or redirect to order confirmation
    """
    cart = flask_session.get('cart', {})
    
    # Validate cart not empty
    if not cart:
        flash('Your cart is empty. Add items before creating an order.', 'warning')
        return redirect(url_for('restaurants.list_restaurants'))
    
    # Validate single restaurant per order
    if len(cart) > 1:
        flash('You can only order from one restaurant at a time.', 'error')
        return redirect(url_for('cart.view_cart'))
    
    restaurant_id = int(list(cart.keys())[0])
    cart_items = cart[restaurant_id]['items']
    cart_total = cart[restaurant_id]['total']
    
    session = SessionLocal()
    try:
        # Verify restaurant exists
        restaurant = session.query(Restaurant).filter_by(
            id=restaurant_id
        ).first()
        
        if not restaurant:
            flash('Selected restaurant no longer exists.', 'error')
            return redirect(url_for('restaurants.list_restaurants'))
        
        form = OrderForm()
        
        if form.validate_on_submit():
            try:
                # Create order
                order = Order(
                    user_id=current_user.id,
                    restaurant_id=restaurant_id,
                    total_price=cart_total,
                    delivery_address=form.delivery_address.data,
                    special_instructions=form.special_instructions.data,
                    notes=form.notes.data,
                    status=OrderStatus.PENDING
                )
                session.add(order)
                session.flush()  # Get order ID without committing
                
                # Create order items
                for item in cart_items:
                    order_item = OrderItem(
                        order_id=order.id,
                        menu_item_name=item['name'],
                        restaurant_id=restaurant_id,
                        quantity=item['quantity'],
                        unit_price=item['price']
                    )
                    session.add(order_item)
                
                # Create payment record
                payment = Payment(
                    order_id=order.id,
                    amount=cart_total,
                    status=PaymentStatus.PENDING
                )
                session.add(payment)
                
                # Commit transaction
                session.commit()
                
                # Clear cart
                flask_session['cart'] = {}
                flask_session.modified = True
                
                flash(f'Order #{order.id} created successfully!', 'success')
                return redirect(url_for('orders.detail', order_id=order.id))
            
            except Exception as e:
                session.rollback()
                flash(f'Error creating order: {str(e)}', 'error')
        
        return render_template(
            'orders/create.html',
            form=form,
            restaurant=restaurant,
            cart_items=cart_items,
            cart_total=cart_total
        )
    
    finally:
        session.close()


@bp.route('/<int:order_id>/cancel', methods=['POST'])
@login_required
def cancel(order_id):
    """
    Cancel a pending order.
    
    Only allows cancellation of PENDING orders.
    User must own the order.
    
    Args:
        order_id: ID of the order to cancel
    
    Returns:
        Redirect to order detail page
    """
    session = SessionLocal()
    try:
        # Get order and verify ownership
        order = session.query(Order).filter_by(
            id=order_id,
            user_id=current_user.id
        ).first()
        
        if not order:
            flash('Order not found.', 'error')
            return redirect(url_for('orders.list_orders'))
        
        # Can only cancel pending orders
        if order.status != OrderStatus.PENDING:
            flash(f'Cannot cancel {order.status.value} orders.', 'error')
            return redirect(url_for('orders.detail', order_id=order_id))
        
        # Update order status
        order.status = OrderStatus.CANCELLED
        
        # Update payment status
        payment = session.query(Payment).filter_by(order_id=order_id).first()
        if payment:
            payment.status = PaymentStatus.REFUNDED
        
        session.commit()
        flash(f'Order #{order_id} has been cancelled.', 'success')
        
    except Exception as e:
        session.rollback()
        flash(f'Error cancelling order: {str(e)}', 'error')
    
    finally:
        session.close()
    
    return redirect(url_for('orders.detail', order_id=order_id))
