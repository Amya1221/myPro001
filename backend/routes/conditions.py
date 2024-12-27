from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_cors import CORS
from models.users import UserManager

# Blueprint for conditions
conditions_bp = Blueprint('conditions', __name__)
CORS(conditions_bp, resources={r"/conditions/*": {"origins": "*"}})

# User manager instance
user_manager = UserManager()

@conditions_bp.route('/conditions', methods=['GET', 'POST'])
@jwt_required()
def conditions():
    user_manager = UserManager()
    """
    Endpoint to handle saving and retrieving user-defined conditions.
    """
    # Get the current logged-in user's identity
    current_user = get_jwt_identity()

    # Find the user in the user manager
    user = user_manager.get_user_by_username(current_user)
    if not user:
        return jsonify({"status": "error", "message": "User not found."}), 404

    if request.method == "POST":
        # Save user-defined conditions
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "No data provided."}), 400

        # Extract and validate the fields
        name = data.get("name")
        method = data.get("method")
        conditions = data.get("conditions", [])

        if not name:
            return jsonify({"status": "error", "message": "Condition name is required."}), 400
        if not method:
            return jsonify({"status": "error", "message": "Condition method is required."}), 400
        if not isinstance(conditions, list) or not conditions:
            return jsonify({"status": "error", "message": "Conditions must be a non-empty list."}), 400

        # Add the condition
        try:
            user.add_condition(name, method, conditions, user_manager)
            return jsonify({"status": "success", "message": f"Condition '{name}' saved successfully."}), 201
        except Exception as e:
            return jsonify({"status": "error", "message": f"An error occurred: {str(e)}"}), 500

    elif request.method == "GET":
        # Retrieve saved conditions
        try:
            return jsonify({"status": "success", "saved_conditions": user.saved_conditions}), 200
        except Exception as e:
            return jsonify({"status": "error", "message": f"An error occurred: {str(e)}"}), 500

@conditions_bp.route('/conditions/<condition_name>', methods=['GET'])
@jwt_required()
def get_condition(condition_name):
    """
    Endpoint to retrieve a specific condition by name.
    """
    # Get the current logged-in user's identity
    current_user = get_jwt_identity()

    # Find the user in the user manager
    user = user_manager.get_user_by_username(current_user)
    if not user:
        return jsonify({"status": "error", "message": "User not found."}), 404

    # Retrieve the specific condition
    condition = user.saved_conditions.get(condition_name)
    if not condition:
        return jsonify({"status": "error", "message": "Condition not found."}), 404

    return jsonify({"status": "success", "conditions": condition}), 200
