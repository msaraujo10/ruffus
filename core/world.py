class World:
    """
    Representa a realidade sincronizada do mercado.
    Mantém preços por símbolo e pode ser serializado.
    """

    def __init__(self, symbols: list[str], store):
        self.symbols = symbols
        self.store = store
        self.prices = {s: None for s in symbols}

    def update(self, feed: dict):
        """
        feed = {
            "BTCUSDT": 43210.5,
            "ETHUSDT": 2310.2,
        }
        """
        for symbol, price in feed.items():
            if symbol in self.prices:
                self.prices[symbol] = price

    def snapshot(self) -> dict:
        return {"prices": dict(self.prices)}

    # -------- Persistência --------

    def export(self) -> dict:
        return {"prices": dict(self.prices)}

    def import_state(self, data: dict):
        if not data:
            return
        prices = data.get("prices", {})
        for symbol, price in prices.items():
            if symbol in self.prices:
                self.prices[symbol] = price
