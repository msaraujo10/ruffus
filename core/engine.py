from core.state_machine import State


class Engine:
    """
    Orquestrador central.
    Não conhece API.
    Não conhece estratégia.
    Apenas coordena:
    World → Decision → Risk → Broker → StateMachine
    """

    def __init__(self, broker, decision, risk, world, store):
        self.broker = broker
        self.decision = decision
        self.risk = risk
        self.world = world
        self.store = store
        self.state = None  # será injetado no boot()

    def boot(self, state_machine):
        """
        Inicializa o sistema restaurando estado salvo, se existir.
        """
        self.state = state_machine

        data = self.store.load()
        if data:
            self.state.import_state(data.get("state"))
            self.world.import_state(data.get("world"))
            self.decision.import_state(data.get("decision"))
        else:
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

        if kind == "BUY":
            self.state.set(State.ENTERING)
            ok = self.broker.buy(symbol, action)
            if ok:
                self.state.set(State.IN_POSITION)
            else:
                self.state.set(State.ERROR)

        elif kind == "SELL":
            self.state.set(State.EXITING)
            ok = self.broker.sell(symbol, action)
            if ok:
                self.state.set(State.POST_TRADE)
                self.state.set(State.IDLE)
            else:
                self.state.set(State.ERROR)

        # Persistir sempre após qualquer ação
        self.store.save(
            {
                "state": self.state.export(),
                "world": self.world.export(),
                "decision": self.decision.export(),
            }
        )
