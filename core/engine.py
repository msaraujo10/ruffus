from core.state_machine import State, StateMachine


class Engine:
    """
    Orquestrador central.
    Agora totalmente desacoplado do mundo físico.
    """

    def __init__(self, broker, decision, risk, world):
        self.broker = broker
        self.decision = decision
        self.risk = risk
        self.world = world
        self.state = StateMachine()

    def boot(self):
        self.state.set(State.SYNC)
        self.state.set(State.IDLE)

    def tick(self, snapshot: dict):
        current = self.state.current()

        action = self.decision.decide(current, snapshot)

        if not action:
            return

        if not self.risk.allow(current, action):
            return

        self.execute(action)

    def execute(self, action: dict):
        kind = action["type"]
        symbol = action["symbol"]
        price = action["price"]

        if kind == "BUY":
            self.state.set(State.ENTERING)
            ok = self.broker.buy(symbol, price)
            if ok:
                self.world.set_entry(symbol, price)
                self.world.set_state(symbol, State.IN_POSITION)
                self.state.set(State.IN_POSITION)
            else:
                self.state.set(State.ERROR)

        elif kind == "SELL":
            self.state.set(State.EXITING)
            ok = self.broker.sell(symbol, price)
            if ok:
                self.world.set_entry(symbol, None)
                self.world.set_state(symbol, State.IDLE)
                self.state.set(State.POST_TRADE)
                self.state.set(State.IDLE)
            else:
                self.state.set(State.ERROR)
