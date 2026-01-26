"""Shopping cart routes and operations"""
from flask import Blueprint, render_template, request, jsonify, session as flask_session
from flask_login import login_required
from database.postgres import SessionLocal
from database.models import Restaurant
from database.firestore import firestore_db

bp = Blueprint('cart', __name__, url_prefix='/cart')


def get_cart():
    """
    Get current cart from session.
    
    Returns:
        dict: Cart data structure {restaurant_id: {items: [...], total: X}}
    """
    if 'cart' not in flask_session:
        flask_session['cart'] = {}
    return flask_session['cart']


def calculate_item_total(item):
    """
    Calculate total for a cart item.
    
    Args:
        item: Cart item with quantity and price
    
    Returns:
        float: Item total (quantity * price)
    """
    return item['quantity'] * item['price']


def calculate_cart_total(items):
    """
    Calculate total for all items in cart.
    
    Args:
        items: List of cart items
    
    Returns:
        float: Total price rounded to 2 decimals
    """
    total = sum(calculate_item_total(item) for item in items)
    return round(total, 2)


@bp.route('', methods=['GET'])
@login_required
def view_cart():
    """
    Display shopping cart page.
    
    Shows all items in cart grouped by restaurant with totals.
    
    Returns:
        Rendered HTML template with cart contents
    """
    cart = get_cart()
    cart_data = []
    grand_total = 0
    
    session = SessionLocal()
    try:
        for restaurant_id_str, restaurant_cart in cart.items():
            restaurant_id = int(restaurant_id_str)
            restaurant = session.query(Restaurant).filter_by(id=restaurant_id).first()
            
            if restaurant:
                items = restaurant_cart.get('items', [])
                total = calculate_cart_total(items)
                grand_total += total
                
                cart_data.append({
                    'restaurant': restaurant,
                    'items': items,
                    'total': total
                })
        
        return render_template(
            'cart.html',
            cart_data=cart_data,
            grand_total=round(grand_total, 2),
            item_count=sum(len(rc.get('items', [])) for rc in cart.values())
        )
    
    finally:
        session.close()


@bp.route('/add', methods=['POST'])
@login_required
def add_item():
    """
    Add item to shopping cart via AJAX.
    
    JSON body:
    {
        'restaurant_id': int,
        'item_id': str,
        'name': str,
        'price': float,
        'quantity': int (default 1)
    }
    
    Returns:
        JSON response with success status and updated cart
    """
    try:
        data = request.get_json()
        restaurant_id = str(data.get('restaurant_id'))
        item_id = data.get('item_id')
        name = data.get('name')
        price = float(data.get('price', 0))
        quantity = int(data.get('quantity', 1))
        
        # Validate inputs
        if not all([restaurant_id, item_id, name, price > 0, quantity > 0]):
            return jsonify({'success': False, 'message': 'Invalid item data'}), 400
        
        cart = get_cart()
        
        # Initialize restaurant cart if not exists
        if restaurant_id not in cart:
            cart[restaurant_id] = {'items': []}
        
        # Check if item already in cart
        items = cart[restaurant_id]['items']
        existing_item = next((i for i in items if i['item_id'] == item_id), None)
        
        if existing_item:
            # Update quantity
            existing_item['quantity'] += quantity
        else:
            # Add new item
            items.append({
                'item_id': item_id,
                'name': name,
                'price': price,
                'quantity': quantity
            })
        
        # Calculate total
        cart[restaurant_id]['total'] = calculate_cart_total(items)
        flask_session.modified = True
        
        return jsonify({
            'success': True,
            'message': f'{name} added to cart',
            'item_count': sum(len(rc.get('items', [])) for rc in cart.values()),
            'cart_total': sum(rc.get('total', 0) for rc in cart.values())
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400


@bp.route('/remove', methods=['POST'])
@login_required
def remove_item():
    """
    Remove item from shopping cart.
    
    JSON body:
    {
        'restaurant_id': int,
        'item_id': str
    }
    
    Returns:
        JSON response with success status
    """
    try:
        data = request.get_json()
        restaurant_id = str(data.get('restaurant_id'))
        item_id = data.get('item_id')
        
        cart = get_cart()
        
        if restaurant_id in cart:
            items = cart[restaurant_id]['items']
            # Remove item
            items[:] = [i for i in items if i['item_id'] != item_id]
            
            # Recalculate total
            if items:
                cart[restaurant_id]['total'] = calculate_cart_total(items)
            else:
                # Remove restaurant from cart if no items
                del cart[restaurant_id]
            
            flask_session.modified = True
        
        return jsonify({
            'success': True,
            'message': 'Item removed from cart',
            'item_count': sum(len(rc.get('items', [])) for rc in cart.values()),
            'cart_total': sum(rc.get('total', 0) for rc in cart.values())
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400


@bp.route('/update', methods=['POST'])
@login_required
def update_item():
    """
    Update item quantity in shopping cart.
    
    JSON body:
    {
        'restaurant_id': int,
        'item_id': str,
        'quantity': int
    }
    
    Returns:
        JSON response with success status
    """
    try:
        data = request.get_json()
        restaurant_id = str(data.get('restaurant_id'))
        item_id = data.get('item_id')
        quantity = int(data.get('quantity', 1))
        
        # Validate quantity
        if quantity < 0:
            return jsonify({'success': False, 'message': 'Invalid quantity'}), 400
        
        cart = get_cart()
        
        if restaurant_id in cart:
            items = cart[restaurant_id]['items']
            
            if quantity == 0:
                # Remove item if quantity is 0
                items[:] = [i for i in items if i['item_id'] != item_id]
            else:
                # Update quantity
                for item in items:
                    if item['item_id'] == item_id:
                        item['quantity'] = quantity
                        break
            
            # Recalculate total
            if items:
                cart[restaurant_id]['total'] = calculate_cart_total(items)
            else:
                # Remove restaurant from cart if no items
                del cart[restaurant_id]
            
            flask_session.modified = True
        
        return jsonify({
            'success': True,
            'message': 'Cart updated',
            'item_count': sum(len(rc.get('items', [])) for rc in cart.values()),
            'cart_total': sum(rc.get('total', 0) for rc in cart.values())
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400


@bp.route('/clear', methods=['POST'])
@login_required
def clear_cart():
    """
    Clear entire shopping cart.
    
    Returns:
        JSON response with success status
    """
    flask_session['cart'] = {}
    flask_session.modified = True
    
    return jsonify({
        'success': True,
        'message': 'Cart cleared'
    })
