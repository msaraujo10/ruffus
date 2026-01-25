from core.state_machine import State


class SimpleTrendStrategy:
    """
    Estratégia simples baseada em tendência,
    agora com regimes cognitivos reais.

    Regimes:
    - NORMAL
    - CAUTIOUS
    - DEFENSIVE
    - SUSPENDED
    """

    def __init__(self, config: dict):
        self.config = config
        self.entries = {}
        self.regime = "NORMAL"

    # ----------------------------
    # ADAPTAÇÃO COGNITIVA
    # ----------------------------
    def adapt(self, diagnosis: dict) -> None:
        health = diagnosis.get("health", "OK")
        signals = diagnosis.get("signals", [])

        # Regimes fortes
        if health == "RISK_BLOCKED":
            self.regime = "SUSPENDED"

        elif health == "UNSTABLE":
            self.regime = "DEFENSIVE"

        # Influência humana
        elif any("Humano tem negado" in s for s in signals):
            self.regime = "CAUTIOUS"

        elif any("Múltiplas negações" in s for s in signals):
            self.regime = "CAUTIOUS"

        else:
            self.regime = "NORMAL"

    # ----------------------------
    # DECISÃO
    # ----------------------------
    def decide(self, state, world, context):
        mode = context.get("mode")

        # Estados absolutos
        if self.regime == "SUSPENDED":
            return None

        if self.regime == "DEFENSIVE" and state == State.IDLE:
            # Em modo defensivo, não abrimos novas posições
            return None

        # Respeito a modos externos
        if mode in ("PAUSED", "OBSERVADOR"):
            return None

        prices = world["prices"]

        # --------------------
        # ENTRADA
        # --------------------
        if state == State.IDLE:
            for symbol, price in prices.items():
                if price is None:
                    continue

                if self.regime == "CAUTIOUS":
                    # Em modo cauteloso, só entra se o "sinal" for forte
                    if not self.should_enter_strong(symbol, price):
                        continue
                else:
                    if not self.should_enter(symbol, price):
                        continue

                self.entries[symbol] = price
                return {
                    "type": "BUY",
                    "symbol": symbol,
                    "price": price,
                }

        # --------------------
        # SAÍDA
        # --------------------
        if state == State.IN_POSITION:
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

    # ----------------------------
    # HEURÍSTICAS
    # ----------------------------
    def should_enter(self, symbol: str, price: float) -> bool:
        # Heurística básica atual
        return True

    def should_enter_strong(self, symbol: str, price: float) -> bool:
        """
        Versão mais exigente do sinal.
        Por enquanto, é igual à normal,
        mas aqui é onde filtros reais entrarão no futuro.
        """
        return True

    # ----------------------------
    # PERSISTÊNCIA
    # ----------------------------
    def export(self) -> dict:
        return {
            "entries": dict(self.entries),
            "regime": self.regime,
        }

    def import_state(self, data: dict | None):
        if not data:
            return

        self.entries = data.get("entries", {})
        self.regime = data.get("regime", "NORMAL")
