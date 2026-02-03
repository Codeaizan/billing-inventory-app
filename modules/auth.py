import bcrypt
from typing import Optional, Tuple
from datetime import datetime
from database.db_manager import db
from utils.logger import logger
from utils.validators import validate_username, validate_password

class AuthManager:
    """Handles user authentication"""
    
    def __init__(self):
        self.current_user = None
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        except Exception as e:
            logger.error(f"Error verifying password: {e}")
            return False
    
    def login(self, username: str, password: str) -> Tuple[bool, str, Optional[dict]]:
        """
        Authenticate user
        Returns: (success, message, user_data)
        """
        # Validate inputs
        valid, msg = validate_username(username)
        if not valid:
            return False, msg, None
        
        valid, msg = validate_password(password)
        if not valid:
            return False, msg, None
        
        try:
            # Get user from database
            with db.get_connection() as conn:
                cursor = conn.execute(
                    "SELECT * FROM users WHERE username = ?",
                    (username,)
                )
                user = cursor.fetchone()
                
                if not user:
                    logger.warning(f"Login failed: User not found - {username}")
                    return False, "Invalid username or password", None
                
                # Verify password against stored hash
                if self.verify_password(password, user['password_hash']):
                    # Update last login
                    conn.execute(
                        "UPDATE users SET last_login = ? WHERE id = ?",
                        (datetime.now(), user['id'])
                    )
                    conn.commit()
                    
                    self.current_user = dict(user)
                    logger.info(f"User logged in successfully: {username}")
                    return True, "Login successful", self.current_user
                else:
                    logger.warning(f"Login failed: Invalid password for user - {username}")
                    return False, "Invalid username or password", None
                    
        except Exception as e:
            logger.error(f"Login error: {e}")
            return False, "Login error occurred", None
    
    def logout(self):
        """Logout current user"""
        if self.current_user:
            logger.info(f"User logged out: {self.current_user['username']}")
            self.current_user = None
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated"""
        return self.current_user is not None
    
    def get_current_user(self) -> Optional[dict]:
        """Get current logged in user"""
        return self.current_user
    
    def get_current_user_id(self) -> Optional[int]:
        """Get current user ID"""
        return self.current_user['id'] if self.current_user else None
    
    def change_password(self, old_password: str, new_password: str) -> Tuple[bool, str]:
        """Change password for current user"""
        if not self.is_authenticated():
            return False, "Not authenticated"
        
        # Validate new password
        valid, msg = validate_password(new_password)
        if not valid:
            return False, msg
        
        # Verify old password
        if not self.verify_password(old_password, self.current_user['password_hash']):
            return False, "Current password is incorrect"
        
        try:
            # Hash new password
            new_hash = self.hash_password(new_password)
            
            # Update in database
            with db.get_connection() as conn:
                conn.execute(
                    "UPDATE users SET password_hash = ? WHERE id = ?",
                    (new_hash, self.current_user['id'])
                )
                conn.commit()
            
            # Update current user
            self.current_user['password_hash'] = new_hash
            
            logger.info(f"Password changed for user: {self.current_user['username']}")
            return True, "Password changed successfully"
            
        except Exception as e:
            logger.error(f"Error changing password: {e}")
            return False, "Error changing password"

# Create global auth manager instance
auth_manager = AuthManager()