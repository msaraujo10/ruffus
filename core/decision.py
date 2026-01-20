from core.state_machine import State


class DecisionEngine:
    def __init__(self, config: dict, store):
        self.config = config
        self.store = store

        data = self.store.load()
        self.entries = data.get("entries", {})

    def _persist(self):
        self.store.save({"entries": self.entries})

    def decide(self, state: State, world: dict):
        prices = world["prices"]

        if state == State.IDLE:
            for symbol, price in prices.items():
                if price is None:
                    continue

                if self.should_enter(symbol, price):
                    self.entries[symbol] = price
                    self._persist()
                    return {
                        "type": "BUY",
                        "symbol": symbol,
                        "price": price,
                    }

        if state == State.IN_POSITION:
            for symbol, entry in list(self.entries.items()):
                price = prices.get(symbol)
                if price is None:
                    continue

                change = ((price - entry) / entry) * 100

                if change <= self.config["stop_loss"]:
                    del self.entries[symbol]
                    self._persist()
                    return {
                        "type": "SELL",
                        "symbol": symbol,
                        "price": price,
                        "reason": "STOP",
                    }

                if change >= self.config["take_profit"]:
                    del self.entries[symbol]
                    self._persist()
                    return {
                        "type": "SELL",
                        "symbol": symbol,
                        "price": price,
                        "reason": "PROFIT",
                    }

        return None

    def should_enter(self, symbol: str, price: float) -> bool:
        return True
