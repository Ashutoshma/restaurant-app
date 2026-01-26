"""Firestore database connection and initialization"""
import os

class FirestoreDB:
    """Firestore database wrapper - simplified for student implementation"""
    def __init__(self, credentials_path=None):
        """Initialize Firestore connection"""
        # For student level - we'll implement basic structure
        # Firebase connection requires credentials which is optional during development
        self.initialized = False
        try:
            import firebase_admin
            from firebase_admin import credentials, firestore
            
            if not firebase_admin._apps:  # Check if already initialized
                if credentials_path is None:
                    credentials_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
                
                if credentials_path and os.path.exists(credentials_path):
                    creds = credentials.Certificate(credentials_path)
                    firebase_admin.initialize_app(creds)
                    self.db = firestore.client()
                    self.initialized = True
        except Exception as e:
            print(f"Note: Firestore not fully initialized (development mode): {e}")
            self.db = None
    
    def get_restaurants(self):
        """Get all restaurants"""
        if not self.initialized:
            return self._get_mock_restaurants()
        
        try:
            docs = self.db.collection('restaurants').stream()
            restaurants = []
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                restaurants.append(data)
            return restaurants
        except Exception as e:
            print(f"Error fetching restaurants: {e}")
            return self._get_mock_restaurants()
    
    def get_menu_items(self, restaurant_id):
        """Get menu items for a restaurant"""
        if not self.initialized:
            return self._get_mock_menu_items(restaurant_id)
        
        try:
            docs = self.db.collection('menu_items')\
                .where('restaurant_id', '==', restaurant_id)\
                .stream()
            items = []
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                items.append(data)
            return items
        except Exception as e:
            print(f"Error fetching menu items: {e}")
            return self._get_mock_menu_items(restaurant_id)
    
    def add_review(self, restaurant_id, user_id, review_data):
        """Add review to restaurant"""
        if not self.initialized:
            return True  # Mock success
        
        try:
            self.db.collection('reviews').add({
                'restaurant_id': restaurant_id,
                'user_id': user_id,
                'rating': review_data.get('rating'),
                'comment': review_data.get('comment'),
                'created_at': __import__('firebase_admin').firestore.SERVER_TIMESTAMP
            })
            return True
        except Exception as e:
            print(f"Error adding review: {e}")
            return False
    
    def get_reviews(self, restaurant_id):
        """Get reviews for restaurant"""
        if not self.initialized:
            return []
        
        try:
            docs = self.db.collection('reviews')\
                .where('restaurant_id', '==', restaurant_id)\
                .order_by('created_at', direction=__import__('firebase_admin').firestore.Query.DESCENDING)\
                .stream()
            reviews = []
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                reviews.append(data)
            return reviews
        except Exception as e:
            print(f"Error fetching reviews: {e}")
            return []
    
    def _get_mock_restaurants(self):
        """Mock data for development"""
        return [
            {
                'id': 'pizza_palace',
                'name': 'Pizza Palace',
                'description': 'Authentic Italian pizza',
                'image_url': 'https://via.placeholder.com/300x200?text=Pizza+Palace',
                'rating': 4.5,
                'cuisines': ['Italian', 'Pizza'],
                'price_range': '$',
                'delivery_time': '30-45 mins'
            },
            {
                'id': 'burger_haven',
                'name': 'Burger Haven',
                'description': 'Gourmet burgers and fries',
                'image_url': 'https://via.placeholder.com/300x200?text=Burger+Haven',
                'rating': 4.2,
                'cuisines': ['American', 'Burgers'],
                'price_range': '$$',
                'delivery_time': '20-30 mins'
            }
        ]
    
    def _get_mock_menu_items(self, restaurant_id):
        """Mock menu items for development"""
        items = {
            'pizza_palace': [
                {
                    'id': '1',
                    'restaurant_id': 'pizza_palace',
                    'name': 'Margherita Pizza',
                    'description': 'Fresh mozzarella and basil',
                    'price': 12.99,
                    'category': 'Pizza',
                    'image_url': 'https://via.placeholder.com/200x200?text=Margherita'
                },
                {
                    'id': '2',
                    'restaurant_id': 'pizza_palace',
                    'name': 'Pepperoni Pizza',
                    'description': 'Classic pepperoni and cheese',
                    'price': 14.99,
                    'category': 'Pizza',
                    'image_url': 'https://via.placeholder.com/200x200?text=Pepperoni'
                }
            ],
            'burger_haven': [
                {
                    'id': '3',
                    'restaurant_id': 'burger_haven',
                    'name': 'Classic Cheeseburger',
                    'description': 'Juicy burger with cheddar',
                    'price': 9.99,
                    'category': 'Burgers',
                    'image_url': 'https://via.placeholder.com/200x200?text=Cheeseburger'
                }
            ]
        }
        return items.get(restaurant_id, [])
    
    def seed_data(self):
        """Seed initial Firestore data"""
        if not self.initialized:
            print("✓ Firestore data (mock mode - using in-memory data)")
            return
        
        try:
            # Check if data exists
            if self.db.collection('restaurants').document('pizza_palace').get().exists:
                return
            
            # Create restaurants
            restaurants = {
                'pizza_palace': {
                    'name': 'Pizza Palace',
                    'description': 'Authentic Italian pizza',
                    'rating': 4.5,
                    'cuisines': ['Italian', 'Pizza']
                }
            }
            
            batch = self.db.batch()
            for doc_id, data in restaurants.items():
                batch.set(self.db.collection('restaurants').document(doc_id), data)
            batch.commit()
            
            print("✓ Firestore data seeded")
        
        except Exception as e:
            print(f"✗ Error seeding Firestore: {e}")

# Global Firestore instance
firestore_db = FirestoreDB()

def init_firestore():
    """Initialize Firestore"""
    firestore_db.seed_data()

if __name__ == '__main__':
    firestore_db.seed_data()
    print("Firestore initialized successfully!")
