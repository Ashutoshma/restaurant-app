# Restaurant Ordering App - Deployment Guide

## Quick Start for Deployment

### Step 1: Prerequisites
- PostgreSQL 12+ installed and running
- Python 3.8+
- pip package manager

### Step 2: Setup Environment

```bash
# Clone/download the repository
cd restaurant-ordering-app

# Install dependencies
pip install -r requirements.txt

# Set environment variables (optional)
export FLASK_ENV=production
export DATABASE_URL=postgresql://user:password@localhost:5432/restaurant_app
```

### Step 3: Initialize Database

Run the initialization script to create tables and populate with restaurants & menus:

```bash
python database/initialize.py
```

This will:
- ✓ Create all database tables in PostgreSQL
- ✓ Add 6 restaurants to the database
- ✓ Add 42 menu items (7 items per restaurant)
- ✓ Setup Firestore integration (if credentials available)

### Step 4: Run the Application

**Development:**
```bash
python app.py
```

**Production (with Gunicorn):**
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

Application will be available at `http://localhost:5000`

---

## Database Configuration

### PostgreSQL Setup

1. **Create Database:**
```bash
psql -U postgres
CREATE DATABASE restaurant_app;
```

2. **Update Connection String:**

Edit `config.py` and set:
```python
SQLALCHEMY_DATABASE_URI = 'postgresql://username:password@localhost:5432/restaurant_app'
```

Or use environment variable:
```bash
export DATABASE_URL=postgresql://username:password@localhost:5432/restaurant_app
```

### Pre-populated Data

The initialization script adds:

#### Restaurants (6 total):
- **Pizza Palace** - New York - Authentic Italian pizza with wood-fired oven
- **Burger Haven** - New York - Gourmet burgers and crispy fries
- **Sushi Paradise** - Los Angeles - Fresh sushi and Japanese cuisine
- **Taco Fiesta** - Los Angeles - Authentic Mexican street food and tacos
- **Dragon Wok** - San Francisco - Chinese cuisine with traditional recipes
- **The Curry House** - San Francisco - Authentic Indian cuisine and curries

#### Menu Items (42 total - 7 per restaurant):
Each restaurant has 7 menu items with:
- Name
- Description
- Price
- Category
- Firestore integration

---

## Optional: Firestore Integration

If you want to enable real Firestore integration:

1. **Get Google Cloud Credentials:**
   - Create a Firebase project
   - Download service account JSON

2. **Set Environment Variable:**
```bash
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
```

3. **Re-run Initialization:**
```bash
python database/initialize.py
```

---

## Features Included

### ✅ Authentication & Security
- User registration with email/username validation
- bcrypt password hashing (12 rounds)
- CSRF protection on forms
- Session-based login
- HTTPOnly secure cookies

### ✅ Core Features
- Browse 6 restaurants
- View 42 menu items (7 per restaurant)
- Add items to cart
- Create and track orders
- Submit reviews and ratings
- Admin dashboard for order management

### ✅ Database
- PostgreSQL with SQLAlchemy ORM
- Firestore integration for menus and reviews
- 5 database models (User, Restaurant, Order, OrderItem, Payment)
- Full relationships and constraints

---

## Database Schema

### Users Table
```sql
id, email, username, password_hash, first_name, last_name, 
phone, address, city, postal_code, created_at, updated_at, 
is_active, is_admin
```

### Restaurants Table
```sql
id, name, description, phone, city, address, created_at, updated_at
```

### Orders Table
```sql
id, user_id, restaurant_id, total_price, status, created_at, updated_at
```

### OrderItems Table
```sql
id, order_id, menu_item_name, quantity, price, category
```

### Payments Table
```sql
id, order_id, amount, status, created_at, updated_at
```

---

## Testing

### Run All Tests
```bash
python -m pytest tests/ -v
```

Expected: 90+ tests passing

### Manual Testing
1. Visit `http://localhost:5000/auth/register` - Create account
2. Visit `http://localhost:5000/auth/login` - Login
3. Visit `http://localhost:5000/restaurants` - Browse 6 restaurants
4. Click on restaurant - View 7 menu items
5. Add items to cart and checkout

---

## Configuration Files

### config.py
Contains environment-specific settings:
- Database URL
- Secret key
- Session configuration
- CSRF protection

### requirements.txt
All Python dependencies with pinned versions

### .env (optional)
For local development:
```
FLASK_ENV=development
DATABASE_URL=postgresql://postgres:password@localhost:5432/restaurant_app
SECRET_KEY=your-secret-key-here
```

---

## Deployment Checklist

- [ ] PostgreSQL installed and running
- [ ] Database created (`restaurant_app`)
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Initialization script run (`python database/initialize.py`)
- [ ] Configuration updated (database URL, secret key)
- [ ] Tests passing (`pytest tests/`)
- [ ] App starts without errors (`python app.py`)
- [ ] Restaurants visible at `/restaurants`
- [ ] Can register and login
- [ ] Can add items to cart and checkout

---

## Troubleshooting

### Database Connection Error
```
Error: could not translate host name "localhost" to address
```
**Solution:** Ensure PostgreSQL is running: `brew services start postgresql`

### Port Already in Use
```
Address already in use
```
**Solution:** Change port in `app.py` or kill existing process: `lsof -i :5000`

### Missing Restaurants
```
No restaurants displayed on /restaurants page
```
**Solution:** Run initialization: `python database/initialize.py`

### CSRF Token Errors
```
CSRF token missing
```
**Solution:** Ensure you're using the same session cookie for form submission

---

## Production Deployment

### Using Gunicorn
```bash
gunicorn -w 4 -b 0.0.0.0:5000 --timeout 120 app:app
```

### Using Docker
```bash
docker build -t restaurant-app .
docker run -p 5000:5000 restaurant-app
```

### Environment Variables for Production
```bash
export FLASK_ENV=production
export DATABASE_URL=postgresql://prod_user:prod_password@prod_host:5432/restaurant_app
export SECRET_KEY=your-secure-secret-key-here
```

---

## Support

For issues or questions:
1. Check logs: `tail -f /tmp/app.log`
2. Review error messages in console
3. Check database connection: `psql -U postgres restaurant_app`
4. Verify restaurants: `SELECT * FROM restaurants;`
5. Verify menus in Firestore (if enabled)

---

**Version**: 1.0  
**Last Updated**: January 31, 2026  
**Status**: Production Ready
