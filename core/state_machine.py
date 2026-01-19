from enum import Enum, auto
from dataclasses import dataclass
from datetime import datetime, timedelta


class State(Enum):
    IDLE = auto()
    IN_TRADE = auto()
    COOLDOWN = auto()
    ERROR = auto()


@dataclass
class World:
    symbol: str | None = None
    entry_price: float | None = None
    last_price: float | None = None
    last_action: str | None = None
    cooldown_until: datetime | None = None


class StateMachine:
    def __init__(self):
        self.state = State.IDLE
        self.world = World()

    # ------------------------
    # TRANSIÇÕES DE ESTADO
    # ------------------------

    def enter_idle(self):
        self.state = State.IDLE
        self.world.symbol = None
        self.world.entry_price = None
        self.world.last_action = "IDLE"

    def enter_trade(self, symbol: str, entry_price: float):
        self.state = State.IN_TRADE
        self.world.symbol = symbol
        self.world.entry_price = entry_price
        self.world.last_action = "BUY"

    def enter_cooldown(self, minutes: int):
        self.state = State.COOLDOWN
        self.world.cooldown_until = datetime.now() + timedelta(minutes=minutes)
        self.world.last_action = "COOLDOWN"

    def enter_error(self, reason: str):
        self.state = State.ERROR
        self.world.last_action = f"ERROR: {reason}"

    # ------------------------
    # CONSULTAS
    # ------------------------

    def is_idle(self) -> bool:
        return self.state == State.IDLE

    def is_in_trade(self) -> bool:
        return self.state == State.IN_TRADE

    def is_in_cooldown(self) -> bool:
        return self.state == State.COOLDOWN

    def is_error(self) -> bool:
        return self.state == State.ERROR

    def cooldown_expired(self) -> bool:
        if not self.world.cooldown_until:
            return True
        return datetime.now() >= self.world.cooldown_until
