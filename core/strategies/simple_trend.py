from core.state_machine import State


class SimpleTrendStrategy:
    """
    Estratégia simples baseada em tendência.

    Agora é consciente do estado cognitivo do sistema:
    - NORMAL
    - DEFENSIVE
    - SUSPENDED
    """

    def __init__(self, config: dict):
        self.config = config
        self.entries = {}
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
    def decide(self, state: State, world: dict, context: dict | None = None):
        prices = world.get("prices", {})

        # Modo SUSPENDED: nunca entrar
        if self.mode == "SUSPENDED":
            return None

        # Estado ocioso → procurar entrada
        if state == State.IDLE:
            for symbol, price in prices.items():
                if price is None:
                    continue

                # DEFENSIVE: exigir "sinal mais forte"
                if self.mode == "DEFENSIVE":
                    if not self.should_enter_defensive(symbol, price):
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

        # Em posição → gerenciar saída
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
        # Versão conservadora: hoje só reutiliza a mesma lógica,
        # mas no futuro pode exigir volume, candle, etc.
        return True
