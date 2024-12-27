class WatchlistService:
    def __init__(self, data_service):
        self.data_service = data_service

    def update_watchlist_prices(self, watchlist):
        for stock in watchlist.stocklist:
            new_price = self.data_service.fetch_latest_price(stock.name)
            if new_price:
                stock.update_cmp(new_price)

    def analyze_watchlist(self, watchlist):
        performance = {}
        for stock in watchlist.stocklist:
            change = round(((stock.cmp - stock.close) / stock.close) * 100, 2)
            performance[stock.name] = change
        return performance
