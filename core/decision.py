from core.state_machine import State


class DecisionEngine:
    """
    Cérebro do robô.
    Só decide. Não executa.
    """

    def __init__(self, config: dict):
        self.config = config

        # memória interna simples
        self.entry_price = None

    def decide(self, state: State, market: dict):
        price = market["price"]

        # Estado ocioso: procurar entrada
        if state == State.IDLE:
            if self.should_enter(market):
                self.entry_price = price
                return {
                    "type": "BUY",
                    "symbol": market["symbol"],
                    "price": price,
                }

        # Estado em posição: gerenciar saída
        if state == State.IN_POSITION:
            if self.entry_price is None:
                return None

            change = ((price - self.entry_price) / self.entry_price) * 100

            if change <= self.config["stop_loss"]:
                return {
                    "type": "SELL",
                    "symbol": market["symbol"],
                    "price": price,
                    "reason": "STOP",
                }

            if change >= self.config["take_profit"]:
                return {
                    "type": "SELL",
                    "symbol": market["symbol"],
                    "price": price,
                    "reason": "PROFIT",
                }

        return None

    def should_enter(self, market: dict) -> bool:
        """
        Por enquanto:
        - sempre permite entrada
        No futuro:
        - filtros técnicos
        - volume
        - tendência
        """
        return True
