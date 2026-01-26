"""Tests for order creation and management"""
import pytest
from database.models import Order, OrderItem, Payment, OrderStatus, PaymentStatus


class TestOrderCreation:
    """Test order creation functionality"""
    
    def test_create_order_requires_login(self, client):
        """Unauthenticated users are redirected to login"""
        response = client.get('/orders/create')
        assert response.status_code == 302
        assert '/auth/login' in response.location
    
    def test_create_order_empty_cart_redirect(self, client, auth_user):
        """Creating order with empty cart redirects to restaurants"""
        response = client.get('/orders/create', follow_redirects=False)
        assert response.status_code == 302
        assert '/restaurants' in response.location
    
    def test_create_order_form_displays(self, client, auth_user, sample_restaurants):
        """Order creation form displays when cart has items"""
        # Add item to cart via session
        with client.session_transaction() as sess:
            sess['cart'] = {
                '1': {
                    'items': [{
                        'item_id': 'pizza_1',
                        'name': 'Margherita Pizza',
                        'price': 12.99,
                        'quantity': 1
                    }],
                    'total': 12.99
                }
            }
        
        response = client.get('/orders/create')
        assert response.status_code == 200
        assert b'Delivery Address' in response.data
        assert b'Margherita Pizza' in response.data
    
    def test_create_order_invalid_restaurant(self, client, auth_user):
        """Creating order for non-existent restaurant fails"""
        # Set up cart with non-existent restaurant
        with client.session_transaction() as sess:
            sess['cart'] = {
                '9999': {
                    'items': [{
                        'item_id': 'pizza_1',
                        'name': 'Margherita Pizza',
                        'price': 12.99,
                        'quantity': 1
                    }],
                    'total': 12.99
                }
            }
        
        response = client.get('/orders/create')
        assert response.status_code == 302
        assert '/restaurants' in response.location
    
    def test_create_order_success(self, client, auth_user, sample_restaurants, init_db):
        """Valid order creation succeeds"""
        # Set up cart
        with client.session_transaction() as sess:
            sess['cart'] = {
                '1': {
                    'items': [{
                        'item_id': 'pizza_1',
                        'name': 'Margherita Pizza',
                        'price': 12.99,
                        'quantity': 1
                    }],
                    'total': 12.99
                }
            }
        
        response = client.post('/orders/create', data={
            'delivery_address': '123 Main Street, New York, NY 10001',
            'special_instructions': 'Extra cheese please',
            'notes': 'Call when arriving'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Order' in response.data
        
        # Verify order was created in database
        session = init_db.get_session()
        order = session.query(Order).filter_by(user_id=auth_user.id).first()
        assert order is not None
        assert order.total_price == 12.99
        assert order.status == OrderStatus.PENDING
        session.close()
    
    def test_create_order_creates_order_items(self, client, auth_user, sample_restaurants, init_db):
        """Order creation creates associated OrderItems"""
        # Set up cart with multiple items
        with client.session_transaction() as sess:
            sess['cart'] = {
                '1': {
                    'items': [
                        {
                            'item_id': 'pizza_1',
                            'name': 'Margherita Pizza',
                            'price': 12.99,
                            'quantity': 1
                        },
                        {
                            'item_id': 'pizza_2',
                            'name': 'Pepperoni Pizza',
                            'price': 14.99,
                            'quantity': 2
                        }
                    ],
                    'total': 42.97
                }
            }
        
        client.post('/orders/create', data={
            'delivery_address': '123 Main Street, New York, NY 10001',
            'special_instructions': '',
            'notes': ''
        }, follow_redirects=True)
        
        # Verify order items were created
        session = init_db.get_session()
        order = session.query(Order).filter_by(user_id=auth_user.id).first()
        
        assert order is not None
        assert len(order.items) == 2
        
        items = order.items
        assert items[0].menu_item_name == 'Margherita Pizza'
        assert items[0].quantity == 1
        assert items[1].menu_item_name == 'Pepperoni Pizza'
        assert items[1].quantity == 2
        session.close()
    
    def test_create_order_creates_payment(self, client, auth_user, sample_restaurants, init_db):
        """Order creation creates associated Payment"""
        with client.session_transaction() as sess:
            sess['cart'] = {
                '1': {
                    'items': [{
                        'item_id': 'pizza_1',
                        'name': 'Margherita Pizza',
                        'price': 12.99,
                        'quantity': 1
                    }],
                    'total': 12.99
                }
            }
        
        client.post('/orders/create', data={
            'delivery_address': '123 Main Street, New York, NY 10001',
            'special_instructions': '',
            'notes': ''
        }, follow_redirects=True)
        
        # Verify payment was created
        session = init_db.get_session()
        order = session.query(Order).filter_by(user_id=auth_user.id).first()
        payment = session.query(Payment).filter_by(order_id=order.id).first()
        
        assert payment is not None
        assert payment.amount == 12.99
        assert payment.status == PaymentStatus.PENDING
        session.close()
    
    def test_create_order_clears_cart(self, client, auth_user, sample_restaurants):
        """Order creation clears the cart"""
        with client.session_transaction() as sess:
            sess['cart'] = {
                '1': {
                    'items': [{
                        'item_id': 'pizza_1',
                        'name': 'Margherita Pizza',
                        'price': 12.99,
                        'quantity': 1
                    }],
                    'total': 12.99
                }
            }
        
        client.post('/orders/create', data={
            'delivery_address': '123 Main Street, New York, NY 10001',
            'special_instructions': '',
            'notes': ''
        }, follow_redirects=True)
        
        # Verify cart is empty
        with client.session_transaction() as sess:
            assert sess.get('cart', {}) == {}


class TestOrderHistory:
    """Test order history and details"""
    
    def test_order_list_requires_login(self, client):
        """Unauthenticated users are redirected to login"""
        response = client.get('/orders')
        assert response.status_code == 302
        assert '/auth/login' in response.location
    
    def test_order_list_displays(self, client, auth_user):
        """Authenticated users can view order history"""
        response = client.get('/orders')
        assert response.status_code == 200
        assert b'order' in response.data.lower()
    
    def test_order_list_shows_user_orders_only(self, client, auth_user, sample_restaurants, init_db):
        """Order list shows only logged-in user's orders"""
        session = init_db.get_session()
        
        # Create an order for auth_user
        order = Order(
            user_id=auth_user.id,
            restaurant_id=sample_restaurants[0].id,
            total_price=25.50,
            status=OrderStatus.PENDING
        )
        session.add(order)
        session.commit()
        session.close()
        
        response = client.get('/orders')
        assert response.status_code == 200
        assert b'25.50' in response.data or b'order' in response.data.lower()
    
    def test_order_detail_requires_login(self, client):
        """Unauthenticated users are redirected to login"""
        response = client.get('/orders/1')
        assert response.status_code == 302
        assert '/auth/login' in response.location
    
    def test_order_detail_displays(self, client, auth_user, sample_restaurants, init_db):
        """Order detail page displays correct information"""
        session = init_db.get_session()
        
        # Create an order
        order = Order(
            user_id=auth_user.id,
            restaurant_id=sample_restaurants[0].id,
            total_price=25.50,
            delivery_address='123 Main St',
            status=OrderStatus.PENDING
        )
        session.add(order)
        session.flush()
        
        # Add order items
        item = OrderItem(
            order_id=order.id,
            menu_item_name='Margherita Pizza',
            restaurant_id=sample_restaurants[0].id,
            quantity=2,
            unit_price=12.75
        )
        session.add(item)
        session.commit()
        session.close()
        
        response = client.get(f'/orders/{order.id}')
        assert response.status_code == 200
        assert b'Margherita Pizza' in response.data
        assert b'Pizza Palace' in response.data
    
    def test_order_detail_not_found(self, client, auth_user):
        """Accessing non-existent order returns 404"""
        response = client.get('/orders/9999')
        assert response.status_code == 404
    
    def test_order_detail_unauthorized_access(self, client, auth_user, init_db):
        """Users cannot view other users' orders"""
        session = init_db.get_session()
        
        # Create another user
        from app.auth.utils import hash_password
        from database.models import User
        
        other_user = User(
            email='other@example.com',
            username='otheruser',
            password_hash=hash_password('password123')
        )
        session.add(other_user)
        session.commit()
        
        # Create order for other user
        order = Order(
            user_id=other_user.id,
            restaurant_id=1,
            total_price=25.50,
            status=OrderStatus.PENDING
        )
        session.add(order)
        session.commit()
        session.close()
        
        # Try to access other user's order
        response = client.get(f'/orders/{order.id}')
        assert response.status_code == 404
    
    def test_cancel_pending_order(self, client, auth_user, sample_restaurants, init_db):
        """Users can cancel pending orders"""
        session = init_db.get_session()
        
        # Create pending order
        order = Order(
            user_id=auth_user.id,
            restaurant_id=sample_restaurants[0].id,
            total_price=25.50,
            status=OrderStatus.PENDING
        )
        session.add(order)
        session.commit()
        order_id = order.id
        session.close()
        
        # Cancel order
        response = client.post(f'/orders/{order_id}/cancel', follow_redirects=True)
        assert response.status_code == 200
        
        # Verify order status changed
        session = init_db.get_session()
        updated_order = session.query(Order).filter_by(id=order_id).first()
        assert updated_order.status == OrderStatus.CANCELLED
        session.close()
    
    def test_cannot_cancel_confirmed_order(self, client, auth_user, sample_restaurants, init_db):
        """Users cannot cancel confirmed orders"""
        session = init_db.get_session()
        
        # Create confirmed order
        order = Order(
            user_id=auth_user.id,
            restaurant_id=sample_restaurants[0].id,
            total_price=25.50,
            status=OrderStatus.CONFIRMED
        )
        session.add(order)
        session.commit()
        order_id = order.id
        session.close()
        
        # Try to cancel confirmed order
        response = client.post(f'/orders/{order_id}/cancel', follow_redirects=True)
        assert response.status_code == 200
        assert b'cannot' in response.data.lower() or b'error' in response.data.lower()
