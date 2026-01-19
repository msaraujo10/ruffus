# core/decision.py

from core.state_machine import State


class DecisionEngine:
    """
    Cérebro do robô.
    Só decide. Não executa.
    """

    def __init__(self, config: dict):
        self.config = config
        self.entry_price = None
        self.current_symbol = None

    def decide(self, state: State, world: dict):
        # Estado ocioso: procurar entrada
        if state == State.IDLE:
            for symbol, data in world.items():
                price = data["price"]

                if self.should_enter(symbol, data):
                    self.entry_price = price
                    self.current_symbol = symbol
                    return {
                        "type": "BUY",
                        "symbol": symbol,
                        "price": price,
                    }

        # Estado em posição: gerenciar saída
        if state == State.IN_POSITION and self.current_symbol:
            data = world.get(self.current_symbol)
            if not data:
                return None

            price = data["price"]
            change = ((price - self.entry_price) / self.entry_price) * 100

            if change <= self.config["stop_loss"]:
                return {
                    "type": "SELL",
                    "symbol": self.current_symbol,
                    "price": price,
                    "reason": "STOP",
                }

            if change >= self.config["take_profit"]:
                return {
                    "type": "SELL",
                    "symbol": self.current_symbol,
                    "price": price,
                    "reason": "PROFIT",
                }

        return None

    def should_enter(self, symbol: str, data: dict) -> bool:
        return True
