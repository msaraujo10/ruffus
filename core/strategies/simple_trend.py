from core.strategies.base import BaseStrategy


class SimpleTrendStrategy(BaseStrategy):
    """
    Estratégia mínima de referência.

    Regras:
    - Sempre entra no primeiro símbolo disponível
    - Sai quando atingir stop ou take
    """

    def __init__(self, config: dict):
        self.config = config
        self.entries = {}

    def export(self) -> dict:
        return {
            "entries": dict(self.entries),
        }

    def import_state(self, data: dict | None):
        if not data:
            return
        self.entries = dict(data.get("entries", {}))

    def decide(self, world: dict, state):
        prices = world["prices"]

        # Entrada
        if state.name == "IDLE":
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
        if state.name == "IN_POSITION":
            for symbol, entry in list(self.entries.items()):
                price = prices.get(symbol)
                if not price:
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
