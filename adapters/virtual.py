# adapters/virtual.py

import random


class VirtualBroker:
    """
    Simula uma exchange.
    Não há dinheiro real aqui.
    """

    def __init__(self):
        self.price = 1.0

    def tick(self):
        """
        Simula movimento de mercado.
        Retorna um feed compatível com o World.
        """
        drift = random.uniform(-0.005, 0.008)
        self.price *= 1 + drift

        return {
            "price": self.price,
            "symbol": "TESTEUSDT",
        }

    def buy(self, action: dict) -> bool:
        print(f"🚀 COMPRA {action['symbol']} @ {self.price:.4f}")
        return True

    def sell(self, action: dict) -> bool:
        print(f"🏁 VENDA {action['symbol']} @ {self.price:.4f}")
        return True
