from flask import Blueprint, request, jsonify,g
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from models.users import UserManager
from flask_cors import CORS
# Initialize user_manager
user_manager = UserManager()

# Define Blueprint
bp = Blueprint('auth', __name__)
CORS(bp)
@bp.route('/register', methods=['POST'])
def register():
    data = request.json
    username, email, phone = data.get('username'), data.get('email'), data.get('phone')
    password = data.get('password', 'password')

    if user_manager.is_username_taken(username):
        return jsonify({"status": "error", "message": f"Username '{username}' already exists."}), 400

    hashed_password = generate_password_hash(password)
    new_user = user_manager.add_user(username, hashed_password, email, phone)

    if new_user:
        new_user.role = "guest"  # Default role
        user_manager.save_users()
        return jsonify(new_user.to_dict()), 201
    else:
        return jsonify({"status": "error", "message": "Failed to register user."}), 500
@bp.route('/register-as-admin', methods=['POST'])
def register_as_admin():
    data = request.json
    username, email, phone = data.get('username'), data.get('email'), data.get('phone')
    password = data.get('password', 'password')

    if user_manager.is_username_taken(username):
        return jsonify({"status": "error", "message": f"Username '{username}' already exists."}), 400

    hashed_password = generate_password_hash(password)
    new_user = user_manager.add_user(username, hashed_password, email, phone)

    if new_user:
        new_user.role = "admin"  # Default role
        user_manager.save_users()
        return jsonify(new_user.to_dict()), 201
    else:
        return jsonify({"status": "error", "message": "Failed to register user."}), 500

@bp.route('/login', methods=['POST'])
def login():
    ohlcv_data = g.ohlcv_data
    data = request.json
    print(data)
    username, password = data.get('username'), data.get('password')
    print('username:',username)
    print('password:',password)
    user = user_manager.get_user_by_username(username)
    print('hashed password:',generate_password_hash(password))
    if user and check_password_hash(user.password, password):
        access_token = create_access_token(identity=username)
        print(f"User '{username}' logged in successfully.")
        user.is_active=True
        # Start monitoring for the authenticated user
        ohlcv_data = {}  # Replace with actual logic to load or fetch OHLCV data
        user.start_monitoring(ohlcv_data)

        return jsonify(access_token=access_token, username=username), 200

    return jsonify({"msg": "Bad username or password"}), 401
@bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    current_user = get_jwt_identity()
    user = user_manager.get_user_by_username(current_user)

    if user:
        user.stop_monitoring()  # Stop monitoring for the user
        print(f"User '{current_user}' logged out and monitoring stopped.")
        return jsonify({"msg": "Logged out successfully"}), 200

    return jsonify({"msg": "User not found"}), 404

@bp.route('/check-token', methods=['GET'])
@jwt_required(optional=True)  # Allows requests without a valid token
def check_token():
    print('checking token')
    current_user = get_jwt_identity()
    print(current_user)
    if current_user:
        return jsonify({"status": "active", "username": current_user}), 200
    else:
        return jsonify({"status": "expired"}), 401



