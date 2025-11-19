from typing import Optional

class User:
    """User class for authentication"""
    
    def __init__(self, username: str, password: str, email: str = ""):
        self.username = username
        self.password = password  # Note: In production, use hashed passwords
        self.email = email
    
    def __str__(self):
        return f"User({self.username})"
    
    def __repr__(self):
        return f"User(username='{self.username}', email='{self.email}')"


class UserManager:
    """Manage user authentication and creation"""
    
    def __init__(self):
        self.users: dict = {}
    
    def create_user(self, username: str, password: str, email: str = "") -> User:
        """Create a new user"""
        if username in self.users:
            raise ValueError(f"User '{username}' already exists")
        
        user = User(username, password, email)
        self.users[username] = user
        return user
    
    def get_user(self, username: str) -> Optional[User]:
        """Get user by username"""
        return self.users.get(username, None)
    
    def delete_user(self, username: str) -> bool:
        """Delete a user"""
        if username in self.users:
            del self.users[username]
            return True
        return False
    
    def authenticate(self, username: str, password: str) -> bool:
        """Authenticate user credentials"""
        user = self.get_user(username)
        if user and user.password == password:
            return True
        return False
    
    def list_users(self) -> list:
        """List all users"""
        return list(self.users.values())