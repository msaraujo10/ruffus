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
    - alimentar a estratégia com histórico e diagnóstico (aprendizado contínuo)
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
        self.pending_action = None
        # Selo de confirmação humana (modo ASSISTED)
        self.human_confirmed = False

        self.state_handlers = {
            State.IDLE: self.handle_idle,
            State.ENTERING: self.handle_entering,
            State.AWAIT_CONFIRMATION: self.handle_await_confirmation,
            State.IN_POSITION: self.handle_in_position,
            State.EXITING: self.handle_exiting,
            State.POST_TRADE: self.handle_post_trade,
            State.ERROR: self.handle_error,
        }

    def handle_await_confirmation(self):
        # Estado passivo.
        # O sistema apenas aguarda uma decisão externa.
        pass

    def confirm(self):
        if self.state.current() == State.AWAIT_CONFIRMATION:
            self.state.set(State.ENTERING)

    def cancel(self):
        if self.state.current() == State.AWAIT_CONFIRMATION:
            self.pending_action = None
            self.state.set(State.IDLE)

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

        raw_state = data.get("state")
        if isinstance(raw_state, str):
            try:
                self.state.set(State[raw_state])
            except Exception:
                self.state.set(State.IDLE)

        world_data = data.get("world")
        if isinstance(world_data, dict):
            self.world.import_state(world_data)

        strat_data = data.get("strategy")
        if isinstance(strat_data, dict):
            self.strategy.import_state(strat_data)

        if isinstance(data, dict) and "mode" in data:
            self.mode = data["mode"]
            print(f"🧠 Modo restaurado: {self.mode}")
        else:
            self.mode = self.initial_mode
            print(f"🆕 Modo inicial aplicado: {self.mode}")

        if self.mode == "REAL":
            for symbol in self.world.symbols:
                pos = self.broker.get_open_position(symbol)
                if pos:
                    print(f"🔗 Posição real detectada em {symbol}. Sincronizando.")
                    self.strategy.on_sync(symbol, pos["entry_price"])
                    self.state.set(State.IN_POSITION)
                    self.persist()
                    return

        if self.state.current() == State.BOOT:
            self.state.set(State.IDLE)

        self.persist()

    # -------------------------------------------------
    # CICLO CANÔNICO
    # -------------------------------------------------
    def step(self, market_snapshot):
        self._global_ritual(market_snapshot)

        # Guardião REAL contínuo
        if self.mode == "REAL":
            if not self._reconcile_with_broker():
                # Qualquer divergência crítica congela o sistema
                self.set_mode("PAUSED")
                self.state.set(State.ERROR)
                self.persist()
                return

        handler = self.state_handlers.get(self.state.current())
        if handler:
            handler()

        self.persist()

    # -------------------------------------------------
    # RITUAL GLOBAL
    # -------------------------------------------------
    def _global_ritual(self, market_snapshot):
        if self.feedback:
            health = self.feedback.health()

            if health == "RISK_BLOCKED" and self.mode != "PAUSED":
                self.set_mode("PAUSED")

            elif health == "UNSTABLE" and self.mode == "REAL":
                self.set_mode("OBSERVADOR")

            elif health == "OK" and self.mode != self.initial_mode:
                self.set_mode(self.initial_mode)

        health = self.feedback.health() if self.feedback else "OK"

        if health == "UNSTABLE" and self.mode != "OBSERVADOR":
            print("🧠 [ENGINE] Sistema instável. Mudando para OBSERVADOR.")
            self.set_mode("OBSERVADOR")

        if hasattr(self.risk, "is_blocked") and self.risk.is_blocked():
            if self.mode != "PAUSED":
                print("🛑 [ENGINE] Risco bloqueado. Mudando para PAUSED.")
                self.set_mode("PAUSED")
                print(">>> GLOBAL_RITUAL | risk_blocked:", self.risk.is_blocked())

        self.world.update(market_snapshot)

        if self.feedback:
            diagnosis = self.feedback.diagnose()
            self.strategy.adapt(diagnosis)

    # -------------------------------------------------
    # CONTEXTO COGNITIVO
    # -------------------------------------------------
    def _build_context(self):
        return {
            "mode": self.mode,
            "health": self.feedback.health() if self.feedback else None,
            "profile": self.feedback.profile() if self.feedback else None,
            "last_action": self.feedback.last_action() if self.feedback else None,
        }

    # -------------------------------------------------
    # GUARDIÃO EXPLÍCITO
    # -------------------------------------------------
    def _preflight_real(self, kind: str, action: dict) -> bool:
        """
        Última barreira antes de tocar o mercado real.
        Retorna False se qualquer condição crítica falhar.
        """

        # 1. Estado ainda é coerente?
        if self.state.current() not in (State.ENTERING, State.EXITING):
            self.store.record_event(
                {
                    "type": "preflight_failed",
                    "reason": "INVALID_STATE",
                    "state": self.state.current().name,
                    "action": action,
                }
            )
            self.set_mode("PAUSED")
            return False

        # 2. Modo ainda é REAL?
        if self.mode != "REAL":
            self.store.record_event(
                {
                    "type": "preflight_failed",
                    "reason": "MODE_CHANGED",
                    "mode": self.mode,
                    "action": action,
                }
            )
            return False

        # 3. Risk ainda permite?
        if not self.risk.allow(self.state.current(), action):
            self.store.record_event(
                {
                    "type": "preflight_failed",
                    "reason": "RISK_REJECTED",
                    "action": action,
                }
            )
            self.set_mode("PAUSED")
            return False

        # 4. Broker responde?
        try:
            ok = self.broker.ping() if hasattr(self.broker, "ping") else True
        except Exception:
            ok = False

        if not ok:
            self.store.record_event(
                {
                    "type": "preflight_failed",
                    "reason": "BROKER_UNREACHABLE",
                    "action": action,
                }
            )
            self.set_mode("PAUSED")
            return False

        # 5. Coerência com a corretora
        # BUY → não pode haver posição aberta
        # SELL → deve haver posição aberta
        try:
            symbol = action.get("symbol")
            real_pos = self.broker.get_open_position(symbol)
        except Exception:
            real_pos = None

        if kind == "BUY" and real_pos:
            self.store.record_event(
                {
                    "type": "preflight_failed",
                    "reason": "REAL_POSITION_EXISTS",
                    "action": action,
                }
            )
            self.set_mode("PAUSED")
            return False

        if kind == "SELL" and not real_pos:
            self.store.record_event(
                {
                    "type": "preflight_failed",
                    "reason": "NO_REAL_POSITION",
                    "action": action,
                }
            )
            self.set_mode("PAUSED")
            return False

        return True

    # -------------------------------------------------
    # RECONCILIADOR REAL
    # -------------------------------------------------
    def _reconcile_with_broker(self) -> bool:
        """
        Verifica se o estado interno é coerente com a corretora.
        Retorna False em qualquer divergência crítica.
        """

        try:
            for symbol in self.world.symbols:
                real_pos = self.broker.get_open_position(symbol)
                internal_state = self.state.current()

                # Engine acha que está em posição, mas corretora não tem nada
                if internal_state == State.IN_POSITION and not real_pos:
                    self.store.record_event(
                        {
                            "type": "reconcile_failed",
                            "reason": "INTERNAL_IN_POSITION_BUT_NO_REAL",
                            "symbol": symbol,
                        }
                    )
                    return False

                # Corretora tem posição, mas Engine acha que está IDLE
                if internal_state == State.IDLE and real_pos:
                    self.store.record_event(
                        {
                            "type": "reconcile_failed",
                            "reason": "REAL_POSITION_BUT_INTERNAL_IDLE",
                            "symbol": symbol,
                            "price": real_pos.get("entry_price"),
                        }
                    )
                    return False

        except Exception as e:
            self.store.record_event(
                {
                    "type": "reconcile_failed",
                    "reason": "BROKER_EXCEPTION",
                    "error": str(e),
                }
            )
            return False

        return True

    # -------------------------------------------------
    # HANDLERS
    # -------------------------------------------------
    def handle_idle(self):
        world_view = self.world.snapshot()
        context = self._build_context()

        action = self.strategy.decide(State.IDLE, world_view, context)

        base_event = {
            "state": State.IDLE.name,
            "world": world_view,
            "action": action,
            "mode": self.mode,
        }

        if not action:
            self.store.record_event({**base_event, "result": "NO_ACTION"})
            self._learn_and_adapt()
            return

        if not self.risk.allow(State.IDLE, action):
            self.store.record_event({**base_event, "result": "BLOCKED_BY_RISK"})
            self._learn_and_adapt()
            return

        self.store.record_event({**base_event, "result": "APPROVED"})

        self.pending_action = action
        self.state.set(State.ENTERING)

    def handle_entering(self):
        print(
            ">>> HANDLE_ENTERING | mode:",
            self.mode,
            "| human_confirmed:",
            self.human_confirmed,
        )

        action = self.pending_action
        if not action:
            self.state.set(State.ERROR)
            return

        if self.mode == "ASSISTED" and not self.human_confirmed:
            self.state.set(State.AWAIT_CONFIRMATION)
            return

        # chegou aqui porque foi confirmado
        self.human_confirmed = False

        if self.mode == "REAL" or self.mode == "ASSISTED":
            if not self._preflight_real("BUY", action):
                self.state.set(State.ERROR)
                self.pending_action = None
                return

        ok = self.broker.buy(action)

        if ok:
            self.state.set(State.IN_POSITION)
            self.risk.on_executed(action)
        else:
            self.state.set(State.ERROR)

        self.pending_action = None

    def handle_in_position(self):
        world_view = self.world.snapshot()
        context = self._build_context()

        action = self.strategy.decide(State.IN_POSITION, world_view, context)

        if not action:
            return

        if not self.risk.allow(State.IN_POSITION, action):
            return

        if action["type"] == "SELL":
            self.pending_action = action
            self.state.set(State.EXITING)

    def handle_exiting(self):
        action = self.pending_action
        if not action:
            self.state.set(State.ERROR)
            return

        if self.mode == "REAL":
            if not self._preflight_real("SELL", action):
                self.state.set(State.ERROR)
                self.pending_action = None
                return

        ok = self.broker.sell(action)

        if ok:
            result = action.get("result") or action.get("reason")
            if result in ("PROFIT", "WIN"):
                self.risk.on_trade_result("WIN")
            else:
                self.risk.on_trade_result("LOSS")

            self.risk.on_executed(action)
            self.state.set(State.POST_TRADE)
        else:
            self.state.set(State.ERROR)

        self.pending_action = None

    def handle_post_trade(self):
        self._learn_and_adapt()
        self.state.set(State.IDLE)

    def handle_error(self):
        print("🔥 Engine em estado de erro. Sistema congelado.")

    # -------------------------------------------------
    # APRENDIZADO
    # -------------------------------------------------
    def _learn_and_adapt(self):
        if hasattr(self.store, "read_events"):
            events = self.store.read_events(limit=50)
            if events:
                self.strategy.learn(events)

        if self.feedback:
            diagnosis = self.feedback.diagnose()
            if diagnosis:
                self.strategy.adapt(diagnosis)

    # -------------------------------------------------
    # PERSISTÊNCIA
    # -------------------------------------------------
    def persist(self):
        snapshot = {
            "state": self.state.current().name,
            "world": self.world.export(),
            "strategy": self.strategy.export(),
            "mode": self.mode,
        }

        self.store.save(snapshot)

    # -------------------------------------------------
    # RENDERIZAR INFORMAÇÕES PARA O PAINEL
    # -------------------------------------------------
    def cognitive_snapshot(self) -> dict:
        return {
            "mode": self.mode,
            "state": self.state.current().name,
            "health": self.feedback.health() if self.feedback else None,
            "pending_action": self.pending_action,
            "world": self.world.snapshot(),
            "last_events": (
                self.store.read_events(limit=5)
                if hasattr(self.store, "read_events")
                else []
            ),
            "risk": {
                "blocked": (
                    self.risk.is_blocked() if hasattr(self.risk, "is_blocked") else None
                ),
            },
            "meta": {
                "engine": "Ruffus V2",
            },
        }
