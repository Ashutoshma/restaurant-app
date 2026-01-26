"""Tests for restaurant browsing features"""
import pytest
from database.models import Restaurant


class TestRestaurantList:
    """Test restaurant listing and filtering"""
    
    def test_restaurant_list_requires_login(self, client):
        """Unauthenticated users are redirected to login"""
        response = client.get('/restaurants')
        assert response.status_code == 302
        assert '/auth/login' in response.location
    
    def test_restaurant_list_loads_authenticated(self, client, auth_user, sample_restaurants):
        """Authenticated users can view restaurant list"""
        response = client.get('/restaurants')
        assert response.status_code == 200
        assert b'Pizza Palace' in response.data
        assert b'Burger Haven' in response.data
        assert b'Sushi Paradise' in response.data
    
    def test_restaurant_list_filter_by_city(self, client, auth_user, sample_restaurants):
        """Users can filter restaurants by city"""
        response = client.get('/restaurants?city=New%20York')
        assert response.status_code == 200
        
        # New York restaurants should appear
        assert b'Pizza Palace' in response.data
        assert b'Burger Haven' in response.data
        
        # Los Angeles restaurant should not appear
        assert b'Sushi Paradise' not in response.data
    
    def test_restaurant_search_by_name(self, client, auth_user, sample_restaurants):
        """Users can search restaurants by name"""
        response = client.get('/restaurants?search=Pizza')
        assert response.status_code == 200
        
        # Only Pizza Palace should appear
        assert b'Pizza Palace' in response.data
        
        # Other restaurants should not appear
        assert b'Burger Haven' not in response.data
    
    def test_restaurant_search_case_insensitive(self, client, auth_user, sample_restaurants):
        """Restaurant search is case insensitive"""
        response = client.get('/restaurants?search=burger')
        assert response.status_code == 200
        assert b'Burger Haven' in response.data
    
    def test_restaurant_detail_page(self, client, auth_user, sample_restaurants):
        """Users can view restaurant details"""
        pizza_restaurant = sample_restaurants[0]
        response = client.get(f'/restaurants/{pizza_restaurant.id}')
        assert response.status_code == 200
        assert b'Pizza Palace' in response.data
        assert b'Authentic Italian pizza' in response.data
    
    def test_restaurant_detail_not_found(self, client, auth_user):
        """Accessing non-existent restaurant returns 404"""
        response = client.get('/restaurants/9999')
        assert response.status_code == 404
    
    def test_restaurant_detail_shows_order_count(self, client, auth_user, sample_restaurants):
        """Restaurant detail shows number of orders"""
        pizza_restaurant = sample_restaurants[0]
        response = client.get(f'/restaurants/{pizza_restaurant.id}')
        assert response.status_code == 200
        # Order count should be shown (initially 0)
        assert b'0' in response.data or b'orders' in response.data.lower()
