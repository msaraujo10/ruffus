from enum import Enum, auto


class State(Enum):
    BOOT = auto()
    SYNC = auto()
    IDLE = auto()
    ENTERING = auto()
    IN_POSITION = auto()
    EXITING = auto()
    POST_TRADE = auto()
    ERROR = auto()


class StateMachine:
    """
    Máquina de estados do sistema.
    """

    def __init__(self):
        self._state = State.BOOT

    def current(self) -> State:
        return self._state

    def set(self, new_state: State):
        if not isinstance(new_state, State):
            raise ValueError("Estado inválido")

        print(f"🔁 STATE: {self._state.name} → {new_state.name}")
        self._state = new_state

    # ---------- Persistência ----------

    def export(self) -> dict:
        return {"state": self._state.name}

    def import_state(self, data: dict):
        if not data:
            return
        name = data.get("state")

        if name:
            self._state = State[name]
