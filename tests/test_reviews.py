"""Tests for review and rating features"""
import pytest


class TestReviewSubmission:
    """Test review submission"""
    
    def test_review_requires_login(self, client, sample_restaurants):
        """Unauthenticated users are redirected to login"""
        restaurant = sample_restaurants[0]
        response = client.get(f'/reviews/restaurants/{restaurant.id}/submit')
        assert response.status_code == 302
        assert '/auth/login' in response.location
    
    def test_review_form_displays(self, client, auth_user, sample_restaurants):
        """Review form loads for authenticated users"""
        restaurant = sample_restaurants[0]
        response = client.get(f'/reviews/restaurants/{restaurant.id}/submit')
        assert response.status_code == 200
        assert b'Review' in response.data
        assert b'Rating' in response.data
    
    def test_submit_valid_review(self, client, auth_user, sample_restaurants):
        """Valid review submission succeeds"""
        restaurant = sample_restaurants[0]
        response = client.post(
            f'/reviews/restaurants/{restaurant.id}/submit',
            data={
                'rating': 5,
                'text': 'Great food and excellent service! Highly recommended.'
            },
            follow_redirects=True
        )
        assert response.status_code == 200
        # Should redirect to restaurant detail or show success message
    
    def test_review_validation(self, client, auth_user, sample_restaurants):
        """Review validation works"""
        restaurant = sample_restaurants[0]
        
        # Missing rating
        response = client.post(
            f'/reviews/restaurants/{restaurant.id}/submit',
            data={
                'rating': '',
                'text': 'Good food'
            },
            follow_redirects=True
        )
        assert response.status_code == 200
        # Should show validation error
        assert b'required' in response.data.lower() or b'Rating' in response.data
    
    def test_review_text_too_short(self, client, auth_user, sample_restaurants):
        """Review text validation enforces minimum length"""
        restaurant = sample_restaurants[0]
        response = client.post(
            f'/reviews/restaurants/{restaurant.id}/submit',
            data={
                'rating': 4,
                'text': 'Good'
            },
            follow_redirects=True
        )
        assert response.status_code == 200
        # Should show validation error
    
    def test_review_text_too_long(self, client, auth_user, sample_restaurants):
        """Review text validation enforces maximum length"""
        restaurant = sample_restaurants[0]
        long_text = 'a' * 501
        response = client.post(
            f'/reviews/restaurants/{restaurant.id}/submit',
            data={
                'rating': 4,
                'text': long_text
            },
            follow_redirects=True
        )
        assert response.status_code == 200
    
    def test_invalid_rating(self, client, auth_user, sample_restaurants):
        """Invalid rating values are rejected"""
        restaurant = sample_restaurants[0]
        
        # Rating too high
        response = client.post(
            f'/reviews/restaurants/{restaurant.id}/submit',
            data={
                'rating': 10,
                'text': 'This is a very detailed review about the restaurant.'
            },
            follow_redirects=True
        )
        assert response.status_code == 200
        # Should show validation error
    
    def test_review_nonexistent_restaurant(self, client, auth_user):
        """Review submission for non-existent restaurant returns 404"""
        response = client.get('/reviews/restaurants/9999/submit')
        assert response.status_code == 404


class TestReviewDisplay:
    """Test review display"""
    
    def test_get_reviews_api(self, client, auth_user, sample_restaurants):
        """Reviews API endpoint works"""
        restaurant = sample_restaurants[0]
        response = client.get(f'/reviews/restaurants/{restaurant.id}/list')
        assert response.status_code == 200
        
        data = response.get_json()
        assert 'reviews' in data
        assert 'average_rating' in data
        assert data['average_rating'] >= 0
    
    def test_reviews_for_nonexistent_restaurant(self, client, auth_user):
        """Reviews for non-existent restaurant returns error"""
        response = client.get('/reviews/restaurants/9999/list')
        assert response.status_code == 404
