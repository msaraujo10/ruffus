from core.state_machine import State


class DecisionEngine:
    """
    Cérebro do robô.
    Multi-ativo.
    Decide em qual símbolo entrar e quando sair.
    """

    def __init__(self, config: dict):
        self.config = config
        self.current_symbol = None
        self.entry_price = None

    def decide(self, state: State, world: dict):
        """
        world = {
            "BTCUSDT": {"price": 0.99},
            "ETHUSDT": {"price": 1.01},
            ...
        }
        """

        # Procurar entrada
        if state == State.IDLE:
            for symbol, data in world.items():
                price = data["price"]

                if self.should_enter(symbol, data):
                    self.current_symbol = symbol
                    self.entry_price = price
                    return {
                        "type": "BUY",
                        "symbol": symbol,
                        "price": price,
                    }

        # Gerenciar posição
        if state == State.IN_POSITION and self.current_symbol:
            data = world[self.current_symbol]
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
        """
        Aqui entram os filtros reais no futuro.
        Por enquanto, sempre permite.
        """
        return True
