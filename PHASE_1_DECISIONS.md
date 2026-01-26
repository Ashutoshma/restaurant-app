# Phase 1: Database Design Decisions

## PostgreSQL Schema Design Rationale

### Tables Created

#### 1. Users Table
- **Fields:** id, email, username, password_hash, first_name, last_name, phone, address, city, postal_code, created_at, updated_at, is_active
- **Why?** Stores user authentication and profile data with unique email/username
- **Relationships:** 1 user → many orders

#### 2. Restaurants Table
- **Fields:** id, name, description, phone, city, address, created_at, updated_at
- **Why?** Stores restaurant information. Detailed info (images, cuisines) in Firestore
- **Relationships:** 1 restaurant → many orders

#### 3. Orders Table (Main Transaction Record)
- **Fields:** id, user_id, restaurant_id, status, total_price, notes, delivery_address, created_at, updated_at
- **Why PostgreSQL?**
  - Financial data (total_price) requires ACID compliance
  - Complex relationships with users, restaurants, items, payments
  - Need for analytics/reporting queries
- **Status enum:** PENDING → CONFIRMED → PREPARING → READY → DELIVERED/CANCELLED

#### 4. OrderItems Table (Order Details)
- **Fields:** id, order_id, menu_item_name, restaurant_id, quantity, unit_price, special_instructions, created_at
- **Why separate table?**
  - One order can have many items
  - Stores unit_price at time of order (menu prices change, but order price is historical)
  - Allows detailed order analytics

#### 5. Payments Table (Payment Tracking)
- **Fields:** id, order_id, amount, status, payment_method, transaction_id, created_at, updated_at
- **Why separate?**
  - 1:1 relationship with orders
  - Separates payment logic from orders
  - Financial auditing and compliance
  - Handles payment failures separately

### Why These Decisions?

**ACID Compliance:** Orders + payments are financial transactions and must be atomic (all-or-nothing)

**Example Transaction:**
```
INSERT INTO orders (user_id, restaurant_id, total_price) → Returns order_id
INSERT INTO order_items (order_id, menu_item_name, quantity, unit_price) → 2 items
INSERT INTO payments (order_id, amount, status) → Payment record
ALL SUCCEED OR ALL FAIL (atomic transaction)
```

**Relationships:** SQLAlchemy handles these automatically:
- User.orders → list of all user's orders
- Order.items → all items in an order
- Order.user → which user placed the order
- Order.restaurant → which restaurant
- Order.payment → payment details

---

## Firestore Data Model

### Collections Created

#### 1. Restaurants Collection
```
Document: pizza_palace
{
  name: "Pizza Palace",
  description: "Authentic Italian pizza",
  image_url: "...",
  rating: 4.5,
  cuisines: ["Italian", "Pizza"],
  price_range: "$",
  delivery_time: "30-45 mins"
}
```
**Why NoSQL?** Flexible schema - each restaurant can have different attributes

#### 2. Menu Items Collection
```
Document: (auto-generated)
{
  restaurant_id: "pizza_palace",
  name: "Margherita Pizza",
  description: "Fresh mozzarella and basil",
  price: 12.99,
  category: "Pizza",
  image_url: "...",
  available: true
}
```
**Why NoSQL?** Menu items vary greatly between restaurants, prices change frequently

#### 3. Reviews Collection
```
Document: (auto-generated)
{
  restaurant_id: "pizza_palace",
  user_id: 1,
  rating: 5,
  comment: "Excellent pizza!",
  created_at: Timestamp
}
```
**Why NoSQL?** Reviews are flexible documents, no complex relationships needed

---

## Design Decision: What Goes Where?

### PostgreSQL (Structured, Relational, ACID)
```
✓ Users         → Authentication, identity
✓ Orders        → Financial transaction, must be atomic
✓ OrderItems    → Line items, relationships
✓ Payments      → Financial records, auditing
✓ Restaurants   → Reference data with relationships to orders
```

### Firestore (Flexible, Document-based, Real-time)
```
✓ Restaurants (detailed info) → Images, cuisines, varying attributes
✓ MenuItems                   → Flexible schemas, frequent changes
✓ Reviews                     → User-generated content, flexible structure
```

---

## SQLAlchemy Models Implementation

### Key Features Implemented

1. **Auto-incrementing IDs:** `Column(Integer, primary_key=True)`
2. **Relationships:** SQLAlchemy automatically manages foreign keys and joins
3. **Enums:** OrderStatus and PaymentStatus enforce valid values
4. **Timestamps:** `created_at` and `updated_at` auto-populate
5. **Cascading Deletes:** Delete user → automatically delete their orders
6. **String Representations:** `__repr__` methods for debugging

### Testing Strategy

Created 7 unit tests:
- ✓ Table creation verification
- ✓ User creation and retrieval
- ✓ Restaurant creation
- ✓ Complex transaction (order with multiple items)
- ✓ Enum validation
- ✓ Model string representations

---

## Database Initialization

### PostgreSQL Flow
```
1. Create all tables (Base.metadata.create_all)
2. Create 3 sample restaurants
3. Ready for orders
```

### Firestore Flow
```
1. Initialize Firebase connection (optional, has mock fallback)
2. Load sample restaurants and menu items
3. Ready for reviews
```

### For Development
- Uses SQLite in-memory database for testing
- Mock Firestore data for development without credentials
- Easy to switch to real PostgreSQL with `DATABASE_URL` environment variable

---

## Files Created in Phase 1

| File | Purpose |
|------|---------|
| `database/models.py` | 5 SQLAlchemy models (User, Restaurant, Order, OrderItem, Payment) |
| `database/postgres.py` | PostgreSQL connection and initialization |
| `database/firestore.py` | Firestore connection with mock fallback |
| `database/__init__.py` | Package initialization |
| `database/init_db.py` | Database setup script |
| `tests/test_database.py` | 7 unit tests (all passing) |

---

## Summary: Phase 1 ✓

**Status:** COMPLETE
- ✓ 5 database tables designed and implemented
- ✓ 3 Firestore collections defined
- ✓ SQLAlchemy models with relationships
- ✓ 7 unit tests (100% passing)
- ✓ Database initialization script ready
- ✓ Documented design decisions
