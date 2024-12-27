from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.users import UserManager

# Initialize user_manager
user_manager = UserManager()

# Define Admin Blueprint
admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/authenticate', methods=['GET', 'POST'])
@jwt_required()  # Ensure only authenticated users can access this route
def admin_authenticate_user():
    """
    Handles admin operations:
    - GET: Returns pending authentication requests.
    - POST: Authenticates a specific user.
    """
    user_manager = UserManager()
    admin_username = get_jwt_identity()  # Get the admin username from the JWT
    print(admin_username)
    # Check if the current user is an admin
    admin = user_manager.get_user_by_username(admin_username)
    print(admin.is_active)
    # if not admin or admin.role != "admin" or not admin.is_active:
    if not admin or admin.role != "admin":

        return jsonify({"status": "error", "message": "Unauthorized access. Admin rights required."}), 403

    if request.method == 'POST':
        # Handle user authentication request
        data = request.json
        user_to_authenticate = data.get("username")
        if not user_to_authenticate:
            return jsonify({"status": "error", "message": "The 'username' to authenticate is required."}), 400

        # Authenticate the specified user
        success = user_manager.authenticate_user(user_to_authenticate, admin_username)
        if success:
            return jsonify({"status": "success", "message": f"User '{user_to_authenticate}' has been authenticated."}), 200
        else:
            return jsonify({"status": "error", "message": f"Failed to authenticate user '{user_to_authenticate}'."}), 400

    else:  # request.method == 'GET'
        # Fetch all pending authentication requests
        pending_users = [
            {"username": user.username, "email": user.email, "phone": user.phone}
            for user in user_manager.users
            if (not getattr(user, "is_active", False) or user.role=="guest")  # Users without `is_authenticated` set to True
        ]

        if pending_users:
            return jsonify({"status": "success", "pending_requests": pending_users}), 200
        else:
            return jsonify({"status": "success", "message": "No pending authentication requests."}), 200


@admin_bp.route('/assign-admin', methods=['POST'])
@jwt_required()
def assign_admin():
    """
    Assign admin role to a user. Admins only.
    """
    user_manager = UserManager()
    admin_username = get_jwt_identity()
    admin = user_manager.get_user_by_username(admin_username)

    if not admin or admin.role != "admin" or not admin.is_active:
        return jsonify({"status": "error", "message": "Unauthorized access. Admin rights required."}), 403

    data = request.json
    username_to_promote = data.get("username")

    if not username_to_promote:
        return jsonify({"status": "error", "message": "Username is required."}), 400

    user_to_promote = user_manager.get_user_by_username(username_to_promote)

    if not user_to_promote:
        return jsonify({"status": "error", "message": f"User '{username_to_promote}' not found."}), 404

    if user_to_promote.role == "admin":
        return jsonify({"status": "error", "message": f"User '{username_to_promote}' is already an admin."}), 400

    # Assign admin role
    user_to_promote.role = "admin"
    user_manager.save_users()
    return jsonify({"status": "success", "message": f"User '{username_to_promote}' has been promoted to admin."}), 200
@admin_bp.route('/get-all-users', methods=['GET'])
@jwt_required()
def get_all_users():
    """
    Assign admin role to a user. Admins only.
    """
    user_manager = UserManager()
    admin_username = get_jwt_identity()
    admin = user_manager.get_user_by_username(admin_username)
    if not admin or admin.role != "admin":
        return jsonify({"status": "error", "message": "Unauthorized access. Admin rights required."}), 403
    all_users = [
        {
            "username": user.username,
            "email": user.email,
            "phone": user.phone,
            "role": user.role,
            "is_active": getattr(user, "is_active", False)  # Handle cases where 'is_active' might not be set
        }
        for user in user_manager.users
    ]

    # Return all user data
    return jsonify({"status": "success", "users": all_users}), 200