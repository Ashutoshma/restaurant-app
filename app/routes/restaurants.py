"""Restaurant browsing and management routes"""
from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required
from sqlalchemy import func
from database.postgres import SessionLocal
from database.models import Restaurant, Order

bp = Blueprint('restaurants', __name__, url_prefix='/restaurants')


@bp.route('', methods=['GET'])
@login_required
def list_restaurants():
    """
    List all restaurants with optional filtering.
    
    Query parameters:
    - city: Filter by city
    - search: Search by restaurant name
    
    Returns:
        Rendered HTML template with restaurants list
    """
    session = SessionLocal()
    try:
        query = session.query(Restaurant)
        
        # Filter by city if provided
        city = request.args.get('city')
        if city:
            query = query.filter_by(city=city)
        
        # Search by name if provided
        search = request.args.get('search')
        if search:
            query = query.filter(Restaurant.name.ilike(f'%{search}%'))
        
        # Get all restaurants
        restaurants = query.all()
        
        # Get unique cities for filter dropdown
        all_cities = session.query(
            Restaurant.city
        ).distinct().all()
        cities = [city[0] for city in all_cities if city[0]]
        
        return render_template(
            'restaurants/list.html',
            restaurants=restaurants,
            cities=cities,
            selected_city=city,
            selected_search=search
        )
    
    finally:
        session.close()


@bp.route('/<int:restaurant_id>', methods=['GET'])
@login_required
def detail(restaurant_id):
    """
    Display restaurant detail page with stats and information.
    
    Args:
        restaurant_id: ID of the restaurant to display
    
    Returns:
        Rendered HTML template with restaurant details
    """
    session = SessionLocal()
    try:
        # Get restaurant
        restaurant = session.query(Restaurant).filter_by(id=restaurant_id).first()
        
        if not restaurant:
            return render_template('errors/404.html'), 404
        
        # Get restaurant stats
        order_count = session.query(func.count(Order.id)).filter_by(
            restaurant_id=restaurant_id
        ).scalar()
        
        return render_template(
            'restaurants/detail.html',
            restaurant=restaurant,
            order_count=order_count
        )
    
    finally:
        session.close()
