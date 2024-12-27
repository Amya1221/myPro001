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