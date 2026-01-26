"""Menu and menu items routes"""
from flask import Blueprint, render_template, jsonify
from flask_login import login_required
from database.postgres import SessionLocal
from database.models import Restaurant
from database.firestore import firestore_db

bp = Blueprint('menu', __name__, url_prefix='/menu')


@bp.route('/restaurants/<int:restaurant_id>/items', methods=['GET'])
@login_required
def restaurant_menu(restaurant_id):
    """
    Display menu items for a specific restaurant.
    
    Fetches items from Firestore collection and displays them
    organized by category.
    
    Args:
        restaurant_id: ID of the restaurant
    
    Returns:
        Rendered HTML template with menu items grouped by category
    """
    session = SessionLocal()
    try:
        # Verify restaurant exists
        restaurant = session.query(Restaurant).filter_by(id=restaurant_id).first()
        
        if not restaurant:
            return render_template('errors/404.html'), 404
        
        # Get menu items from Firestore using Firestore document ID
        # Convert restaurant ID to Firestore format
        firestore_restaurant_id = restaurant.name.lower().replace(' ', '_')
        menu_items = firestore_db.get_menu_items(firestore_restaurant_id)
        
        # Group items by category
        items_by_category = {}
        for item in menu_items:
            category = item.get('category', 'Other')
            if category not in items_by_category:
                items_by_category[category] = []
            items_by_category[category].append(item)
        
        return render_template(
            'menu/items.html',
            restaurant=restaurant,
            items_by_category=items_by_category,
            all_items=menu_items
        )
    
    finally:
        session.close()


@bp.route('/restaurants/<int:restaurant_id>/items/api', methods=['GET'])
@login_required
def restaurant_menu_api(restaurant_id):
    """
    Return menu items as JSON API.
    
    Args:
        restaurant_id: ID of the restaurant
    
    Returns:
        JSON response with menu items list
    """
    session = SessionLocal()
    try:
        # Verify restaurant exists
        restaurant = session.query(Restaurant).filter_by(id=restaurant_id).first()
        
        if not restaurant:
            return jsonify({'error': 'Restaurant not found'}), 404
        
        # Get menu items from Firestore
        firestore_restaurant_id = restaurant.name.lower().replace(' ', '_')
        menu_items = firestore_db.get_menu_items(firestore_restaurant_id)
        
        return jsonify({
            'success': True,
            'restaurant_id': restaurant_id,
            'restaurant_name': restaurant.name,
            'items': menu_items
        })
    
    finally:
        session.close()
