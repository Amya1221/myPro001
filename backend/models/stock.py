
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
