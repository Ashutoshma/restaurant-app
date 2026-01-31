"""Comprehensive seed data for restaurants and menus"""

RESTAURANTS = [
    {
        'name': 'Pizza Palace',
        'description': 'Authentic Italian pizza with wood-fired oven',
        'city': 'New York',
        'address': '123 Main St',
        'phone': '(212) 555-0101'
    },
    {
        'name': 'Burger Haven',
        'description': 'Gourmet burgers and crispy fries',
        'city': 'New York',
        'address': '456 Oak Ave',
        'phone': '(212) 555-0102'
    },
    {
        'name': 'Sushi Paradise',
        'description': 'Fresh sushi and Japanese cuisine',
        'city': 'Los Angeles',
        'address': '789 Elm St',
        'phone': '(213) 555-0103'
    },
    {
        'name': 'Taco Fiesta',
        'description': 'Authentic Mexican street food and tacos',
        'city': 'Los Angeles',
        'address': '321 Maple Dr',
        'phone': '(213) 555-0104'
    },
    {
        'name': 'Dragon Wok',
        'description': 'Chinese cuisine with traditional recipes',
        'city': 'San Francisco',
        'address': '654 Pine Rd',
        'phone': '(415) 555-0105'
    },
    {
        'name': 'The Curry House',
        'description': 'Authentic Indian cuisine and curries',
        'city': 'San Francisco',
        'address': '987 Cedar Ln',
        'phone': '(415) 555-0106'
    }
]

