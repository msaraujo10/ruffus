from core.state_machine import State, StateMachine


class Engine:
    """
    Orquestrador central do sistema.
    """

    def __init__(self, broker, world, decision, risk, store, feedback, mode: str):
        self.broker = broker
        self.world = world
        self.decision = decision
        self.risk = risk
        self.store = store
        self.feedback = feedback
        self.mode = mode

        self.state = StateMachine()

    # -------------------------------------------------
    # BOOT
    # -------------------------------------------------
    def boot(self):
        print("🔄 Restaurando estado persistido.")

        data = self.store.load() or {}

        self.state.import_state(data.get("state"))
        self.world.import_state(data.get("world"))
        self.decision.import_state(data.get("decision"))

        if self.state.current() == State.BOOT:
            self.state.set(State.IDLE)

    # -------------------------------------------------
    # CICLO PRINCIPAL
    # -------------------------------------------------
    def tick(self, market_snapshot: dict):
        current = self.state.current()

        self.world.update(market_snapshot)
        world_view = self.world.snapshot()

        action = self.decision.decide(current, world_view)

        # Feedback passivo
        self.feedback.observe(
            state=current.name,
            world=world_view,
            action=action,
        )

        if not action:
            return

        if not self.risk.allow(current, action):
            return

        self.execute(action)

    # -------------------------------------------------
    # EXECUÇÃO
    # -------------------------------------------------
    def execute(self, action: dict):
        kind = action["type"]

        try:
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

        except Exception:
            self.state.set(State.ERROR)

        self.persist()

    # -------------------------------------------------
    # PERSISTÊNCIA
    # -------------------------------------------------
    def persist(self):
        snapshot = {
            "state": self.state.current().name,
            "world": self.world.export(),
            "decision": self.decision.export(),
        }

        self.store.save(snapshot)
