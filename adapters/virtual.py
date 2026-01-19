import random


class VirtualBroker:
    """
    Simula uma exchange multi-ativo.
    """

    def __init__(self, symbols: list[str]):
        self.symbols = symbols
        self.prices = {s: 1.0 for s in symbols}
        self.entry = None  # (symbol, price)

    def tick(self) -> dict:
        """
        Retorna um feed multi-ativo:
        {
            "BTCUSDT": 1.002,
            "ETHUSDT": 0.998,
            ...
        }
        """
        feed = {}

        for s in self.symbols:
            drift = random.uniform(-0.005, 0.008)
            self.prices[s] *= 1 + drift
            feed[s] = round(self.prices[s], 5)

        return feed

    def buy(self, action: dict) -> bool:
        symbol = action["symbol"]
        price = action["price"]
        self.entry = (symbol, price)
        print(f"🚀 COMPRA {symbol} @ {price}")
        return True

    def sell(self, action: dict) -> bool:
        if self.entry:
            symbol, entry_price = self.entry
            price = action["price"]
            profit = ((price - entry_price) / entry_price) * 100
            print(f"🏁 VENDA {symbol} @ {price} | {profit:.2f}%")
            self.entry = None
        return True
