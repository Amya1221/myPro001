from flask import Flask,g,render_template, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO
from flask_jwt_extended import JWTManager
from routes import auth, watchlists, conditions, screen,admin,alerts
from utils.initialize import initialize
from utils.background import start_background_update_thread
from services.data_service import DataService
from models.users import UserManager
from utils.screening import screen_data
#background separate process
# from multiprocessing import Manager
# from utils.background1 import start_background_update_process

app = Flask(__name__)
app.config.from_object('config.Config')

# Extensions
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")  # Enable cross-origin resource sharing for SocketIO
jwt = JWTManager(app)

# Initialize Services
user_manager = UserManager(app.config['USER_DATA_FILE'])  # Assuming 'USER_DATA_FILE' is defined in your config
data_service = DataService()  # Initialize your data service (e.g., for fetching stock data)

# Global Variables
scriplist, scripdata, fundamentals, fundamentals_fund = initialize()  # Custom initialization logic
ohlcv_data = data_service.load_ohlcv_data(['daily','weekly'], scriplist)  # Load stock data for daily interval
# print('screendata',scripdata)

# manager = Manager()
# shared_ohlcv_data = manager.dict(ohlcv_data)  # Convert `ohlcv_data` to a Manager dictionary

# Start Background Process
# start_background_update_process(scriplist, scripdata, shared_ohlcv_data, data_service)

@app.before_request
def set_globals():
    g.scriplist = scriplist
    g.scripdata = scripdata
    g.fundamentals = fundamentals
    g.ohlcv_data = ohlcv_data
    g.fundamentals_fund=fundamentals_fund
# @app.before_request
# def set_globals():
#     g.scriplist = scriplist
#     g.scripdata = scripdata
#     g.fundamentals = fundamentals
#     g.ohlcv_data = shared_ohlcv_data  # Use the shared dictionary
#     g.fundamentals_fund = fundamentals_fund

# Register Blueprints

app.register_blueprint(auth.bp, url_prefix='/auth')
app.register_blueprint(watchlists.watchlists_bp, url_prefix='/')
app.register_blueprint(conditions.conditions_bp, url_prefix='/')

app.register_blueprint(screen.bp, url_prefix='/')
app.register_blueprint(admin.admin_bp, url_prefix='/admin')
app.register_blueprint(alerts.alerts_bp,url_prefix='/alerts')

# Background Task
# start_background_update_thread(socketio, scriplist, scripdata, ohlcv_data, data_service)

if __name__ == '__main__':
    socketio.run(app, allow_unsafe_werkzeug=True)  # Run the app with SocketIO
