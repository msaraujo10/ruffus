import random
import time


class VirtualBroker:
    """
    Simula uma exchange.
    Não há dinheiro real aqui.
    """

    def __init__(self):
        self.price = 1.0
        self.entry_price = None

    def tick(self):
        """
        Simula movimento de mercado.
        """
        drift = random.uniform(-0.005, 0.008)
        self.price *= 1 + drift
        return self.price

    def buy(self, action: dict) -> bool:
        self.entry_price = self.price
        print(f"🚀 COMPRA @ {self.price:.4f}")
        return True

    def sell(self, action: dict) -> bool:
        if self.entry_price:
            profit = ((self.price - self.entry_price) / self.entry_price) * 100
            print(f"🏁 VENDA @ {self.price:.4f} | {profit:.2f}%")
            self.entry_price = None
        return True
