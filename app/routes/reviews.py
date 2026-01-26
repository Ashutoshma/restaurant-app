"""Review and rating routes"""
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from database.postgres import SessionLocal
from database.models import Restaurant
from database.firestore import firestore_db
from app.reviews.forms import ReviewForm

bp = Blueprint('reviews', __name__, url_prefix='/reviews')


@bp.route('/restaurants/<int:restaurant_id>/submit', methods=['GET', 'POST'])
@login_required
def submit_review(restaurant_id):
    """
    Submit a review for a restaurant.
    
    Args:
        restaurant_id: ID of the restaurant to review
        
    Returns:
        Form page (GET) or redirect to restaurant detail (POST)
    """
    session = SessionLocal()
    try:
        # Verify restaurant exists
        restaurant = session.query(Restaurant).filter_by(id=restaurant_id).first()
        if not restaurant:
            return render_template('errors/404.html'), 404
        
        form = ReviewForm()
        if form.validate_on_submit():
            try:
                # Prepare review data
                review_data = {
                    'restaurant_id': restaurant.name.lower().replace(' ', '_'),
                    'user_id': current_user.id,
                    'username': current_user.username,
                    'rating': form.rating.data,
                    'text': form.text.data,
                    'created_at': __import__('datetime').datetime.utcnow().isoformat()
                }
                
                # Store review in Firestore
                success = firestore_db.add_review(
                    restaurant.name.lower().replace(' ', '_'),
                    current_user.id,
                    review_data
                )
                
                if success:
                    flash('Your review has been submitted!', 'success')
                    return redirect(url_for('restaurants.detail', restaurant_id=restaurant_id))
                else:
                    flash('Error submitting review. Please try again.', 'error')
            
            except Exception as e:
                flash(f'Error submitting review: {str(e)}', 'error')
        
        return render_template('reviews/form.html', form=form, restaurant=restaurant)
    
    finally:
        session.close()


@bp.route('/restaurants/<int:restaurant_id>/list', methods=['GET'])
@login_required
def list_reviews(restaurant_id):
    """
    Get reviews for a restaurant as JSON or HTML.
    
    Args:
        restaurant_id: ID of the restaurant
        
    Returns:
        JSON reviews or HTML template
    """
    session = SessionLocal()
    try:
        # Verify restaurant exists
        restaurant = session.query(Restaurant).filter_by(id=restaurant_id).first()
        if not restaurant:
            return jsonify({'error': 'Restaurant not found'}), 404
        
        # Get reviews from Firestore
        firestore_restaurant_id = restaurant.name.lower().replace(' ', '_')
        reviews = firestore_db.get_reviews(firestore_restaurant_id)
        
        # Return as JSON
        return jsonify({
            'success': True,
            'restaurant_id': restaurant_id,
            'reviews': reviews,
            'average_rating': calculate_average_rating(reviews)
        })
    
    finally:
        session.close()


def calculate_average_rating(reviews):
    """
    Calculate average rating from reviews list.
    
    Args:
        reviews: List of review dictionaries
        
    Returns:
        float: Average rating (0-5), or 0 if no reviews
    """
    if not reviews:
        return 0.0
    
    total = sum(review.get('rating', 0) for review in reviews)
    return round(total / len(reviews), 1)


def get_restaurant_average_rating(restaurant_id):
    """
    Get average rating for a restaurant.
    
    Args:
        restaurant_id: Firestore restaurant ID
        
    Returns:
        float: Average rating (0-5)
    """
    reviews = firestore_db.get_reviews(restaurant_id)
    return calculate_average_rating(reviews)
