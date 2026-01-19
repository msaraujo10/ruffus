import random
from core.broker import BrokerBase


class VirtualBroker(BrokerBase):
    """
    Simula um mercado simples para testes.
    Não conhece Bybit, API, nem rede.
    Apenas emula preço, compra e venda.
    """

    def __init__(self, start_price=1.0):
        self.price = start_price
        self.position_open = False
        self.entry_price = None

    def get_market_data(self):
        # simula variação de preço
        delta = random.uniform(-0.005, 0.008)
        self.price *= 1 + delta

        return {
            "symbol": "TESTE-USD",
            "price": round(self.price, 6),
            "timestamp": None,
        }

    def buy(self, action: dict) -> bool:
        if self.position_open:
            return False

        self.position_open = True
        self.entry_price = self.price
        print(f"🧪 BUY @ {self.price:.6f}")
        return True

    def sell(self, action: dict) -> bool:
        if not self.position_open:
            return False

        result = ((self.price - self.entry_price) / self.entry_price) * 100
        print(f"🧪 SELL @ {self.price:.6f} | RESULT {result:.2f}%")

        self.position_open = False
        self.entry_price = None
        return True
