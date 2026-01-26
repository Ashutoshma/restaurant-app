"""Tests for admin features"""
import pytest
from database.models import Order, OrderStatus, User
from app.auth.utils import hash_password


class TestAdminAccess:
    """Test admin route protection"""
    
    def test_admin_orders_requires_login(self, client):
        """Unauthenticated users are redirected"""
        response = client.get('/admin/orders')
        assert response.status_code == 302
        assert '/auth/login' in response.location
    
    def test_regular_user_cannot_access_admin(self, client, auth_user):
        """Regular users cannot access admin dashboard"""
        response = client.get('/admin/orders', follow_redirects=False)
        assert response.status_code == 403 or b'Admin' in response.data or b'Home' in response.data
    
    def test_admin_user_can_access_dashboard(self, client, init_db):
        """Admin users can access admin dashboard"""
        session = init_db.get_session()
        
        # Create admin user
        admin = User(
            email='admin@example.com',
            username='admin',
            password_hash=hash_password('adminpass123'),
            is_admin=True
        )
        session.add(admin)
        session.commit()
        session.close()
        
        # Log in as admin
        client.post('/auth/login', data={
            'email': 'admin@example.com',
            'password': 'adminpass123'
        }, follow_redirects=True)
        
        # Access admin dashboard
        response = client.get('/admin/orders')
        assert response.status_code == 200
        assert b'Admin Dashboard' in response.data or b'Orders' in response.data


class TestOrderStatusManagement:
    """Test order status updates"""
    
    def test_admin_can_update_order_status(self, client, init_db, auth_user, sample_restaurants):
        """Admin can update order status"""
        session = init_db.get_session()
        
        # Create order
        order = Order(
            user_id=auth_user.id,
            restaurant_id=sample_restaurants[0].id,
            status=OrderStatus.PENDING,
            total_price=25.00
        )
        session.add(order)
        session.commit()
        order_id = order.id
        session.close()
        
        # Make user admin
        session = init_db.get_session()
        auth_user = session.query(User).filter_by(id=auth_user.id).first()
        auth_user.is_admin = True
        session.commit()
        session.close()
        
        # Log out and log back in to refresh session
        client.get('/auth/logout')
        client.post('/auth/login', data={
            'email': 'test@example.com',
            'password': 'testpass123'
        }, follow_redirects=True)
        
        # Update status
        response = client.post(f'/admin/orders/{order_id}/status', json={
            'status': 'confirmed'
        })
        
        assert response.status_code == 200
        
        # Verify status changed
        session = init_db.get_session()
        updated_order = session.query(Order).filter_by(id=order_id).first()
        assert updated_order.status == OrderStatus.CONFIRMED
        session.close()
    
    def test_invalid_status_transition(self, client, init_db, auth_user, sample_restaurants):
        """Invalid status transitions are rejected"""
        session = init_db.get_session()
        
        # Create delivered order
        order = Order(
            user_id=auth_user.id,
            restaurant_id=sample_restaurants[0].id,
            status=OrderStatus.DELIVERED,
            total_price=25.00
        )
        session.add(order)
        session.commit()
        order_id = order.id
        session.close()
        
        # Make user admin and log in
        session = init_db.get_session()
        auth_user = session.query(User).filter_by(id=auth_user.id).first()
        auth_user.is_admin = True
        session.commit()
        session.close()
        
        client.get('/auth/logout')
        client.post('/auth/login', data={
            'email': 'test@example.com',
            'password': 'testpass123'
        }, follow_redirects=True)
        
        # Try invalid transition
        response = client.post(f'/admin/orders/{order_id}/status', json={
            'status': 'pending'
        })
        
        assert response.status_code == 400


class TestAdminStats:
    """Test admin statistics"""
    
    def test_admin_can_view_stats(self, client, init_db, auth_user):
        """Admin can view order statistics"""
        # Make user admin
        session = init_db.get_session()
        auth_user = session.query(User).filter_by(id=auth_user.id).first()
        auth_user.is_admin = True
        session.commit()
        session.close()
        
        # Log out and log back in
        client.get('/auth/logout')
        client.post('/auth/login', data={
            'email': 'test@example.com',
            'password': 'testpass123'
        }, follow_redirects=True)
        
        # Access stats
        response = client.get('/admin/stats')
        assert response.status_code == 200
        
        data = response.get_json()
        assert 'total_orders' in data
        assert 'total_revenue' in data
