"""Unit tests for database connections and models"""
import pytest
import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.postgres import PostgresDB
from database.models import User, Restaurant, Order, OrderItem, Payment, OrderStatus

class TestPostgresDatabaseConnection:
    """Test PostgreSQL connection with in-memory SQLite"""
    
    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """Setup and teardown for each test"""
        # Setup - use SQLite in-memory
        self.db = PostgresDB('sqlite:///:memory:')
        self.db.create_tables()
        yield
        # Teardown
        self.db.drop_tables()
    
    def test_create_tables(self):
        """Test that tables are created successfully"""
        session = self.db.get_session()
        # Try to query a table
        users = session.query(User).all()
        assert isinstance(users, list)
        assert len(users) == 0
        session.close()
    
    def test_create_user(self):
        """Test creating a user"""
        session = self.db.get_session()
        
        user = User(
            email='test@example.com',
            username='testuser',
            password_hash='hashed_password',
            first_name='Test',
            last_name='User',
            city='New York'
        )
        
        session.add(user)
        session.commit()
        
        # Retrieve and verify
        retrieved_user = session.query(User).filter_by(email='test@example.com').first()
        assert retrieved_user is not None
        assert retrieved_user.username == 'testuser'
        assert retrieved_user.first_name == 'Test'
        
        session.close()
    
    def test_create_restaurant(self):
        """Test creating a restaurant"""
        session = self.db.get_session()
        
        restaurant = Restaurant(
            name='Test Restaurant',
            description='A test restaurant',
            city='New York'
        )
        
        session.add(restaurant)
        session.commit()
        
        # Retrieve and verify
        retrieved = session.query(Restaurant).filter_by(name='Test Restaurant').first()
        assert retrieved is not None
        assert retrieved.city == 'New York'
        
        session.close()
    
    def test_create_order_with_items(self):
        """Test creating order with items"""
        session = self.db.get_session()
        
        try:
            # Create user
            user = User(
                email='user@test.com',
                username='user1',
                password_hash='hash'
            )
            session.add(user)
            session.flush()
            
            # Create restaurant
            restaurant = Restaurant(name='Test Restaurant')
            session.add(restaurant)
            session.flush()
            
            # Create order
            order = Order(
                user_id=user.id,
                restaurant_id=restaurant.id,
                total_price=50.00,
                status=OrderStatus.PENDING
            )
            session.add(order)
            session.flush()
            
            # Create order items
            item1 = OrderItem(
                order_id=order.id,
                menu_item_name='Pizza',
                restaurant_id=restaurant.id,
                quantity=1,
                unit_price=15.00
            )
            item2 = OrderItem(
                order_id=order.id,
                menu_item_name='Salad',
                restaurant_id=restaurant.id,
                quantity=2,
                unit_price=8.50
            )
            
            session.add_all([item1, item2])
            session.commit()
            
            # Verify relationships
            retrieved_order = session.query(Order).first()
            assert len(retrieved_order.items) == 2
            assert retrieved_order.total_price == 50.00
        
        finally:
            session.close()
    
    def test_user_repr(self):
        """Test User __repr__ method"""
        user = User(email='test@test.com', username='testuser', password_hash='hash')
        assert repr(user) == '<User testuser>'
    
    def test_restaurant_repr(self):
        """Test Restaurant __repr__ method"""
        restaurant = Restaurant(name='Test Rest')
        assert repr(restaurant) == '<Restaurant Test Rest>'
    
    def test_order_status_enum(self):
        """Test order status enum"""
        session = self.db.get_session()
        
        user = User(email='user@test.com', username='user1', password_hash='hash')
        restaurant = Restaurant(name='Restaurant')
        session.add_all([user, restaurant])
        session.flush()
        
        order = Order(
            user_id=user.id,
            restaurant_id=restaurant.id,
            total_price=10.00,
            status=OrderStatus.PREPARING
        )
        session.add(order)
        session.commit()
        
        retrieved = session.query(Order).first()
        assert retrieved.status == OrderStatus.PREPARING
        
        session.close()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
