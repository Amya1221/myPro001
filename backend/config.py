from datetime import timedelta


class Config:
    # JWT configuration
    JWT_SECRET_KEY = 'your_secret_key'  # Replace with a secure secret
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=30)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

    # CORS configuration
    CORS_HEADERS = 'Content-Type'

    # User data file path
    USER_DATA_FILE = 'data/users.json'  # Path to the user data file
