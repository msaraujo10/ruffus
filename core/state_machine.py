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
    Controla o estado do robô.
    Nenhuma ação acontece fora de um estado válido.
    """

    def __init__(self):
        self._state = State.BOOT

    def current(self) -> State:
        return self._state

    def set(self, new_state: State):
        if not isinstance(new_state, State):
            raise ValueError("Estado inválido")

        # Log simples e explícito
        print(f"🔁 STATE: {self._state.name} → {new_state.name}")
        self._state = new_state

    def is_idle(self) -> bool:
        return self._state == State.IDLE

    def in_position(self) -> bool:
        return self._state == State.IN_POSITION

    def is_transitioning(self) -> bool:
        return self._state in (State.ENTERING, State.EXITING)

    def is_error(self) -> bool:
        return self._state == State.ERROR
