# core/decision.py

from core.state_machine import State


class DecisionEngine:
    """
    Cérebro do robô.
    Apenas observa o mundo e decide.
    """

    def __init__(self, config: dict):
        self.config = config

    def decide(self, state: State, world: dict):
        price = world["price"]

        # Procurar entrada
        if state == State.IDLE and not world["in_position"]:
            return {
                "type": "BUY",
                "symbol": world["symbol"],
                "price": price,
            }

        # Gerenciar saída
        if state == State.IN_POSITION and world["in_position"]:
            entry = world["entry_price"]
            change = ((price - entry) / entry) * 100

            if change <= self.config["stop_loss"]:
                return {
                    "type": "SELL",
                    "symbol": world["symbol"],
                    "price": price,
                    "reason": "STOP",
                }

            if change >= self.config["take_profit"]:
                return {
                    "type": "SELL",
                    "symbol": world["symbol"],
                    "price": price,
                    "reason": "PROFIT",
                }

        return None
