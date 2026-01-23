# core/engine.py

from core.state_machine import State, StateMachine


class Engine:
    """
    Orquestrador central do sistema.

    Responsabilidades:
    - coordenar StateMachine, World, Strategy e RiskManager
    - restaurar o estado persistido no boot
    - executar ações aprovadas
    - persistir snapshots consistentes após cada mutação
    - manter e controlar o modo global (VIRTUAL / OBSERVADOR / REAL / PAUSED)
    - propagar diagnósticos cognitivos para a estratégia
    """

    def __init__(self, broker, world, strategy, risk, store, feedback, mode: str):
        self.broker = broker
        self.world = world
        self.strategy = strategy
        self.risk = risk
        self.store = store
        self.feedback = feedback

        self.initial_mode = mode
        self.mode = mode

        self.state = StateMachine()

    # -------------------------------------------------
    # CONTROLE DE MODO
    # -------------------------------------------------
    def set_mode(self, mode: str):
        self.mode = mode
        print(f"🧠 Modo alterado para: {self.mode}")
        self.persist()

    # -------------------------------------------------
    # BOOT
    # -------------------------------------------------
    def boot(self):
        print("🔄 Restaurando estado persistido.")

        data = self.store.load() or {}

        # Restaura State
        raw_state = data.get("state")
        if isinstance(raw_state, str):
            try:
                self.state.set(State[raw_state])
            except Exception:
                self.state.set(State.IDLE)

        # Restaura World
        world_data = data.get("world")
        if isinstance(world_data, dict):
            self.world.import_state(world_data)

        # Restaura Strategy
        strategy_data = data.get("strategy")
        if isinstance(strategy_data, dict):
            self.strategy.import_state(strategy_data)

        # Restaura modo
        if "mode" in data:
            self.mode = data["mode"]
            print(f"🧠 Modo restaurado: {self.mode}")
        else:
            self.mode = self.initial_mode
            print(f"🆕 Modo inicial aplicado: {self.mode}")

        # Sincronização REAL
        if self.mode == "REAL":
            for symbol in self.world.symbols:
                pos = self.broker.get_open_position(symbol)
                if pos:
                    print(f"🔗 Posição real detectada em {symbol}. Sincronizando.")
                    self.strategy.restore_position(symbol, pos)
                    self.state.set(State.IN_POSITION)
                    self.persist()
                    return

        if self.state.current() == State.BOOT:
            self.state.set(State.IDLE)

        self.persist()

    # -------------------------------------------------
    # CICLO PRINCIPAL
    # -------------------------------------------------
    def tick(self, market_snapshot: dict):
        current = self.state.current()

        # Atualiza o mundo
        self.world.update(market_snapshot)

        world_view = self.world.snapshot()

        context = {
            "mode": self.mode,
            "health": self.feedback.health() if self.feedback else None,
            "profile": self.feedback.profile() if self.feedback else None,
            "last_action": self.feedback.last_action() if self.feedback else None,
        }

        action = self.strategy.decide(current, world_view, context)

        base_event = {
            "state": current.name,
            "world": world_view,
            "action": action,
            "mode": self.mode,
        }

        if not action:
            self.store.record_event({**base_event, "result": "NO_ACTION"})
            return

        if not self.risk.allow(current, action):
            self.store.record_event({**base_event, "result": "BLOCKED_BY_RISK"})
            return

        self.store.record_event({**base_event, "result": "APPROVED"})

        # Regra global
        if current == State.IN_POSITION and action["type"] == "BUY":
            print("⛔ BUY bloqueado: já existe posição aberta.")
            return

        self.execute(action)

        # ------------------------------
        # DIAGNÓSTICO + ADAPTAÇÃO
        # ------------------------------
        if self.feedback:
            diagnosis = self.feedback.diagnose()
            if diagnosis:
                self.strategy.adapt(diagnosis)

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
                    self.state.set(State.ERROR)
                    status = "FAILED"
                self.persist()

            elif kind == "SELL":
                self.state.set(State.EXITING)
                ok = self.broker.sell(action)
                if ok:
                    self.state.set(State.POST_TRADE)
                    self.state.set(State.IDLE)
                    status = "EXECUTED"
                else:
                    self.state.set(State.ERROR)
                    status = "FAILED"
                self.persist()

        except Exception:
            status = "ERROR"
            self.state.set(State.ERROR)

        self.store.record_trade(
            {
                "action": action,
                "status": status,
                "mode": self.mode,
                "state": self.state.current().name,
            }
        )

        self.persist()

    # -------------------------------------------------
    # PERSISTÊNCIA CENTRAL
    # -------------------------------------------------
    def persist(self):
        snapshot = {
            "state": self.state.current().name,
            "world": self.world.export(),
            "strategy": self.strategy.export(),
            "mode": self.mode,
        }

        self.store.save(snapshot)
