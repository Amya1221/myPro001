from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.users import UserManager

# Initialize user manager
user_manager = UserManager()

# Define Blueprint
alerts_bp = Blueprint('alerts', __name__)

@alerts_bp.route('/add', methods=['POST'])
@jwt_required()
def add_alert():
    user_manager = UserManager()
    """
    Adds a stock alert for the logged-in user.
    """
    data = request.json
    print(data)
    stock_name = data.get('stock_name')
    trigger_price = data.get('trigger_price')
    to_trade = data.get('to_trade')
    condition = data.get('condition')

    if not stock_name or trigger_price is None or not to_trade or not condition:
        return jsonify({"status": "error", "message": "Invalid input data"}), 400

    current_user = get_jwt_identity()
    user = user_manager.get_user_by_username(current_user)

    if not user:
        return jsonify({"status": "error", "message": "User not found"}), 404

    user.add_stock_alert(
        stock_name=stock_name,
        trigger_price=float(trigger_price),
        to_trade=to_trade.upper(),
        condition=condition
    )
    user_manager.save_users()

    return jsonify({"status": "success", "message": "Alert added successfully!"}), 201


@alerts_bp.route('/list', methods=['GET'])
@jwt_required()
def list_alerts():
    current_user = get_jwt_identity()
    user = user_manager.get_user_by_username(current_user)

    if not user:
        return jsonify({"status": "error", "message": "User not found"}), 404
    alerts_dict = [alert.to_dict() for alert in user.stock_alerts]
    return jsonify({"status": "success", "alerts": alerts_dict}), 200

@alerts_bp.route('/delete/<int:index>', methods=['DELETE'])
@jwt_required()
def delete_alert(index):
    current_user = get_jwt_identity()
    user = user_manager.get_user_by_username(current_user)

    if not user or index < 0 or index >= len(user.stock_alerts):
        return jsonify({"status": "error", "message": "Invalid index"}), 400

    user.stock_alerts.pop(index)
    user_manager.save_users()

    return jsonify({"status": "success", "message": "Alert removed successfully"}), 200
