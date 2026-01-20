from core.state_machine import State


class DecisionEngine:
    """
    Cérebro multi-ativo.
    Mantém memória de entradas por símbolo.
    """

    def __init__(self, config: dict):
        self.config = config
        self.entries: dict[str, float] = {}

    def decide(self, state: State, world: dict):
        prices = world["prices"]

        # Procurar entrada
        if state == State.IDLE:
            for symbol, price in prices.items():
                if price is None:
                    continue

                if self.should_enter(symbol, price):
                    self.entries[symbol] = price
                    return {
                        "type": "BUY",
                        "symbol": symbol,
                        "price": price,
                        "reason": "ENTRY",
                    }

        # Gerenciar saída
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
                        "reason": "PROFIT",
                    }

                if change >= self.config["take_profit"]:
                    return {
                        "type": "SELL",
                        "symbol": symbol,
                        "price": price,
                        "reason": "PROFIT",
                    }

        return None

    def should_enter(self, symbol: str, price: float) -> bool:
        return True

    # ---------- Persistência ----------

    def export(self) -> dict:
        return {"entries": dict(self.entries)}

    def import_state(self, data: dict):
        if not data:
            return
        self.entries = data.get("entries", {})
