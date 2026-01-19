# adapters/virtual.py

import random


class VirtualBroker:
    """
    Simula uma exchange.
    Produz um feed de mercado.
    """

    def __init__(self):
        self.prices = {
            "TESTEUSDT": 1.0,
        }

    def tick(self):
        feed = {}

        for symbol, price in self.prices.items():
            drift = random.uniform(-0.005, 0.008)
            new_price = price * (1 + drift)
            self.prices[symbol] = new_price

            feed[symbol] = {"price": round(new_price, 5)}

        return feed

    def buy(self, action: dict) -> bool:
        print(f"🚀 COMPRA {action['symbol']} @ {action['price']:.5f}")
        return True

    def sell(self, action: dict) -> bool:
        print(
            f"🏁 VENDA {action['symbol']} @ {action['price']:.5f} | {action.get('reason', '')}"
        )
        return True
