from core.state_machine import State, StateMachine


class Engine:
    """
    Orquestrador central do sistema.

    Responsabilidades:
    - coordenar StateMachine, World, DecisionEngine e RiskManager
    - restaurar o estado persistido no boot
    - executar ações aprovadas
    - persistir snapshots consistentes após cada mutação
    """

    def __init__(self, broker, world, decision, risk, store):
        self.broker = broker
        self.world = world
        self.decision = decision
        self.risk = risk
        self.store = store

        self.state = StateMachine()

    # -------------------------------------------------
    # BOOT
    # -------------------------------------------------
    def boot(self):
        """
        Inicializa o sistema.

        - tenta carregar snapshot persistido
        - restaura todos os módulos
        - se não houver snapshot, inicia limpo
        """

        snapshot = self.store.load()

        if snapshot:
            print("🔄 Restaurando estado persistido...")

            # State
            state_name = snapshot.get("state")
            if state_name:
                self.state.set(State[state_name])

            # World
            if "world" in snapshot:
                self.world.import_state(snapshot["world"])

            # Decision
            if "decision" in snapshot:
                self.decision.import_state(snapshot["decision"])

        else:
            print("🆕 Nenhum estado encontrado. Inicialização limpa.")
            self.state.set(State.IDLE)
            self.persist()

    # -------------------------------------------------
    # CICLO PRINCIPAL
    # -------------------------------------------------
    def tick(self, market_snapshot: dict):
        """
        Um ciclo completo do robô.
        """

        # Atualiza o mundo
        self.world.update(market_snapshot)

        current_state = self.state.current()
        world_view = self.world.snapshot()

        action = self.decision.decide(current_state, world_view)

        if not action:
            return

        if not self.risk.allow(current_state, action):
            return

        self.execute(action)

    # -------------------------------------------------
    # EXECUÇÃO
    # -------------------------------------------------
    def execute(self, action: dict):
        kind = action["type"]

        if kind == "BUY":
            self.state.set(State.ENTERING)
            ok = self.broker.buy(action)

            if ok:
                self.state.set(State.IN_POSITION)
                self.persist()
            else:
                self.state.set(State.ERROR)
                self.persist()

        elif kind == "SELL":
            self.state.set(State.EXITING)
            ok = self.broker.sell(action)

            if ok:
                self.state.set(State.POST_TRADE)
                self.state.set(State.IDLE)
                self.persist()
            else:
                self.state.set(State.ERROR)
                self.persist()

    # -------------------------------------------------
    # PERSISTÊNCIA CENTRAL
    # -------------------------------------------------
    def persist(self):
        """
        Salva um snapshot consistente de todo o sistema.
        """

        snapshot = {
            "state": self.state.current().name,
            "world": self.world.export(),
            "decision": self.decision.export(),
        }

        self.store.save(snapshot)
