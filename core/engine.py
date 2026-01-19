import time
from core.state_machine import StateMachine
from core.decision import DecisionEngine
from core.risk import RiskManager


class Engine:
    def __init__(self, broker, config):
        self.broker = broker
        self.config = config

        self.state = StateMachine()
        self.decision = DecisionEngine(config)
        self.risk = RiskManager(config)

    def tick(self, market_data):
        """
        Um ciclo completo do robô.
        """
        current_state = self.state.current()

        action = self.decision.decide(
            state=current_state,
            market=market_data,
        )

        if not self.risk.allow(current_state, action):
            return  # bloqueado por risco

        if action:
            self.execute(action)

    def execute(self, action):
        """
        Executa a ação aprovada.
        """
        kind = action["type"]

        if kind == "BUY":
            ok = self.broker.buy(action)
            if ok:
                self.state.set("IN_TRADE")

        elif kind == "SELL":
            ok = self.broker.sell(action)
            if ok:
                self.state.set("IDLE")

        # informa ao RiskManager que algo ocorreu
        self.risk.on_executed(action)
