# Phase 3: Ordering System - Implementation Plan

**Status**: In Progress  
**Target Duration**: 2-3 days  
**Estimated Commits**: 5-6  
**Estimated Tests**: 10-12  

---

## Overview

Phase 3 implements the core ordering functionality, allowing users to:
1. Browse and filter restaurants
2. View menus from Firestore
3. Manage shopping cart
4. Create and submit orders
5. Track order history and status

---

## Implementation Breakdown

### 1. Restaurant Browsing Feature (Commit 1)
**Routes**: `app/routes/restaurants.py`
- **GET /restaurants** - List all restaurants with filtering
  - Filter by city
  - Filter by cuisine
  - Search by name
  - Returns JSON for API + HTML for web
- **GET /restaurants/<id>** - View restaurant details
  - Restaurant info from PostgreSQL
  - Aggregate stats (rating, order count)

**Templates**:
- `app/templates/restaurants/list.html` - Browse all restaurants
- `app/templates/restaurants/detail.html` - Restaurant detail page

**Database Queries**:
- Query restaurants from PostgreSQL
- Count orders per restaurant
- Calculate average rating

**Tests** (3 tests):
- ✓ Restaurant list page loads
- ✓ Restaurant list filters by city
- ✓ Restaurant detail page loads

---

### 2. Menu & Items Display (Commit 2)
**Routes**: `app/routes/menu.py`
- **GET /restaurants/<id>/menu** - View restaurant menu
  - Fetch menu items from Firestore
  - Display organized by category
  - Show prices and descriptions

**Templates**:
- `app/templates/menu/items.html` - Menu items display

**Firestore Integration**:
- Read from `menu_items` collection
- Filter by restaurant_id
- Group by category

**Tests** (2 tests):
- ✓ Menu items load from Firestore
- ✓ Menu items display correctly

---

### 3. Shopping Cart (Commit 3)
**Routes**: `app/routes/cart.py`
- **GET /cart** - View cart contents
- **POST /cart/add** - Add item to cart (AJAX)
- **POST /cart/remove** - Remove item from cart
- **POST /cart/update** - Update item quantity

**Session-based Cart**:
- Store cart in Flask session
- Structure: `{restaurant_id: {items: [{id, qty, price}], total: X}}`
- Support only one restaurant per order

**Templates**:
- `app/templates/cart.html` - Shopping cart page
- AJAX methods for add/remove/update

**Tests** (3 tests):
- ✓ Add item to cart
- ✓ Remove item from cart
- ✓ Calculate cart total correctly

---

### 4. Order Creation (Commit 4)
**Routes**: `app/routes/orders.py` (Create)
- **POST /orders/create** - Submit order
  - Validate cart not empty
  - Validate items still available
  - Create Order + OrderItems in PostgreSQL
  - Clear cart
  - Redirect to order confirmation

**Forms**: `app/orders/forms.py`
- **OrderForm** - Delivery address, special instructions, notes

**Database Operations**:
- Insert Order
- Insert OrderItems
- Create Payment record (PENDING)

**Tests** (2 tests):
- ✓ Order creation with valid data
- ✓ Order creation fails with empty cart

---

### 5. Order History & Status (Commit 5)
**Routes**: `app/routes/orders.py` (Retrieve)
- **GET /orders** - List user's orders
  - Order details from PostgreSQL
  - Current status
  - Order date and total
- **GET /orders/<id>** - Order detail page
  - Order items
  - Restaurant info
  - Payment status
  - Delivery address

**Templates**:
- `app/templates/orders/list.html` - Order history
- `app/templates/orders/detail.html` - Order details

**Tests** (2 tests):
- ✓ Order history shows user's orders only
- ✓ Order detail page displays correctly

---

### 6. Order Status Updates (Commit 6 - Optional)
**Routes**: 
- Admin/worker routes to update order status
- Webhook endpoint for payment updates

---

## File Structure

```
app/
├── routes/
│   ├── restaurants.py      (NEW)
│   ├── menu.py             (NEW)
│   ├── cart.py             (NEW)
│   └── orders.py           (NEW)
├── templates/
│   ├── restaurants/
│   │   ├── list.html       (NEW)
│   │   └── detail.html     (NEW)
│   ├── menu/
│   │   └── items.html      (NEW)
│   ├── orders/
│   │   ├── list.html       (NEW)
│   │   └── detail.html     (NEW)
│   ├── cart.html           (NEW)
│   └── ...
├── orders/                 (NEW)
│   ├── __init__.py
│   └── forms.py            (NEW)
└── static/
    ├── css/
    │   └── style.css       (UPDATE - add cart styles)
    └── js/
        └── cart.js         (NEW - AJAX cart operations)

tests/
├── test_restaurants.py     (NEW)
├── test_menu.py            (NEW)
├── test_cart.py            (NEW)
└── test_orders.py          (NEW)
```

