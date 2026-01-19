from core.state_machine import State


class DecisionEngine:
    """
    Cérebro multi-ativo do robô.

    Ele:
    - decide entradas por símbolo
    - acompanha preços de entrada por símbolo
    - gera ações BUY / SELL independentes
    """

    def __init__(self, config: dict):
        self.config = config

        # memória por ativo
        # ex: { "BTCUSDT": 1.0023, "ETHUSDT": 0.9981 }
        self.entries: dict[str, float] = {}

    def decide(self, state: State, world: dict):
        """
        world = {
            "prices": {
                "BTCUSDT": 1.0023,
                "ETHUSDT": 0.9981,
            }
        }

        Retorna:
            None
            ou
            {"type": "BUY" / "SELL", "symbol": "...", "price": ...}
        """

        prices = world["prices"]

        # Se não estamos em posição, procurar entrada
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
                    }

        # Se estamos em posição, gerenciar saída
        if state == State.IN_POSITION:
            for symbol, entry in list(self.entries.items()):
                price = prices.get(symbol)
                if price is None:
                    continue

                change = ((price - entry) / entry) * 100

                if change <= self.config["stop_loss"]:
                    self.entries.pop(symbol, None)
                    return {
                        "type": "SELL",
                        "symbol": symbol,
                        "price": price,
                        "reason": "STOP",
                    }

                if change >= self.config["take_profit"]:
                    self.entries.pop(symbol, None)
                    return {
                        "type": "SELL",
                        "symbol": symbol,
                        "price": price,
                        "reason": "PROFIT",
                    }

        return None

    def should_enter(self, symbol: str, price: float) -> bool:
        """
        Filtro de entrada.
        Por enquanto: sempre True.
        Depois: volume, tendência, candle, etc.
        """
        return True
