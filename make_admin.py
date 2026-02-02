#!/usr/bin/env python
"""
Script to promote a user to admin.

Usage:
    python make_admin.py <email>

Example:
    python make_admin.py test@example.com
"""
import sys
from database.postgres import SessionLocal
from database.models import User

def make_admin(email):
    """Promote user to admin by email"""
    session = SessionLocal()
    try:
        user = session.query(User).filter_by(email=email).first()
        
        if not user:
            print(f"❌ User with email '{email}' not found")
            return False
        
        if user.is_admin:
            print(f"⚠️  User '{user.username}' is already an admin")
            return True
        
        user.is_admin = True
        session.commit()
        
        print(f"✅ User '{user.username}' ({email}) is now an admin!")
        return True
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        session.rollback()
        return False
    
    finally:
        session.close()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python make_admin.py <email>")
        print("Example: python make_admin.py test@example.com")
        sys.exit(1)
    
    email = sys.argv[1]
    success = make_admin(email)
    sys.exit(0 if success else 1)
