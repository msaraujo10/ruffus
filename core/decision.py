from core.state_machine import State


class DecisionEngine:
    """
    Cérebro do robô.
    Agora opera sobre um mundo multi-ativo.
    """

    def __init__(self, config: dict):
        self.config = config
        self.entry = None  # {"symbol": str, "price": float}

    def decide(self, state: State, world: dict):
        # world = {"BTCUSDT": {"price": 1.002}, "ETHUSDT": {"price": 0.998}, ...}

        # Procurar entrada
        if state == State.IDLE:
            for symbol, data in world.items():
                price = data["price"]

                if self.should_enter(symbol, price):
                    self.entry = {"symbol": symbol, "price": price}
                    return {
                        "type": "BUY",
                        "symbol": symbol,
                        "price": price,
                    }

        # Gerenciar posição
        if state == State.IN_POSITION and self.entry:
            symbol = self.entry["symbol"]
            entry_price = self.entry["price"]

            price = world[symbol]["price"]
            change = ((price - entry_price) / entry_price) * 100

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

    def should_enter(self, symbol: str, price: float) -> bool:
        # Por enquanto: sempre permite
        return True
