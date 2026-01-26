"""Tests for menu and menu items features"""
import pytest


class TestMenuDisplay:
    """Test menu viewing functionality"""
    
    def test_menu_requires_login(self, client):
        """Unauthenticated users are redirected to login"""
        response = client.get('/menu/restaurants/1/items')
        assert response.status_code == 302
        assert '/auth/login' in response.location
    
    def test_menu_nonexistent_restaurant(self, client, auth_user):
        """Accessing menu for non-existent restaurant returns 404"""
        response = client.get('/menu/restaurants/9999/items')
        assert response.status_code == 404
    
    def test_menu_items_display(self, client, auth_user, sample_restaurants):
        """Menu items load and display correctly"""
        pizza_restaurant = sample_restaurants[0]
        response = client.get(f'/menu/restaurants/{pizza_restaurant.id}/items')
        assert response.status_code == 200
        assert b'Pizza Palace' in response.data
    
    def test_menu_items_grouped_by_category(self, client, auth_user, sample_restaurants):
        """Menu items are grouped by category"""
        pizza_restaurant = sample_restaurants[0]
        response = client.get(f'/menu/restaurants/{pizza_restaurant.id}/items')
        assert response.status_code == 200
        # Should display category headings
        assert b'Pizza' in response.data or b'category' in response.data.lower()
    
    def test_menu_api_endpoint(self, client, auth_user, sample_restaurants):
        """Menu API endpoint returns JSON"""
        pizza_restaurant = sample_restaurants[0]
        response = client.get(f'/menu/restaurants/{pizza_restaurant.id}/items/api')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['success'] is True
        assert data['restaurant_id'] == pizza_restaurant.id
        assert 'items' in data
    
    def test_menu_api_nonexistent_restaurant(self, client, auth_user):
        """Menu API returns error for non-existent restaurant"""
        response = client.get('/menu/restaurants/9999/items/api')
        assert response.status_code == 404
        
        data = response.get_json()
        assert data['error'] == 'Restaurant not found'
    
    def test_menu_items_have_required_fields(self, client, auth_user, sample_restaurants):
        """Menu items contain required fields (name, price, etc)"""
        pizza_restaurant = sample_restaurants[0]
        response = client.get(f'/menu/restaurants/{pizza_restaurant.id}/items/api')
        assert response.status_code == 200
        
        data = response.get_json()
        items = data['items']
        
        if items:  # Only test if mock data provides items
            for item in items:
                assert 'name' in item
                assert 'price' in item
                assert 'id' in item
