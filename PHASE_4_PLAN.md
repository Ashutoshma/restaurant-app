# Phase 4: Admin & Reviews - Basic Implementation Plan

**Status**: Starting  
**Target Duration**: 1-2 days  
**Estimated Commits**: 3-4  
**Estimated Tests**: 8-10 new tests  

---

## Overview

Phase 4 adds essential features for a student project without payment:
1. Order status management (admin workflow)
2. Simple notification logging (console/file)
3. Restaurant reviews and ratings (Firestore)
4. Basic admin dashboard

---

## Feature 1: Order Status Management

**Routes**: `app/routes/admin.py`

- **GET /admin/orders** - Admin dashboard
  - List all orders (not just user's)
  - Filter by status
  - Show order details, customer, items, total
  - Quick status update buttons

- **POST /admin/orders/<id>/status** - Update order status
  - Change status: PENDING → CONFIRMED → PREPARING → READY → DELIVERED
  - Admin-only access
  - Log status changes

**Templates**:
- `app/templates/admin/orders.html` - Admin order dashboard
- `app/templates/admin/order_detail.html` - Full order details

**Database**: No new tables, uses existing Order model

**Tests** (3-4 tests):
- ✓ Admin can view all orders
- ✓ Admin can update order status
- ✓ Non-admin cannot access admin routes
- ✓ Status transitions work correctly

---

## Feature 2: Simple Notifications

**File**: `app/services/notifications.py`

- **notify_order_confirmation()** - When order created
- **notify_status_change()** - When status updated
- **notify_delivery()** - When marked delivered

**Implementation**:
- Log to console in development
- Log to file in production
- Format: timestamp, order_id, user_email, message
- Ready for email integration later

**No new routes** - Called internally from order routes

**Tests** (2 tests):
- ✓ Notification creates log file
- ✓ Notification contains correct info

---

## Feature 3: Reviews & Ratings

**Routes**: `app/routes/reviews.py`

- **POST /restaurants/<id>/review** - Submit review
  - Logged-in users only
  - Rating 1-5 stars
  - Text review (max 500 chars)
  - Stores in Firestore

- **GET /restaurants/<id>/reviews** - View reviews
  - Show all reviews for restaurant
  - Display rating, text, author, date
  - Average rating displayed

**Forms**: `app/reviews/forms.py`
- **ReviewForm** - Rating and text fields

**Templates**:
- Review form embedded in restaurant detail
- Review list on restaurant detail page

**Firestore**: `reviews` collection
```json
{
  "restaurant_id": "pizza_palace",
  "user_id": 1,
  "username": "john_doe",
  "rating": 5,
  "text": "Great pizza!",
  "created_at": timestamp
}
```

**Tests** (3-4 tests):
- ✓ User can submit review
- ✓ Reviews display on restaurant page
- ✓ Rating calculation works
- ✓ Only logged-in users can review

---

## Feature 4: Admin User Role (Basic)

**Models**: Add to User model
```python
class User:
    is_admin = Column(Boolean, default=False)
```

**Routes**: Protection
- Check `current_user.is_admin` before admin routes
- Return 403 Forbidden if not admin
- Or redirect to home

**Fixture**: Create admin user in test seeds
```python
admin_user = User(
    email='admin@example.com',
    username='admin',
    is_admin=True
)
```

---

## Implementation Details

### Admin Dashboard Features
- Display all orders (not filtered by user)
- Show order status with badges
- Quick inline status update buttons
- Show customer name and email
- Show order total and items count
- Click to view full details

### Notification System
```python
# Usage in orders.py
from app.services.notifications import notify_order_confirmation

@bp.route('/create', methods=['POST'])
def create():
    # ... create order ...
    notify_order_confirmation(order, current_user)
    # ... redirect ...
```

### Review System
- Each restaurant can have multiple reviews
- Show average rating on restaurant list/detail
- User can only review once per restaurant (optional)
- Reviews sorted by newest first
- Display username, rating, text, date

---

## File Structure

```
app/
├── routes/
│   ├── auth.py
│   ├── restaurants.py
│   ├── menu.py
│   ├── cart.py
│   ├── orders.py
│   └── admin.py              (NEW)
├── reviews/                   (NEW)
│   ├── __init__.py
│   └── forms.py
├── services/                  (NEW)
│   ├── __init__.py
│   └── notifications.py
├── templates/
│   ├── admin/                 (NEW)
│   │   ├── orders.html
│   │   └── order_detail.html
│   ├── reviews/               (NEW)
│   │   └── review_form.html
│   └── ...
└── ...

tests/
├── test_admin.py              (NEW)
└── test_reviews.py            (NEW)
```

---

## Database Changes

### User Model Update
```python
class User(Base, UserMixin):
    # ... existing fields ...
    is_admin = Column(Boolean, default=False)  # NEW
```

### Firestore Updates
```
reviews/
├── review_1 { restaurant_id, user_id, username, rating, text, created_at }
├── review_2 { ... }
└── ...
```

---

## Routes Summary

### Admin Routes (NEW)
```
GET  /admin/orders              - Admin dashboard
POST /admin/orders/<id>/status  - Update status
GET  /admin/orders/<id>         - Order detail
```

### Review Routes (NEW)
```
POST /restaurants/<id>/review   - Submit review
GET  /restaurants/<id>/reviews  - View reviews
```

---

## Testing Strategy

### Admin Tests
- Admin can access dashboard
- Non-admin gets 403
- Status updates work
- Status change notifications sent

### Review Tests
- User can submit review
- Review appears on restaurant page
- Rating calculation correct
- Duplicate review prevention (optional)

### Notification Tests
- Log file created
- Log contains order info
- Log has correct timestamp

---

## Git Commits

1. **Commit 1**: Admin order management
   - Admin routes
   - Admin templates
   - Admin tests

2. **Commit 2**: Reviews and ratings
   - Review forms
   - Review routes
   - Review templates
   - Review tests

3. **Commit 3**: Notifications system
   - Notification service
   - Integration with orders
   - Notification tests

---

## Student Project Level

This is perfect for a student project because:
✅ Shows understanding of admin patterns
✅ Demonstrates Firestore usage (reviews)
✅ Adds real feature (reviews are visible to users)
✅ Simple notification stubs (not real emails)
✅ Basic role-based access (admin flag)
✅ No external service integrations needed
✅ More test coverage
✅ Shows workflow completeness

---

## Success Criteria

✓ Admin can manage order status
✓ Reviews appear on restaurant pages
✓ Notifications logged to file
✓ Admin-only access enforced
✓ All new tests passing
✓ Code is documented
✓ 3-4 clean git commits

---

## Estimated Time

- Admin orders: 2-3 hours
- Reviews system: 2-3 hours
- Notifications: 1-2 hours
- Testing: 2-3 hours
- Documentation: 1 hour

**Total**: ~10 hours of work (1-2 days)
