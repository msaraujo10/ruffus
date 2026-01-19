class World:
    def __init__(self, symbols):
        self.symbols = symbols
        self.prices = {s: None for s in symbols}

    def update(self, feed: dict):
        """
        Recebe algo como:
        {
            "BTCUSDT": 43210.5,
            "ETHUSDT": 2310.2,
            ...
        }
        """
        for symbol, price in feed.items():
            if symbol in self.prices:
                self.prices[symbol] = price

    def snapshot(self) -> dict:
        """
        Retorna o estado atual do mundo para o Engine.
        """
        return {"prices": dict(self.prices)}