---

## Key Implementation Patterns

### 1. Restaurant Filtering
```python
query = session.query(Restaurant)
if city:
    query = query.filter_by(city=city)
if search:
    query = query.filter(Restaurant.name.ilike(f'%{search}%'))
```

### 2. Firestore Integration
```python
from database.firestore import firestore_db
items = firestore_db.get_menu_items(restaurant_id)
```

### 3. Session-based Cart
```python
# Add to cart
if 'cart' not in session:
    session['cart'] = {}
session['cart'][restaurant_id] = {
    'items': [...],
    'total': calculate_total()
}
session.modified = True
```

### 4. Order Creation with Transaction
```python
order = Order(
    user_id=current_user.id,
    restaurant_id=restaurant_id,
    total_price=total,
    status=OrderStatus.PENDING
)
session.add(order)
session.flush()  # Get order ID

for item in cart_items:
    order_item = OrderItem(
        order_id=order.id,
        menu_item_name=item['name'],
        quantity=item['quantity'],
        unit_price=item['price']
    )
    session.add(order_item)

payment = Payment(
    order_id=order.id,
    amount=total,
    status=PaymentStatus.PENDING
)
session.add(payment)
session.commit()
```

---

## Testing Approach

### Test Structure
```python
def test_restaurant_list_filters_by_city(client, auth_user):
    response = client.get('/restaurants?city=New%20York')
    assert response.status_code == 200
    assert 'Pizza Palace' in response.data.decode()

def test_add_item_to_cart(client, auth_user):
    response = client.post('/cart/add', json={
        'restaurant_id': 1,
        'item_id': 'item_1',
        'name': 'Pizza',
        'price': 12.99,
        'quantity': 1
    })
    assert response.status_code == 200
    assert response.json['success']
```

### Test Fixtures Needed
- `auth_user` - Authenticated user logged in
- `sample_restaurants` - Pre-populated restaurants
- `sample_menu_items` - Mock Firestore menu items
- `client` - Flask test client

---

## Database Seeding

### Restaurant Data (PostgreSQL)
- Pizza Palace (New York)
- Burger Haven (New York)
- Sushi Paradise (Los Angeles)

### Menu Items (Firestore Mock)
```json
{
  "id": "item_1",
  "restaurant_id": "pizza_palace",
  "name": "Margherita Pizza",
  "price": 12.99,
  "category": "Pizza",
  "description": "Fresh mozzarella and basil"
}
```

---

## Security Considerations

1. **Cart Validation**: Verify items belong to selected restaurant
2. **User Authorization**: Orders only accessible to order owner
3. **Price Validation**: Compare cart prices with current menu prices
4. **Inventory**: Could add stock checks (future enhancement)
5. **CSRF Protection**: All POST routes protected via Flask-WTF

---

## Code Quality Standards

- All functions documented with docstrings
- Comments explaining complex logic
- Student-level implementation - clear and readable
- Form validation on both client and server side
- Error handling with appropriate flash messages
- Type hints where helpful for clarity
- Consistent naming conventions

---

## Git Commit Strategy

1. **Commit 1**: Restaurant browsing and filtering
2. **Commit 2**: Menu display from Firestore
3. **Commit 3**: Shopping cart functionality
4. **Commit 4**: Order creation and submission
5. **Commit 5**: Order history and details
6. **Commit 6** (Optional): Order status updates and admin features

Each commit includes:
- Route implementation
- Templates
- Tests (2-3 per feature)
- Database seeding if needed
- Documentation updates

---

## Success Criteria

✓ All 5 main features implemented  
✓ 10-12 unit tests all passing  
✓ Uses both PostgreSQL and Firestore  
✓ Cart persists in session  
✓ Orders properly stored in database  
✓ Code is clean and documented  
✓ 5-6 meaningful git commits  

---

## Next Phase Preview (Phase 4)

Phase 4 will add:
- Payment processing (Stripe integration)
- Admin dashboard for restaurants
- Order status notifications
- Email confirmations
