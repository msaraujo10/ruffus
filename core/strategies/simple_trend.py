from core.state_machine import State
from .base import BaseStrategy


class SimpleTrendStrategy(BaseStrategy):
    """
    Estratégia simples baseada em tendência.

    Agora é consciente do estado cognitivo do sistema:
    - NORMAL
    - DEFENSIVE
    - SUSPENDED
    """

    name = "simple_trend"

    def __init__(self, config: dict):
        self.config = config
        self.entries: dict[str, float] = {}
        self.mode = "NORMAL"

    # ----------------------------
    # ADAPTAÇÃO COGNITIVA
    # ----------------------------
    def adapt(self, diagnosis: dict) -> None:
        health = diagnosis.get("health", "OK")

        if health == "RISK_BLOCKED":
            self.mode = "SUSPENDED"

        elif health == "UNSTABLE":
            self.mode = "DEFENSIVE"

        else:
            self.mode = "NORMAL"

    # ----------------------------
    # DECISÃO
    # ----------------------------
    def decide(self, state, world: dict, context: dict | None = None):
        context = context or {}
        mode = context.get("mode")

        # Consciência de regime
        if mode in ("PAUSED", "OBSERVADOR"):
            return None

        prices = world.get("prices", {})

        # Entrada
        if state == State.IDLE:
            for symbol, price in prices.items():
                if price is None:
                    continue

                if self.mode == "DEFENSIVE":
                    ok = self.should_enter_defensive(symbol, price)
                elif self.mode == "SUSPENDED":
                    ok = False
                else:
                    ok = self.should_enter(symbol, price)

                if ok:
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

    # ----------------------------
    # HEURÍSTICAS
    # ----------------------------
    def should_enter(self, symbol: str, price: float) -> bool:
        return True

    def should_enter_defensive(self, symbol: str, price: float) -> bool:
        # Versão conservadora: hoje reutiliza a mesma lógica,
        # mas no futuro pode exigir volume, candle, etc.
        return True

    # ----------------------------
    # CONTRATO CANÔNICO
    # ----------------------------
    def learn(self, events: list):
        # Estratégia simples não aprende por enquanto
        pass

    def export(self) -> dict:
        return {
            "entries": dict(self.entries),
            "mode": self.mode,
        }

    def import_state(self, data: dict | None):
        if not data:
            return

        self.entries = data.get("entries", {})
        self.mode = data.get("mode", "NORMAL")
