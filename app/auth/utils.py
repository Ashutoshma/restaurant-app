"""Password hashing and verification utilities using bcrypt"""
import bcrypt


def hash_password(password: str) -> str:
    """
    Hash a plaintext password using bcrypt.
    
    Args:
        password: Plaintext password string
        
    Returns:
        Hashed password (bcrypt hash)
    """
    salt = bcrypt.gensalt(rounds=12)  # 12 rounds provides good security/performance balance
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def verify_password(password: str, password_hash: str) -> bool:
    """
    Verify a plaintext password against a bcrypt hash.
    
    Args:
        password: Plaintext password to verify
        password_hash: Bcrypt hash to check against
        
    Returns:
        True if password matches, False otherwise
    """
    try:
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    except (ValueError, TypeError):
        # Handle cases where hash is invalid
        return False
