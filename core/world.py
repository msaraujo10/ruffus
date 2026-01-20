class World:
    """
    Representa o mundo observado pelo robô.
    Mantém preços por símbolo.
    """

    def __init__(self, symbols: list[str]):
        self.symbols = symbols
        self.prices = {s: None for s in symbols}

    def update(self, feed: dict):
        """
        feed = {
            "BTCUSDT": 43210.5,
            "ETHUSDT": 2310.2,
            ...
        }
        """
        for symbol, price in feed.items():
            if symbol in self.prices:
                self.prices[symbol] = price

    def snapshot(self) -> dict:
        return {"prices": dict(self.prices)}

    # ---------- Persistência ----------

    def export(self) -> dict:
        return {
            "symbols": list(self.symbols),
            "prices": dict(self.prices),
        }

    def import_state(self, data: dict):
        symbols = data.get("symbols")
        prices = data.get("prices")

        if symbols:
            self.symbols = symbols
            self.prices = {s: None for s in symbols}

        if prices:
            for s, p in prices.items():
                if s in self.prices:
                    self.prices[s] = p
