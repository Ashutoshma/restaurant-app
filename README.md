# Restaurant Ordering App

A cloud-based restaurant ordering application built with Flask, PostgreSQL, and Firebase Firestore on Google Cloud Platform.

## Project Overview

This is a coursework project for the Systems Development unit. The application demonstrates:
- Multi-database architecture (SQL + NoSQL)
- Cloud security and authentication
- RESTful APIs and Cloud Functions
- Cloud deployment on Google App Engine

## Features

### Core Features
- User registration and login with bcrypt hashing
- Browse restaurants and menu items
- Place orders with multiple items
- View order history
- Leave and view reviews
- Real-time menu updates

### Security Features
- Secure password hashing (bcrypt)
- CSRF protection on forms
- Session-based authentication
- Secure cookies (HTTPOnly, Secure flags)

## Technology Stack

| Component | Technology |
|-----------|-----------|
| Backend | Flask 2.3.0 (Python) |
| SQL Database | PostgreSQL (Cloud SQL) |
| NoSQL Database | Firebase Firestore |
| Authentication | bcrypt + Flask-Login |
| Frontend | HTML/CSS/Bootstrap |
| Deployment | Google App Engine |

## Project Structure

```
restaurant-ordering-app/
├── app/                      # Flask application
│   ├── routes/              # API endpoints
│   ├── services/            # Business logic
│   ├── templates/           # HTML templates
│   └── static/              # CSS, JavaScript
├── database/                # Database models
├── tests/                   # Unit and integration tests
├── cloud_functions/         # Serverless functions
├── config.py               # Configuration
├── app.py                  # Application factory
└── requirements.txt        # Python dependencies
```

## Getting Started

### Prerequisites
- Python 3.9+
- PostgreSQL 12+
- Google Cloud Project

### Local Development

1. **Clone repository**
```bash
git clone <repo-url>
cd restaurant-ordering-app
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Setup environment**
```bash
cp .env.example .env
# Edit .env with your credentials
```

5. **Run application**
```bash
flask run
```

## Development Phases

- **Phase 0:** Project Setup ✓
- **Phase 1:** Database Design (in progress)
- **Phase 2:** Authentication & Security
- **Phase 3:** Core Features (CRUD)
- **Phase 4:** APIs & Cloud Functions
- **Phase 5:** Testing & Documentation
- **Phase 6:** Deployment
- **Phase 7:** Evaluation & Presentation

## Git Commits Strategy

We follow conventional commits:
- `feat:` New feature
- `fix:` Bug fix
- `test:` Tests
- `docs:` Documentation
- `config:` Configuration
