import random
import time


class BullexAPI:
    def __init__(self, account="DEMO"):
        self.account = account
        self._last = {}
        self._prices = {}

    def get_last_candle(self, symbol, timeframe="5m"):
        now = time.time()

        if timeframe == "5m":
            block = int(now // 300)  # 5 minutos
        elif timeframe == "4h":
            block = int(now // 14400)  # 4 horas
        else:
            block = int(now)

        key = (symbol, timeframe)

        if key not in self._last or self._last[key]["ts"] != block:
            base = self._prices.get(symbol, random.uniform(1.0, 2.0))
            delta = random.uniform(-0.002, 0.002)

            open_ = base
            close = base + delta
            high = max(open_, close) + abs(random.uniform(0, 0.001))
            low = min(open_, close) - abs(random.uniform(0, 0.001))

            self._prices[symbol] = close

            self._last[key] = {
                "open": round(open_, 5),
                "close": round(close, 5),
                "high": round(high, 5),
                "low": round(low, 5),
                "ts": block,
            }

        return self._last[key]

    def place_demo_order(self, symbol, side, amount, expiry):
        """
        Simula uma ordem binária DEMO.
        Retorna True se aceita.
        """
        return True
