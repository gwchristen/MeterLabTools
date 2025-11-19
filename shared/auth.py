# shared/auth.py

class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password  # In practice, use hashed passwords

    def __str__(self):
        return f"User({self.username})"


class UserManager:
    def __init__(self):
        self.users = {}

    def create_user(self, username, password):
        if username in self.users:
            raise ValueError("User already exists")
        self.users[username] = User(username, password)
        return self.users[username]

    def get_user(self, username):
        return self.users.get(username, None)

    def delete_user(self, username):
        if username in self.users:
            del self.users[username]
        else:
            raise ValueError("User not found")

    def authenticate(self, username, password):
        user = self.get_user(username)
        if user and user.password == password:
            return True
        return False

# Example usage
if __name__ == "__main__":
    user_manager = UserManager()
    # Create a new user
    user_manager.create_user("test_user", "password123")
    # Authenticate user
    print(user_manager.authenticate("test_user", "password123"))  # Should return True
