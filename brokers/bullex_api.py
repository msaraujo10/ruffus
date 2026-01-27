import random
import time


class BullexAPI:
    """
    Camada de abstração da Bullex.

    Hoje: simulada.
    Futuro: conexão real (HTTP, WebSocket, browser automation, etc).
    """

    def __init__(self, account="DEMO"):
        self.account = account
        self._prices = {}

    def get_last_candle(self, symbol, timeframe="5m"):
        """
        Retorna algo como:
        {
            "open": 1.234,
            "close": 1.236,
            "high": 1.238,
            "low": 1.232,
            "ts": 1700000000
        }
        """
        base = self._prices.get(symbol, random.uniform(1.0, 2.0))
        delta = random.uniform(-0.002, 0.002)

        open_ = base
        close = base + delta
        high = max(open_, close) + abs(random.uniform(0, 0.001))
        low = min(open_, close) - abs(random.uniform(0, 0.001))

        self._prices[symbol] = close

        return {
            "open": round(open_, 5),
            "close": round(close, 5),
            "high": round(high, 5),
            "low": round(low, 5),
            "ts": int(time.time()),
        }

    def get_candles(self, symbol, timeframe="4h", limit=50):
        candles = []
        price = self._prices.get(symbol, random.uniform(1.0, 2.0))

        for _ in range(limit):
            delta = random.uniform(-0.01, 0.01)
            open_ = price
            close = price + delta
            high = max(open_, close) + abs(random.uniform(0, 0.005))
            low = min(open_, close) - abs(random.uniform(0, 0.005))

            candles.append(
                {
                    "open": round(open_, 5),
                    "close": round(close, 5),
                    "high": round(high, 5),
                    "low": round(low, 5),
                }
            )

            price = close

        return candles

    def place_demo_order(self, symbol, side, amount, expiry):
        """
        Simula uma ordem binária DEMO.
        Retorna True se aceita.
        """
        return True
