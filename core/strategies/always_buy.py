from core.state_machine import State
from .base import Strategy


class AlwaysBuyStrategy(Strategy):
    name = "always_buy"

    def __init__(self, config: dict):
        self.config = config
        self.entries: dict[str, float] = {}

    def decide(self, state: State, world: dict) -> dict | None:
        prices = world["prices"]

        # Entrada
        if state == State.IDLE:
            for symbol, price in prices.items():
                if price is None:
                    continue

                self.entries[symbol] = price
                return {
                    "type": "BUY",
                    "symbol": symbol,
                    "price": price,
                }

        # Saída
        if state == State.IN_POSITION:
            for symbol, entry in list(self.entries.items()):
                price = prices.get(symbol)
                if price is None:
                    continue

                change = ((price - entry) / entry) * 100

                if change <= self.config["stop_loss"]:
                    return {
                        "type": "SELL",
                        "symbol": symbol,
                        "price": price,
                        "reason": "STOP",
                    }

                if change >= self.config["take_profit"]:
                    return {
                        "type": "SELL",
                        "symbol": symbol,
                        "price": price,
                        "reason": "PROFIT",
                    }

        return None

    def export(self) -> dict:
        return {"entries": dict(self.entries)}

    def import_state(self, data: dict | None):
        if not data:
            return
        self.entries = data.get("entries", {})
