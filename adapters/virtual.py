import random


class VirtualBroker:
    """
    Broker virtual multi-ativo.
    Simula uma exchange real.
    """

    def __init__(self):
        # preços por símbolo
        self.prices: dict[str, float] = {}

        # preço de entrada por símbolo
        self.entries: dict[str, float] = {}

    def tick(self, symbols: list[str]) -> dict:
        """
        Gera um feed multi-ativo:
        {
            "BTCUSDT": 1.0023,
            "ETHUSDT": 0.9981,
            ...
        }
        """
        feed = {}

        for s in symbols:
            if s not in self.prices:
                self.prices[s] = 1.0

            drift = random.uniform(-0.005, 0.008)
            self.prices[s] *= 1 + drift
            feed[s] = round(self.prices[s], 6)

        return feed

    def buy(self, symbol: str, action: dict) -> bool:
        price = action["price"]
        self.entries[symbol] = price
        print(f"🚀 COMPRA {symbol} @ {price}")
        return True

    def sell(self, symbol: str, action: dict) -> bool:
        price = action["price"]
        entry = self.entries.get(symbol)

        if entry:
            profit = ((price - entry) / entry) * 100
            print(f"🏁 VENDA {symbol} @ {price} | {profit:.2f}%")
            self.entries.pop(symbol, None)

        return True
