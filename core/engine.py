from core.state_machine import State, StateMachine


class Engine:
    """
    Orquestrador multi-ativo.
    Cada símbolo possui sua própria StateMachine.
    """

    def __init__(self, broker, decision, risk, symbols: list[str]):
        self.broker = broker
        self.decision = decision
        self.risk = risk

        # Uma máquina de estados por símbolo
        self.states: dict[str, StateMachine] = {s: StateMachine(s) for s in symbols}

    def boot(self):
        for sm in self.states.values():
            sm.set(State.SYNC)
            sm.set(State.IDLE)

    def tick(self, world_snapshot: dict):
        prices = world_snapshot["prices"]

        for symbol, sm in self.states.items():
            state = sm.current()
            price = prices.get(symbol)

            if price is None:
                continue

            market = {
                "symbol": symbol,
                "price": price,
            }

            action = self.decision.decide(state, {"prices": {symbol: price}})

            if not action:
                continue

            if not self.risk.allow(state, action):
                continue

            self.execute(symbol, sm, action)

    def execute(self, symbol: str, sm: StateMachine, action: dict):
        kind = action["type"]

        if kind == "BUY":
            sm.set(State.ENTERING)
            ok = self.broker.buy(symbol, action)
            if ok:
                sm.set(State.IN_POSITION)
            else:
                sm.set(State.ERROR)

        elif kind == "SELL":
            sm.set(State.EXITING)
            ok = self.broker.sell(symbol, action)
            if ok:
                sm.set(State.POST_TRADE)
                sm.set(State.IDLE)
            else:
                sm.set(State.ERROR)
