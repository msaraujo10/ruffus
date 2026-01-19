# core/engine.py

from core.state_machine import State, StateMachine


class Engine:
    """
    Orquestrador central.
    Nenhuma regra de mercado aqui.
    Nenhuma regra de API aqui.
    """

    def __init__(self, broker, decision, risk):
        self.broker = broker
        self.decision = decision
        self.risk = risk
        self.state = StateMachine()

    def boot(self):
        self.state.set(State.SYNC)

    def tick(self, market_data):
        current = self.state.current()

        action = self.decision.decide(current, market_data)
        if not action:
            return

        if not self.risk.allow(current, action):
            return

        self.execute(action)

    def execute(self, action: dict):
        kind = action["type"]

        if kind == "BUY":
            self.state.set(State.ENTERING)
            ok = self.broker.buy(action)
            if ok:
                self.state.set(State.IN_POSITION)
            else:
                self.state.set(State.ERROR)

        elif kind == "SELL":
            self.state.set(State.EXITING)
            ok = self.broker.sell(action)
            if ok:
                self.state.set(State.POST_TRADE)
                self.state.set(State.IDLE)
            else:
                self.state.set(State.ERROR)
