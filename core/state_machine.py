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
    Máquina de estados por ativo.
    """

    def __init__(self):
        self._state = State.BOOT

    def current(self) -> State:
        return self._state

    def set(self, new_state: State):
        if not isinstance(new_state, State):
            raise ValueError("Estado inválido")

        print(f"🧠 {self._state.name} -> {new_state.name}")
        self._state = new_state

    def is_idle(self) -> bool:
        return self._state == State.IDLE

    def in_position(self) -> bool:
        return self._state == State.IN_POSITION
