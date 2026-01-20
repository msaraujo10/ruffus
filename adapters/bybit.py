import random


class BybitBroker:
    """
    Broker REAL (mockado nesta fase).

    Nesta etapa ele ainda não fala com a API da Bybit.
    Ele apenas imita o comportamento do mercado real,
    mantendo o mesmo contrato do VirtualBroker.
    """

    def __init__(self, symbols: list[str]):
        self.symbols = symbols

        # preços internos simulados por símbolo
        self.prices = {s: 1.0 for s in symbols}

        # controle simples de posição
        self.positions = {}

    def tick(self) -> dict:
        """
        Retorna um feed de mercado realista:

        {
            "BTCUSDT": 43210.5,
            "ETHUSDT": 2310.2,
        }
        """
        feed = {}

        for s in self.symbols:
            drift = random.uniform(-0.004, 0.006)
            self.prices[s] *= 1 + drift
            feed[s] = round(self.prices[s], 6)

        return feed

    def buy(self, action: dict) -> bool:
        symbol = action["symbol"]
        price = action["price"]

        self.positions[symbol] = price
        print(f"🟢 [REAL-MOCK] COMPRA {symbol} @ {price:.6f}")
        return True

    def sell(self, action: dict) -> bool:
        symbol = action["symbol"]
        price = action["price"]

        entry = self.positions.pop(symbol, None)
        if entry:
            change = ((price - entry) / entry) * 100
            print(f"🔴 [REAL-MOCK] VENDA {symbol} @ {price:.6f} | {change:.2f}%")
        else:
            print(f"🔴 [REAL-MOCK] VENDA {symbol} @ {price:.6f}")

        return True
