from flask import Blueprint, request, jsonify, render_template, g
from utils.screening import screen_data
import traceback
from flask_cors import CORS

bp = Blueprint('screen', __name__)
CORS(bp, resources={r"/screen": {"origins": "*"}})

@bp.route('/screen', methods=['GET', 'POST'])
def screen():
    """
    Endpoint for screening stocks based on user-defined conditions.
    """
    scriplist = g.scriplist
    scripdata = g.scripdata
    fundamentals = g.fundamentals
    ohlcv_data = g.ohlcv_data
    fundamentals_fund = g.fundamentals_fund

    try:
        if request.method == 'GET':
            # Get the columns from any one stock's OHLCV data
            sample_symbol = next(iter(ohlcv_data['daily']))
            columns = ohlcv_data['daily'][sample_symbol].columns.tolist()
            return jsonify({"status": "success", "columns": columns}), 200

        elif request.method == 'POST':
            conditions = request.get_json()
            if not conditions:
                return jsonify({"status": "error", "message": "No conditions provided."}), 400
            # Perform screening
            print(conditions)
            screened_stocks = screen_data(conditions, scriplist, ohlcv_data, scripdata, fundamentals, fundamentals_fund)
            print('screened stocks:', screened_stocks)
            return jsonify({"status": "success", "screened_stocks": screened_stocks}), 200

    except Exception as e:
        print('Exception raised:', e)
        return jsonify({"status": "error", "message": str(e)}), 500
