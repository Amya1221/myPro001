from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime

SECRET_KEY = "your_secret_key_here"  # Replace with a secure key

class AuthService:
    def __init__(self, user_manager):
        self.user_manager = user_manager

    def login(self, username, password):
        user = self.user_manager.find_user_by_username(username)
        if user and check_password_hash(user.password, password):
            token = self.generate_token(user)
            return {"message": "Login successful", "token": token, "username": user.username}
        return {"message": "Invalid username or password"}

    def register(self, username, password, email, phone):
        if self.user_manager.find_user_by_username(username):
            return {"message": "Username already exists"}
        hashed_password = generate_password_hash(password)
        user = self.user_manager.add_user(username, hashed_password, email, phone)
        return {"message": "Registration successful", "user": user.username}

    def generate_token(self, user):
        payload = {
            "username": user.username,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)  # Token expires in 1 hour
        }
        return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    def verify_token(self, token):
        try:
            decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            return {"username": decoded["username"]}
        except jwt.ExpiredSignatureError:
            return {"error": "Token expired"}
        except jwt.InvalidTokenError:
            return {"error": "Invalid token"}
