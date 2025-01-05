from flask import Blueprint, jsonify, request,g
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_cors import CORS
from datetime import datetime
import math
from models.users import UserManager
from models.stock import Stock
import pandas as pd
watchlists_bp = Blueprint('watchlists', __name__)
user_manager=UserManager()
def get_fund_data(symbol):
    # nifty500_tickers = pd.read_csv('D:/codings/fundamental_sec.csv')
    # nifty500_tickers.dropna(inplace=True)
    print(symbol)
    s=symbol+".NS"
    scriplist = g.scriplist
    scripdata = g.scripdata
    fundamentals = g.fundamentals
    ohlcv_data = g.ohlcv_data
    fundamentals_fund=g.fundamentals_fund
    try:
        total_fund = fundamentals_fund[fundamentals_fund['Symbol'] == s]['total'].iloc[0]
    except Exception as err:
        total_fund = 100
    # print('total for ', symbol, ':', total_fund)
    # print('reliance funda:', reliance_fund if not reliance_fund.empty else 100)
    nifty500_tickers=scripdata
    try:
        sector = nifty500_tickers.loc[nifty500_tickers["symbol"] == symbol, "sector"].values[0]
        mcap = nifty500_tickers.loc[nifty500_tickers["symbol"] == symbol, "mcap"].values[0]
    except Exception as err:
        sector="INDIA"
        mcap=100
    try:
        # print('current price for symbol', symbol, ' is ')
        cmp1=ohlcv_data['daily'][symbol+".NS"]['Close'].iloc[-1]
        cmp = cmp1 if not math.isnan(cmp1) else 100
        prev_cmp1=ohlcv_data['daily'][symbol+".NS"]['Close'].iloc[-2]
        prev_cmp=prev_cmp1 if not math.isnan(prev_cmp1) else 100
        # change=(ohlcv_data['daily'][symbol+".NS"]['Close'].iloc[-1]-ohlcv_data['daily'][symbol+".NS"]['Close'].iloc[-2])*100/(ohlcv_data['daily'][symbol+".NS"]['Close'].iloc[-1])
        # print(cmp)
        change=(cmp-prev_cmp)*100/prev_cmp
    except Exception as err:
        # print(err)
        cmp=100
        change=0
    return {"total_value": total_fund, "sector": sector, "mcap": mcap,"cmp":cmp,"todays_change":change}

@watchlists_bp.route('/watchlists', methods=['GET', 'POST', 'DELETE', 'PUT'])
@jwt_required()
def watchlists():
    user_manager = UserManager()
    """
    Route for managing user-specific watchlists.
    """
    current_user = get_jwt_identity()
    user = next((u for u in user_manager.users if u.username == current_user), None)
    if not user:
        return jsonify({"status": "error", "message": "User not found."}), 404

    if request.method == 'POST':
        # Create a new watchlist
        data = request.get_json()
        name = data.get("name")
        goal = data.get("goal")

        if name and goal:
            user.create_watchlist(name, goal,user_manager)
            user_manager.save_users()
            return jsonify({"status": "success", "message": f"Watchlist '{name}' created."}), 201
        else:
            return jsonify({"status": "error", "message": "Name and goal are required fields."}), 400

    elif request.method == 'DELETE':
        # Delete an existing watchlist
        data = request.get_json()
        name = data.get("name")

        if name:
            if name in user.watchlists:
                user.delete_watchlist(name)
                user_manager.save_users()
                return jsonify({"status": "success", "message": f"Watchlist '{name}' deleted."}), 200
            else:
                return jsonify({"status": "error", "message": f"Watchlist '{name}' not found."}), 404
        else:
            return jsonify({"status": "error", "message": "Watchlist name is required."}), 400

    elif request.method == 'PUT':
        # Update an existing watchlist by adding or removing a stock
        data = request.get_json()
        name = data.get("name")
        action = data.get("action")
        stock_data = data.get("stock")

        watchlist = user.watchlists.get(name)
        if not watchlist:
            return jsonify({"status": "error", "message": f"Watchlist '{name}' not found."}), 404

        if action == "add" and stock_data:
            try:
                stock = Stock(
                    name=stock_data.get("name", "Unknown"),
                    date=datetime.fromisoformat(stock_data.get("date", "2024-01-01")),
                    close=stock_data.get("close", 100),
                    cmp=100,
                    open=stock_data.get("open", 100),
                    high=stock_data.get("high", 100),
                    low=stock_data.get("low", 100),
                    volume=stock_data.get("volume", 100),
                )
                watchlist.add_stock(stock)
                user_manager.save_users()
                return jsonify({"status": "success", "message": f"Stock '{stock.name}' added to watchlist '{name}'."}), 200
            except KeyError as e:
                return jsonify({"status": "error", "message": f"Missing stock data: {e}"}), 400
            except ValueError:
                return jsonify({"status": "error", "message": "Invalid date format for stock."}), 400

        elif action == "remove" and stock_data:
            stock_name = stock_data.get("name")
            stock_date = stock_data.get("date")

            if stock_name and stock_date:
                try:
                    date_obj = datetime.fromisoformat(stock_date)
                    watchlist.remove_stock(stock_name, date_obj)
                    user_manager.save_users()
                    return jsonify({"status": "success", "message": f"Stock '{stock_name}' removed from watchlist '{name}'."}), 200
                except ValueError:
                    return jsonify({"status": "error", "message": "Invalid date format for stock."}), 400
            else:
                return jsonify({"status": "error", "message": "Stock name and date are required for removal."}), 400
        else:
            return jsonify({"status": "error", "message": "Invalid action or missing stock data."}), 400

    elif request.method == 'GET':
        # print('inside GET')
        # Retrieve all watchlists with detailed stock information
        watchlists_info = {
            name: {
                "goal": wl.goal,
                "stock_count": len(wl.stocklist),
                "stocks": [
                    {
                        "name": stock.name,
                        "date": stock.date.isoformat(),
                        "close": stock.close,
                        # "cmp": 300,
                        "link": f'https://in.tradingview.com/chart/GC72xsHV/?symbol=NSE%3A{stock.name}',
                        **get_fund_data(stock.name)
                    }
                    for stock in wl.stocklist
                ]
            }
            for name, wl in user.watchlists.items()
        }
        print(watchlists_info)
        return jsonify({"status": "success", "watchlists": watchlists_info}), 200