# Menus mapped by restaurant name (lowercase with underscores for Firestore)
MENUS = {
    'pizza_palace': [
        {'name': 'Margherita Pizza', 'category': 'Pizza', 'price': 12.99, 'description': 'Fresh mozzarella, basil, tomato'},
        {'name': 'Pepperoni Pizza', 'category': 'Pizza', 'price': 14.99, 'description': 'Classic pepperoni with cheese'},
        {'name': 'Veggie Supreme', 'category': 'Pizza', 'price': 13.99, 'description': 'Bell peppers, onions, mushrooms, olives'},
        {'name': 'Meat Lovers', 'category': 'Pizza', 'price': 16.99, 'description': 'Pepperoni, sausage, bacon, ham'},
        {'name': 'Garlic Bread', 'category': 'Appetizer', 'price': 4.99, 'description': 'Crispy garlic bread'},
        {'name': 'Caesar Salad', 'category': 'Salad', 'price': 8.99, 'description': 'Romaine, parmesan, croutons'},
        {'name': 'Italian Pasta', 'category': 'Pasta', 'price': 10.99, 'description': 'Spaghetti with marinara sauce'},
    ],
    'burger_haven': [
        {'name': 'Classic Burger', 'category': 'Burger', 'price': 9.99, 'description': 'Beef patty, lettuce, tomato, onion'},
        {'name': 'Deluxe Cheeseburger', 'category': 'Burger', 'price': 11.99, 'description': 'Double cheese, bacon, special sauce'},
        {'name': 'Mushroom Swiss Burger', 'category': 'Burger', 'price': 12.99, 'description': 'Swiss cheese, sautéed mushrooms'},
        {'name': 'Crispy Fries', 'category': 'Side', 'price': 3.99, 'description': 'Golden crispy fries with salt'},
        {'name': 'Sweet Potato Fries', 'category': 'Side', 'price': 4.99, 'description': 'Crispy sweet potato fries'},
        {'name': 'Onion Rings', 'category': 'Side', 'price': 4.49, 'description': 'Golden fried onion rings'},
        {'name': 'Milkshake', 'category': 'Beverage', 'price': 5.99, 'description': 'Vanilla, chocolate, or strawberry'},
    ],
    'sushi_paradise': [
        {'name': 'California Roll', 'category': 'Roll', 'price': 7.99, 'description': 'Crab, avocado, cucumber'},
        {'name': 'Spicy Tuna Roll', 'category': 'Roll', 'price': 8.99, 'description': 'Spicy tuna with jalapeño'},
        {'name': 'Dragon Roll', 'category': 'Roll', 'price': 12.99, 'description': 'Shrimp tempura, eel, avocado'},
        {'name': 'Salmon Sashimi', 'category': 'Sashimi', 'price': 10.99, 'description': '6 pieces of fresh salmon'},
        {'name': 'Tuna Sashimi', 'category': 'Sashimi', 'price': 11.99, 'description': '6 pieces of fresh tuna'},
        {'name': 'Miso Soup', 'category': 'Soup', 'price': 3.99, 'description': 'Traditional miso soup'},
        {'name': 'Edamame', 'category': 'Appetizer', 'price': 4.99, 'description': 'Steamed edamame with salt'},
    ],
    'taco_fiesta': [
        {'name': 'Carne Asada Tacos', 'category': 'Tacos', 'price': 8.99, 'description': '3 grilled beef tacos'},
        {'name': 'Pollo Asado Tacos', 'category': 'Tacos', 'price': 7.99, 'description': '3 grilled chicken tacos'},
        {'name': 'Fish Tacos', 'category': 'Tacos', 'price': 9.99, 'description': '3 crispy fish tacos'},
        {'name': 'Burrito Supreme', 'category': 'Burrito', 'price': 10.99, 'description': 'Beef, beans, rice, cheese, salsa'},
        {'name': 'Enchiladas', 'category': 'Main', 'price': 9.99, 'description': '3 cheese enchiladas with sauce'},
        {'name': 'Nachos', 'category': 'Appetizer', 'price': 6.99, 'description': 'Tortilla chips, cheese, jalapeños'},
        {'name': 'Churros', 'category': 'Dessert', 'price': 4.99, 'description': 'Fried dough with cinnamon sugar'},
    ],
    'dragon_wok': [
        {'name': 'General Tso Chicken', 'category': 'Chicken', 'price': 10.99, 'description': 'Spicy chicken with vegetables'},
        {'name': 'Kung Pao Chicken', 'category': 'Chicken', 'price': 10.99, 'description': 'Chicken with peanuts and peppers'},
        {'name': 'Beef and Broccoli', 'category': 'Beef', 'price': 11.99, 'description': 'Tender beef with broccoli'},
        {'name': 'Lo Mein Noodles', 'category': 'Noodles', 'price': 8.99, 'description': 'Stir-fried noodles with vegetables'},
        {'name': 'Fried Rice', 'category': 'Rice', 'price': 7.99, 'description': 'Egg fried rice with vegetables'},
        {'name': 'Spring Rolls', 'category': 'Appetizer', 'price': 5.99, 'description': '4 crispy spring rolls'},
        {'name': 'Hot and Sour Soup', 'category': 'Soup', 'price': 4.99, 'description': 'Spicy and tangy soup'},
    ],
    'the_curry_house': [
        {'name': 'Chicken Tikka Masala', 'category': 'Chicken', 'price': 12.99, 'description': 'Creamy tomato sauce with chicken'},
        {'name': 'Butter Chicken', 'category': 'Chicken', 'price': 12.99, 'description': 'Chicken in rich butter sauce'},
        {'name': 'Lamb Vindaloo', 'category': 'Lamb', 'price': 13.99, 'description': 'Spicy lamb curry'},
        {'name': 'Palak Paneer', 'category': 'Vegetarian', 'price': 10.99, 'description': 'Spinach with cottage cheese'},
        {'name': 'Chana Masala', 'category': 'Vegetarian', 'price': 9.99, 'description': 'Spiced chickpeas'},
        {'name': 'Garlic Naan', 'category': 'Bread', 'price': 2.99, 'description': 'Soft flatbread with garlic'},
        {'name': 'Basmati Rice', 'category': 'Rice', 'price': 3.99, 'description': 'Fragrant basmati rice'},
    ]
}

def get_restaurants():
    """Get all restaurants"""
    return RESTAURANTS

def get_menu_for_restaurant(restaurant_name):
    """Get menu items for a restaurant"""
    firestore_id = restaurant_name.lower().replace(' ', '_')
    return MENUS.get(firestore_id, [])

def get_all_menus():
    """Get all menus"""
    return MENUS
