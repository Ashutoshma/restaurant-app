# Design Decisions - Restaurant Ordering App

## Technology Stack

### Backend Framework
**Decision:** Flask 2.3.0
**Rationale:**
- Lightweight and beginner-friendly for undergraduate coursework
- Flexible - doesn't impose structure (vs Django)
- Perfect for learning core web concepts
- Easy to integrate with Google Cloud
- Smaller learning curve compared to FastAPI

### SQL Database
**Decision:** PostgreSQL (Cloud SQL)
**Rationale:**
- ACID compliance - critical for financial transactions (orders, payments)
- Strong data relationships - users → orders → items → payments
- Good at handling complex queries with JOINs
- Free tier available on Google Cloud

### NoSQL Database
**Decision:** Firebase Firestore
**Rationale:**
- Flexible schema - menu items have varying attributes
- Real-time synchronization - menus update instantly
- Built-in Google Cloud integration
- Easy to add new fields (reviews, ratings, images as nested objects)

### Frontend Framework
**Decision:** HTML/CSS/Bootstrap (No SPA framework)
**Rationale:**
- Simple, straightforward
- No complex build process
- Focus on backend learning
- Faster development

### Deployment
**Decision:** Google App Engine (Python 3.9)
**Rationale:**
- Direct alignment with coursework requirement
- Managed service - no server management
- Auto-scaling
- Free tier eligible

## Architecture Pattern
**Decision:** MVC (Model-View-Controller) with Service Layer

## Next Decision: Phase 1 (Database Design)
To be documented after implementation begins.
