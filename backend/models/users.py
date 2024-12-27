from datetime import datetime
import random
import json
import time
import threading


class Stock:
    def __init__(self, name, date, close, cmp=None, open=None, high=None, low=None, volume=None):
        self.name = name
        self.date = date
        self.close = close
        self.cmp = cmp if cmp is not None else close
        self.open = open
        self.high = high
        self.low = low
        self.volume = volume

    def __repr__(self):
        return f"Stock({self.name}, Date: {self.date}, Close: {self.close}, CMP: {self.cmp})"

    def update_cmp(self, new_cmp):
        self.cmp = new_cmp


class Watchlist:
    def __init__(self, name, goal):
        self.name = name
        self.goal = goal
        self.stocklist = []

    def add_stock(self, stock):
        if all(s.name != stock.name or s.date != stock.date for s in self.stocklist):
            self.stocklist.append(stock)
            print(f"Added {stock.name} to {self.name} watchlist.")
        else:
            print(f"{stock.name} on {stock.date} is already in the {self.name} watchlist.")

    def remove_stock(self, stock_name, date=None):
        self.stocklist = [s for s in self.stocklist if s.name != stock_name or (date and s.date != date)]
        print(f"Removed {stock_name} from {self.name} watchlist.")

    def update_cmp(self):
        for stock in self.stocklist:
            new_cmp = self.fetch_latest_price(stock.name)
            stock.update_cmp(new_cmp)

    def fetch_latest_price(self, stock_name):
        # Placeholder: Replace with actual API call to fetch the latest price
        return round(random.uniform(100, 500), 2)

    @classmethod
    def from_dict(cls, data):
        name = data.get("name")
        goal = data.get("goal")
        watchlist = cls(name, goal)

        watchlist.stocklist = [
            Stock(
                name=stock_data["name"],
                date=datetime.fromisoformat(stock_data["date"]),
                close=stock_data["close"],
                cmp=stock_data.get("cmp"),
                open=stock_data.get("open"),
                high=stock_data.get("high"),
                low=stock_data.get("low"),
                volume=stock_data.get("volume")
            )
            for stock_data in data.get("stocks", [])
        ]
        return watchlist


class StockAlert:
    def __init__(self, stock_name, trigger_price, to_trade, condition, date=None):
        self.stock_name = stock_name
        self.trigger_price = trigger_price
        self.to_trade = to_trade
        self.condition = condition
        self.date = date or datetime.now().date()  # Default to today's date
        self.triggered = False
        self.read_alert = False

    def __repr__(self):
        return (f"StockAlert(Stock: {self.stock_name}, Date: {self.date}, Trade: {self.to_trade}, "
                f"Trigger: {self.trigger_price}, Condition: {self.condition}, Triggered: {self.triggered})")

    def to_dict(self):
        return {
            "stock_name": self.stock_name,
            "date": self.date.isoformat(),  # Convert date to ISO format string
            "to_trade": self.to_trade,
            "trigger_price": self.trigger_price,
            "condition": self.condition,
            "triggered": self.triggered,
            "read_alert": self.read_alert
        }

    @classmethod
    def from_dict(cls, data):
        alert = cls(
            stock_name=data["stock_name"],
            date=datetime.fromisoformat(data["date"]),
            to_trade=data["to_trade"],
            trigger_price=data["trigger_price"],
            condition=data["condition"]
        )
        alert.triggered = data.get("triggered", False)
        alert.read_alert = data.get("read_alert", False)
        return alert

    def check_trigger(self, ohlcv_data):
        """
        Checks the latest closing price for the stock against the trigger price
        and updates the triggered status.
        """
        try:
            latest_price = ohlcv_data['daily'][self.stock_name]['Close'].iloc[-1]

            # Check condition (assuming "price crosses" means >= for buy and <= for sell)
            if not self.triggered:
                if self.to_trade == "buy" and latest_price >= self.trigger_price:
                    self.triggered = True
                    print(f"Trigger activated for BUY on {self.stock_name} at {latest_price}.")
                elif self.to_trade == "sell" and latest_price <= self.trigger_price:
                    self.triggered = True
                    print(f"Trigger activated for SELL on {self.stock_name} at {latest_price}.")
        except KeyError:
            print(f"Error: Stock {self.stock_name} not found in provided OHLCV data.")
        except Exception as e:
            print(f"Error while checking trigger: {e}")

    def mark_as_read(self):
        """
        Marks the alert as read, resetting the read_alert status.
        """
        if self.triggered:
            self.read_alert = True
            print(f"Alert for {self.stock_name} marked as read.")


