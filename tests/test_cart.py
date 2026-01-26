"""Tests for shopping cart functionality"""
import pytest
import json


class TestShoppingCart:
    """Test shopping cart operations"""
    
    def test_cart_requires_login(self, client):
        """Unauthenticated users are redirected to login"""
        response = client.get('/cart')
        assert response.status_code == 302
        assert '/auth/login' in response.location
    
    def test_view_empty_cart(self, client, auth_user):
        """Users can view empty cart"""
        response = client.get('/cart')
        assert response.status_code == 200
        assert b'cart' in response.data.lower()
    
    def test_add_item_to_cart(self, client, auth_user):
        """Items can be added to cart"""
        response = client.post('/cart/add', json={
            'restaurant_id': 1,
            'item_id': 'pizza_1',
            'name': 'Margherita Pizza',
            'price': 12.99,
            'quantity': 1
        })
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['success'] is True
        assert 'cart_total' in data
    
    def test_add_invalid_item_to_cart(self, client, auth_user):
        """Adding item with invalid data fails"""
        response = client.post('/cart/add', json={
            'restaurant_id': 1,
            'item_id': '',
            'name': 'Pizza',
            'price': -5.00,
            'quantity': 0
        })
        assert response.status_code == 400
        
        data = response.get_json()
        assert data['success'] is False
    
    def test_add_multiple_items(self, client, auth_user):
        """Multiple items can be added to cart"""
        # Add first item
        client.post('/cart/add', json={
            'restaurant_id': 1,
            'item_id': 'pizza_1',
            'name': 'Margherita Pizza',
            'price': 12.99,
            'quantity': 1
        })
        
        # Add second item
        response = client.post('/cart/add', json={
            'restaurant_id': 1,
            'item_id': 'pizza_2',
            'name': 'Pepperoni Pizza',
            'price': 14.99,
            'quantity': 1
        })
        
        data = response.get_json()
        assert data['success'] is True
        assert data['item_count'] == 2
    
    def test_increase_item_quantity(self, client, auth_user):
        """Adding same item increases quantity"""
        # Add item first time
        client.post('/cart/add', json={
            'restaurant_id': 1,
            'item_id': 'pizza_1',
            'name': 'Margherita Pizza',
            'price': 12.99,
            'quantity': 1
        })
        
        # Add same item again
        response = client.post('/cart/add', json={
            'restaurant_id': 1,
            'item_id': 'pizza_1',
            'name': 'Margherita Pizza',
            'price': 12.99,
            'quantity': 1
        })
        
        data = response.get_json()
        assert data['success'] is True
        assert data['item_count'] == 1  # Still 1 item but with qty 2
    
    def test_remove_item_from_cart(self, client, auth_user):
        """Items can be removed from cart"""
        # Add item
        client.post('/cart/add', json={
            'restaurant_id': 1,
            'item_id': 'pizza_1',
            'name': 'Margherita Pizza',
            'price': 12.99,
            'quantity': 1
        })
        
        # Remove item
        response = client.post('/cart/remove', json={
            'restaurant_id': 1,
            'item_id': 'pizza_1'
        })
        
        data = response.get_json()
        assert data['success'] is True
        assert data['item_count'] == 0
    
    def test_update_item_quantity(self, client, auth_user):
        """Item quantity can be updated"""
        # Add item
        client.post('/cart/add', json={
            'restaurant_id': 1,
            'item_id': 'pizza_1',
            'name': 'Margherita Pizza',
            'price': 12.99,
            'quantity': 1
        })
        
        # Update quantity to 3
        response = client.post('/cart/update', json={
            'restaurant_id': 1,
            'item_id': 'pizza_1',
            'quantity': 3
        })
        
        data = response.get_json()
        assert data['success'] is True
    
    def test_update_item_to_zero_removes_item(self, client, auth_user):
        """Updating quantity to 0 removes item from cart"""
        # Add item
        client.post('/cart/add', json={
            'restaurant_id': 1,
            'item_id': 'pizza_1',
            'name': 'Margherita Pizza',
            'price': 12.99,
            'quantity': 1
        })
        
        # Update quantity to 0
        response = client.post('/cart/update', json={
            'restaurant_id': 1,
            'item_id': 'pizza_1',
            'quantity': 0
        })
        
        data = response.get_json()
        assert data['success'] is True
        assert data['item_count'] == 0
    
    def test_clear_cart(self, client, auth_user):
        """Cart can be cleared"""
        # Add item
        client.post('/cart/add', json={
            'restaurant_id': 1,
            'item_id': 'pizza_1',
            'name': 'Margherita Pizza',
            'price': 12.99,
            'quantity': 1
        })
        
        # Clear cart
        response = client.post('/cart/clear')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['success'] is True
    
    def test_cart_total_calculation(self, client, auth_user):
        """Cart total is calculated correctly"""
        # Add item with price 12.99 and quantity 2
        response = client.post('/cart/add', json={
            'restaurant_id': 1,
            'item_id': 'pizza_1',
            'name': 'Margherita Pizza',
            'price': 12.99,
            'quantity': 2
        })
        
        data = response.get_json()
        # Total should be 25.98 (12.99 * 2)
        assert abs(data['cart_total'] - 25.98) < 0.01
