from core.state_machine import State, StateMachine
from datetime import datetime


class Engine:
    """
    Orquestrador central do sistema.

    Responsabilidades:
    - coordenar StateMachine, World, DecisionEngine e RiskManager
    - restaurar o estado persistido no boot
    - executar ações aprovadas
    - registrar eventos e trades
    - persistir snapshots consistentes
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

        snapshot = self.store.load()

        if snapshot:
            print("🔄 Estado encontrado. Restaurando...")

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

        # Sincronização REAL
        if self.mode == "REAL":
            for symbol in self.world.symbols:
                pos = self.broker.get_open_position(symbol)
                if pos:
                    print(f"🔗 Posição real detectada em {symbol}. Sincronizando.")
                    self.decision.entries[symbol] = pos["entry_price"]
                    self.state.set(State.IN_POSITION)
                    return

        # Caso ainda esteja em BOOT
        if self.state.current() == State.BOOT:
            self.state.set(State.IDLE)

    # -------------------------------------------------
    # CICLO PRINCIPAL
    # -------------------------------------------------
    def tick(self, market_snapshot: dict):
        current = self.state.current()

        # Atualiza o mundo
        self.world.update(market_snapshot)
        world_view = self.world.snapshot()
        action = self.decision.decide(current, world_view)

        base_event = {
            "ts": datetime.utcnow().isoformat(),
            "mode": self.mode,
            "state": current.name,
            "world": world_view,
            "action": action,
        }

        if not action:
            self.store.record_event({**base_event, "result": "NO_ACTION"})
            return

        if not self.risk.allow(current, action):
            self.store.record_event({**base_event, "result": "BLOCKED_BY_RISK"})
            return

        # Ação aprovada
        self.store.record_event({**base_event, "result": "APPROVED"})

        self.execute(action)

    # -------------------------------------------------
    # EXECUÇÃO
    # -------------------------------------------------
    def execute(self, action: dict):
        kind = action["type"]
        status = "UNKNOWN"

        try:
            if kind == "BUY":
                self.state.set(State.ENTERING)
                ok = self.broker.buy(action)
                if ok:
                    self.state.set(State.IN_POSITION)
                    status = "EXECUTED"
                else:
                    if self.mode == "OBSERVADOR":
                        print("[OBSERVADOR] BUY ignorado.")
                        self.state.set(State.IDLE)
                        status = "IGNORED"
                    else:
                        self.state.set(State.ERROR)
                        status = "FAILED"

            elif kind == "SELL":
                self.state.set(State.EXITING)
                ok = self.broker.sell(action)
                if ok:
                    self.state.set(State.POST_TRADE)
                    self.state.set(State.IDLE)
                    status = "EXECUTED"
                else:
                    if self.mode == "OBSERVADOR":
                        print("[OBSERVADOR] SELL ignorado.")
                        self.state.set(State.IN_POSITION)
                        status = "IGNORED"
                    else:
                        self.state.set(State.ERROR)
                        status = "FAILED"

        except Exception:
            status = "ERROR"
            self.state.set(State.ERROR)

        # Registro financeiro (apenas uma vez por ação real)
        self.store.record_trade(
            action=action,
            status=status,
            mode=self.mode,
            state=self.state.current().name,
        )

        # Persistência obrigatória após mutação real
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
