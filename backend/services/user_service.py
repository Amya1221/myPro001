import json
from models.users import User, UserManager

class UserService:
    def __init__(self, user_manager: UserManager):
        self.user_manager = user_manager

    def create_user(self, username, password, email, phone):
        user = self.user_manager.add_user(username, password, email, phone)
        if user:
            print(f"User {username} created successfully.")
        return user

    def get_user(self, username):
        return self.user_manager.find_user_by_username(username)

    def add_watchlist(self, username, watchlist_name, goal):
        user = self.get_user(username)
        if user:
            user.create_watchlist(watchlist_name, goal)
            self.user_manager.save_users()
            return f"Watchlist '{watchlist_name}' added for user {username}."
        return f"User {username} not found."

    def delete_watchlist(self, username, watchlist_name):
        user = self.get_user(username)
        if user:
            user.delete_watchlist(watchlist_name)
            self.user_manager.save_users()
            return f"Watchlist '{watchlist_name}' deleted for user {username}."
        return f"User {username} not found."

    def add_condition(self, username, name, method, conditions):
        user = self.get_user(username)
        if user:
            user.add_condition(name, method, conditions)
            self.user_manager.save_users()
            return f"Condition '{name}' added for user {username}."
        return f"User {username} not found."

    def delete_condition(self, username, name):
        user = self.get_user(username)
        if user:
            user.delete_condition(name)
            self.user_manager.save_users()
            return f"Condition '{name}' deleted for user {username}."
        return f"User {username} not found."