class User:
    def __init__(self, username, password, email, phone, role="guest", is_active=True):
        self.username = username
        self.password = password
        self.email = email
        self.phone = phone
        self.role = role
        self.is_active = is_active
        self.watchlists = {}
        self.saved_conditions = {}
        self.stock_alerts = []  # Array of StockAlert objects
        self.monitoring_thread = None
        self.monitoring_active = False


    def add_stock_alert(self, stock_name, trigger_price, to_trade, condition, date=None):

        date = date or datetime.now().date()  # Use today's date if none provided
        new_alert = StockAlert(stock_name, trigger_price, to_trade, condition, date)
        self.stock_alerts.append(new_alert)
        print(f"Added alert for {stock_name} with trigger price {trigger_price} on {date}.")

    def remove_stock_alert(self, stock_name, date=None):
        initial_count = len(self.stock_alerts)
        self.stock_alerts = [
            alert for alert in self.stock_alerts
            if alert.stock_name != stock_name or (date and alert.date != date)
        ]
        if len(self.stock_alerts) < initial_count:
            print(f"Stock alert for {stock_name} removed.")
        else:
            print(f"No stock alert found for {stock_name} on the given date.")
    def monitor_alerts(self, ohlcv_data):
        """
        Continuously monitors stock alerts every 10 minutes in a separate thread.
        """
        self.monitoring_active = True
        while self.monitoring_active:
            print(f"Monitoring alerts for user {self.username}...")
            for alert in self.stock_alerts:
                alert.check_trigger(ohlcv_data)
            time.sleep(600)  # Wait for 10 minutes

    def start_monitoring(self, ohlcv_data):
        """
        Starts the monitoring process in a background thread.
        """
        if self.monitoring_thread is None or not self.monitoring_thread.is_alive():
            print(f"Starting monitoring for user {self.username}...")
            self.monitoring_thread = threading.Thread(
                target=self.monitor_alerts, args=(ohlcv_data,), daemon=True
            )
            self.monitoring_thread.start()
        else:
            print(f"Monitoring already running for user {self.username}.")

    def stop_monitoring(self):
        """
        Stops the monitoring process.
        """
        if self.monitoring_active:
            print(f"Stopping monitoring for user {self.username}...")
            self.monitoring_active = False
            if self.monitoring_thread:
                self.monitoring_thread.join()

    def add_condition(self, name, method, conditions, user_manager):
        self.saved_conditions[name] = {
            "name": name,
            "method": method,
            "conditions": [
                {
                    "field1": condition["field1"],
                    "operator": condition["operator"],
                    "field2": condition["field2"],
                    "multiple": float(condition.get("multiple", 1.0))
                }
                for condition in conditions
            ]
        }
        print(f"Condition {name} added.")
        user_manager.save_users()  # Save data after adding a condition

    def delete_condition(self, name, user_manager):
        if name in self.saved_conditions:
            del self.saved_conditions[name]
            print(f"Condition {name} deleted.")
            user_manager.save_users()  # Save data after deleting a condition
        else:
            print(f"Condition {name} not found.")

    def create_watchlist(self, name, goal, user_manager):
        if name not in self.watchlists:
            self.watchlists[name] = Watchlist(name, goal)
            print(f"Watchlist '{name}' created.")
            user_manager.save_users()  # Save data after creating a watchlist
        else:
            print(f"Watchlist '{name}' already exists.")

    def delete_watchlist(self, name, user_manager):
        if name in self.watchlists:
            del self.watchlists[name]
            print(f"Watchlist '{name}' deleted.")
            user_manager.save_users()  # Save data after deleting a watchlist
        else:
            print(f"Watchlist '{name}' does not exist.")

    def to_dict(self):
        return {
            "username": self.username,
            "password": self.password,
            "email": self.email,
            "phone": self.phone,
            "role": self.role,
            "is_active": self.is_active,
            "watchlists": {
                name: {
                    "goal": wl.goal,
                    "stocks": [
                        {
                            "name": stock.name,
                            "date": stock.date.isoformat(),
                            "close": stock.close,
                            "cmp": stock.cmp,
                            "open": stock.open,
                            "high": stock.high,
                            "low": stock.low,
                            "volume": stock.volume
                        }
                        for stock in wl.stocklist
                    ]
                }
                for name, wl in self.watchlists.items()
            },
            "saved_conditions": self.saved_conditions,
            "stock_alerts": [alert.to_dict() for alert in self.stock_alerts]
        }

    @classmethod
    def from_dict(cls, data):
        user = cls(
            username=data["username"],
            password=data["password"],
            email=data.get("email", ""),
            phone=data.get("phone", ""),
            role=data.get("role", "guest"),
            is_active=data.get("is_active", False)
        )
        user.saved_conditions = data.get("saved_conditions", {})
        user.watchlists = {
            name: Watchlist.from_dict(wl_data)
            for name, wl_data in data.get("watchlists", {}).items()
        }
        user.stock_alerts = [
            StockAlert.from_dict(alert_data) for alert_data in data.get("stock_alerts", [])
        ]
        return user


class UserManager:
    def __init__(self, filename='data/users.json'):
        self.filename = filename
        self.users = []
        self.load_users()

    def add_user(self, username, password, email, phone, role="guest"):
        if self.is_username_taken(username):
            print(f"Error: Username '{username}' already exists.")
            return None

        new_user = User(username, password, email, phone, role)
        self.users.append(new_user)
        self.save_users()
        print(f"User '{username}' added but needs admin authentication.")
        return new_user

    def authenticate_user(self, username, admin_username):
        admin = self.get_user_by_username(admin_username)
        if admin and admin.role == "admin":
            user = self.get_user_by_username(username)
            if user and not user.is_active:
                user.is_active = True
                user.role="user"
                self.save_users()
                # self.load_users()
                print(f"User '{username}' authenticated by admin '{admin_username}'.")
                return True
        print(f"Authentication failed for user '{username}'.")
        return False

    def is_username_taken(self, username):
        return any(user.username == username for user in self.users)

    def get_user_by_username(self, username):
        return next((user for user in self.users if user.username == username), None)

    def load_users(self):
        try:
            with open(self.filename, 'r') as f:
                data = json.load(f)
            self.users = [User.from_dict(user_data) for user_data in data]
        except FileNotFoundError:
            print(f"File '{self.filename}' not found. Starting with an empty user list.")
            self.users = []
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            self.users = []

    def save_users(self):
        with open(self.filename, 'w') as f:
            json.dump([user.to_dict() for user in self.users], f)

