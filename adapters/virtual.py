import random


class VirtualBroker:
    """
    Simulador multi-ativo de exchange.
    Mantém um preço independente para cada símbolo.
    """

    def __init__(self, symbols: list[str]):
        # preço inicial por símbolo
        self.prices = {s: 1.0 for s in symbols}
        self.entries = {}

    def tick(self) -> dict:
        """
        Avança o mercado de todos os ativos.
        Retorna algo como:
        {
            "BTCUSDT": 1.0023,
            "ETHUSDT": 0.9981,
            ...
        }
        """
        feed = {}

        for symbol, price in self.prices.items():
            drift = random.uniform(-0.006, 0.009)
            new_price = price * (1 + drift)
            self.prices[symbol] = new_price
            feed[symbol] = round(new_price, 6)

        return feed

    def buy(self, symbol: str, action: dict) -> bool:
        price = self.prices[symbol]
        self.entries[symbol] = price
        print(f"🚀 COMPRA {symbol} @ {price:.6f}")
        return True

    def sell(self, symbol: str, action: dict) -> bool:
        price = self.prices[symbol]
        entry = self.entries.get(symbol)

        if entry:
            profit = ((price - entry) / entry) * 100
            print(f"🏁 VENDA {symbol} @ {price:.6f} | {profit:.2f}%")
            del self.entries[symbol]

        return True
