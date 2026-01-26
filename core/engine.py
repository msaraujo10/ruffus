import json
import os
from core.state_machine import State, StateMachine


class Engine:
    def __init__(self, broker, world, strategy, risk, store, feedback, mode: str):
        self.broker = broker
        self.world = world
        self.strategy = strategy
        self.risk = risk
        self.store = store
        self.feedback = feedback

        self.initial_mode = mode
        self.mode = mode
        self.identity = self.load_identity

        self.state = StateMachine()
        self.pending_action = None
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

    def load_identity(self):
        path = "storage/identity.json"
        if not os.path.exists(path):
            return None

        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    # -------------------------------------------------
    # BOOT
    # -------------------------------------------------
    def boot(self):
        print("🔄 Restaurando estado persistido.")

        data = self.store.load() or {}

        raw_state = data.get("state")
        if isinstance(raw_state, str):
            try:
                restored = State[raw_state]
                if restored not in (State.BOOT, State.ERROR):
                    self.state.set(restored)
            except Exception:
                self.state.set(State.IDLE)

        world_data = data.get("world")
        if isinstance(world_data, dict):
            self.world.import_state(world_data)

        strat_data = data.get("strategy")
        if isinstance(strat_data, dict):
            self.strategy.import_state(strat_data)

        if "mode" in data:
            self.mode = data["mode"]
            print(f"🧠 Modo restaurado: {self.mode}")
        else:
            self.mode = self.initial_mode
            print(f"🆕 Modo inicial aplicado: {self.mode}")

        if self.state.current() == State.BOOT:
            self.state.set(State.IDLE)

        self.persist()

    # -------------------------------------------------
    # CICLO
    # -------------------------------------------------
    def step(self, market_snapshot):
        if self.state.current() == State.ERROR:
            self.handle_error()
            return

        self._global_ritual(market_snapshot)

        handler = self.state_handlers.get(self.state.current())
        if handler:
            handler()

        self.persist()

    # -------------------------------------------------
    # RITUAL GLOBAL
    # -------------------------------------------------
    def _global_ritual(self, market_snapshot):
        self.world.update(market_snapshot)

        if self.feedback:
            diagnosis = self.feedback.diagnose()
            self.strategy.adapt(diagnosis)

    # -------------------------------------------------
    # CONTEXTO
    # -------------------------------------------------
    def _build_context(self):
        return {
            "mode": self.mode,
            "health": self.feedback.health() if self.feedback else None,
        }

    # -------------------------------------------------
    # HANDLERS
    # -------------------------------------------------
    def handle_idle(self):
        world_view = self.world.snapshot()
        context = self._build_context()

        action = self.strategy.decide(State.IDLE, world_view, context)
        if not action:
            return

        if not self.risk.allow(State.IDLE, action):
            return

        self.pending_action = action

        if self.mode == "ASSISTED":
            self.state.set(State.AWAIT_CONFIRMATION)
        else:
            self.state.set(State.ENTERING)

    def handle_entering(self):
        action = self.pending_action
        if not action:
            self.state.set(State.ERROR)
            return

        if self.mode == "ASSISTED" and not self.human_confirmed:
            self.state.set(State.AWAIT_CONFIRMATION)
            return

        self.human_confirmed = False

        ok = self.broker.buy(action)

        if ok:
            self.state.set(State.IN_POSITION)
            self.risk.on_executed(action)
        else:
            self.store.record_event({"type": "engine_error", "reason": "BUY_FAILED"})
            self.state.set(State.ERROR)

        self.pending_action = None

    def handle_await_confirmation(self):
        pass

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

        ok = self.broker.sell(action)

        if ok:
            self.state.set(State.POST_TRADE)
        else:
            self.store.record_event({"type": "engine_error", "reason": "SELL_FAILED"})
            self.state.set(State.ERROR)

        self.pending_action = None

    def handle_post_trade(self):
        self.state.set(State.IDLE)

    def handle_error(self):
        print("🔥 Engine em estado de erro. Sistema congelado.")

    # -------------------------------------------------
    # CONTROLE HUMANO
    # -------------------------------------------------
    def confirm(self):
        if self.state.current() == State.AWAIT_CONFIRMATION:
            self.store.record_event(
                {
                    "type": "human_confirm",
                    "state": self.state.current().name,
                    "mode": self.mode,
                    "action": self.pending_action,
                }
            )
            self.human_confirmed = True
            self.state.set(State.ENTERING)

    def cancel(self, reason: str | None = None):
        if self.state.current() == State.AWAIT_CONFIRMATION:
            self.store.record_event(
                {
                    "type": "human_cancel",
                    "state": self.state.current().name,
                    "mode": self.mode,
                    "action": self.pending_action,
                    "human_reason": reason,
                }
            )

            self.pending_action = None
            self.human_confirmed = False
            self.state.set(State.IDLE)

    def override_regime(self, regime: str):
        self.store.record_event(
            {
                "type": "human_override_regime",
                "mode": self.mode,
                "regime": regime,
            }
        )

        if hasattr(self.strategy, "regime"):
            self.strategy.regime = regime.upper()

    # -------------------------------------------------
    # SNAPSHOT
    # -------------------------------------------------
    def cognitive_snapshot(self) -> dict:
        intent = None
        if self.pending_action:
            intent = {
                "type": self.pending_action.get("type"),
                "symbol": self.pending_action.get("symbol"),
                "price": self.pending_action.get("price"),
                "reason": self.pending_action.get("reason"),
            }

        regime = getattr(self.strategy, "regime", None)

        diagnosis = self.feedback.diagnose() if self.feedback else {}
        human_profile = diagnosis.get("signals", [])
        identity = self.identity or {}

        return {
            "mode": self.mode,
            "identity": identity,
            "state": self.state.current().name,
            "health": self.feedback.health() if self.feedback else None,
            "regime": regime,
            "human_profile": human_profile,
            "intent": intent,
            "awaiting_human": self.state.current() == State.AWAIT_CONFIRMATION,
            "last_events": (
                self.store.read_events(limit=5)
                if hasattr(self.store, "read_events")
                else []
            ),
        }

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
