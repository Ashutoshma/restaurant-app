"""Admin routes for order management and dashboard"""
from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from sqlalchemy import func
from database.postgres import SessionLocal
from database.models import Order, OrderStatus, User
from app.services.notifications import notify_status_change

bp = Blueprint('admin', __name__, url_prefix='/admin')


def admin_required(f):
    """Decorator to require admin access"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Access denied. Admin privileges required.', 'error')
            return redirect(url_for('main.home')), 403
        return f(*args, **kwargs)
    return decorated_function


@bp.route('/orders', methods=['GET'])
@login_required
@admin_required
def orders_dashboard():
    """
    Admin dashboard showing all orders.
    
    Query parameters:
    - status: Filter by order status
    
    Returns:
        Rendered admin dashboard template
    """
    session = SessionLocal()
    try:
        query = session.query(Order)
        
        # Filter by status if provided
        status_filter = request.args.get('status')
        if status_filter:
            try:
                status = OrderStatus[status_filter.upper()]
                query = query.filter_by(status=status)
            except KeyError:
                pass
        
        # Get orders sorted by most recent
        orders = query.order_by(Order.created_at.desc()).all()
        
        # Get order statistics
        stats = {
            'total_orders': session.query(func.count(Order.id)).scalar(),
            'pending': session.query(func.count(Order.id)).filter_by(status=OrderStatus.PENDING).scalar(),
            'confirmed': session.query(func.count(Order.id)).filter_by(status=OrderStatus.CONFIRMED).scalar(),
            'preparing': session.query(func.count(Order.id)).filter_by(status=OrderStatus.PREPARING).scalar(),
            'ready': session.query(func.count(Order.id)).filter_by(status=OrderStatus.READY).scalar(),
            'delivered': session.query(func.count(Order.id)).filter_by(status=OrderStatus.DELIVERED).scalar(),
            'cancelled': session.query(func.count(Order.id)).filter_by(status=OrderStatus.CANCELLED).scalar(),
        }
        
        # Get all statuses for filter dropdown
        all_statuses = [s.name for s in OrderStatus]
        
        return render_template(
            'admin/orders.html',
            orders=orders,
            stats=stats,
            all_statuses=all_statuses,
            selected_status=status_filter
        )
    
    finally:
        session.close()


@bp.route('/orders/<int:order_id>', methods=['GET'])
@login_required
@admin_required
def order_detail(order_id):
    """
    View detailed information for an order.
    
    Args:
        order_id: ID of the order
        
    Returns:
        Rendered order detail template or 404
    """
    session = SessionLocal()
    try:
        order = session.query(Order).filter_by(id=order_id).first()
        
        if not order:
            return render_template('errors/404.html'), 404
        
        # Get user info
        user = session.query(User).filter_by(id=order.user_id).first()
        
        return render_template(
            'admin/order_detail.html',
            order=order,
            user=user
        )
    
    finally:
        session.close()


@bp.route('/orders/<int:order_id>/status', methods=['POST'])
@login_required
@admin_required
def update_order_status(order_id):
    """
    Update order status.
    
    JSON body:
    {
        'status': 'confirmed|preparing|ready|delivered|cancelled'
    }
    
    Args:
        order_id: ID of the order
        
    Returns:
        JSON response or redirect
    """
    session = SessionLocal()
    try:
        data = request.get_json() if request.is_json else request.form
        new_status_str = data.get('status', '').upper()
        
        # Validate status
        try:
            new_status = OrderStatus[new_status_str]
        except KeyError:
            return jsonify({'success': False, 'message': 'Invalid status'}), 400
        
        # Get order
        order = session.query(Order).filter_by(id=order_id).first()
        if not order:
            return jsonify({'success': False, 'message': 'Order not found'}), 404
        
        # Validate status transition
        old_status = order.status
        
        # Simple validation: can't go backwards in workflow
        valid_transitions = {
            OrderStatus.PENDING: [OrderStatus.CONFIRMED, OrderStatus.CANCELLED],
            OrderStatus.CONFIRMED: [OrderStatus.PREPARING, OrderStatus.CANCELLED],
            OrderStatus.PREPARING: [OrderStatus.READY, OrderStatus.CANCELLED],
            OrderStatus.READY: [OrderStatus.DELIVERED],
            OrderStatus.DELIVERED: [],
            OrderStatus.CANCELLED: [],
        }
        
        if new_status not in valid_transitions.get(old_status, []):
            if new_status == old_status:
                return jsonify({'success': False, 'message': 'Status unchanged'}), 400
            else:
                return jsonify({'success': False, 'message': f'Cannot transition from {old_status.value} to {new_status.value}'}), 400
        
        # Update status
        order.status = new_status
        session.commit()
        
        # Send notification
        notify_status_change(order, old_status, new_status)
        
        flash(f'Order #{order_id} status updated to {new_status.value}', 'success')
        
        # Return based on request type
        if request.is_json:
            return jsonify({'success': True, 'message': 'Status updated'})
        else:
            return redirect(url_for('admin.order_detail', order_id=order_id))
    
    except Exception as e:
        session.rollback()
        error_msg = f'Error updating order: {str(e)}'
        if request.is_json:
            return jsonify({'success': False, 'message': error_msg}), 500
        else:
            flash(error_msg, 'error')
            return redirect(url_for('admin.order_detail', order_id=order_id))
    
    finally:
        session.close()


@bp.route('/stats', methods=['GET'])
@login_required
@admin_required
def stats():
    """
    Get admin statistics as JSON.
    
    Returns:
        JSON with order statistics
    """
    session = SessionLocal()
    try:
        stats = {
            'total_orders': session.query(func.count(Order.id)).scalar(),
            'total_revenue': float(session.query(func.sum(Order.total_price)).scalar() or 0),
            'pending': session.query(func.count(Order.id)).filter_by(status=OrderStatus.PENDING).scalar(),
            'confirmed': session.query(func.count(Order.id)).filter_by(status=OrderStatus.CONFIRMED).scalar(),
            'preparing': session.query(func.count(Order.id)).filter_by(status=OrderStatus.PREPARING).scalar(),
            'ready': session.query(func.count(Order.id)).filter_by(status=OrderStatus.READY).scalar(),
            'delivered': session.query(func.count(Order.id)).filter_by(status=OrderStatus.DELIVERED).scalar(),
            'cancelled': session.query(func.count(Order.id)).filter_by(status=OrderStatus.CANCELLED).scalar(),
        }
        
        return jsonify(stats)
    
    finally:
        session.close()
