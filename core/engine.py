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

    def __init__(self, broker, world, decision, risk, store, mode: str):
        self.broker = broker
        self.world = world
        self.decision = decision
        self.risk = risk
        self.store = store
        self.mode = mode

        self.state = StateMachine()

    # -------------------------------------------------
    # BOOT
    # -------------------------------------------------
    def boot(self):
        print("🔄 Restaurando estado persistido.")

        data = self.store.load() or {}

        # Restaura componentes lógicos
        self.state.import_state(data.get("state"))
        self.world.import_state(data.get("world"))
        self.decision.import_state(data.get("decision"))

        # Sincronização REAL
        if self.mode == "REAL":
            for symbol in self.world.symbols:
                pos = self.broker.get_open_position(symbol)
                if pos:
                    print(f"🔗 Posição real detectada em {symbol}. Sincronizando.")
                    self.decision.entries[symbol] = pos["entry_price"]
                    self.state.set(State.IN_POSITION)
                    return

        # Caso normal
        if self.state.current() == State.BOOT:
            self.state.set(State.IDLE)

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

        try:
            if kind == "BUY":
                self.state.set(State.ENTERING)
                ok = self.broker.buy(action)

            elif kind == "SELL":
                self.state.set(State.EXITING)
                ok = self.broker.sell(action)

            else:
                return

            if ok:
                status = "EXECUTED"
                if kind == "BUY":
                    self.state.set(State.IN_POSITION)
                else:
                    self.state.set(State.POST_TRADE)
                    self.state.set(State.IDLE)
            else:
                status = "BLOCKED"
                self.state.set(State.ERROR)

        except Exception:
            status = "ERROR"
            self.state.set(State.ERROR)

        # Persistência obrigarória
        self.store.record_trade(
            action=action,
            status=status,
            mode=self.mode,  # VIRTUAL, OBSERVDOR ou REAL
        )

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
