from core.state_machine import State
from datetime import date
import time


class RiskManager:
    """
    Camada de proteção absoluta.
    O comportamento é definido pelo perfil/config.
    """

    def __init__(self, config: dict):
        self.config = config
        self.cooldown_until = 0

        self.today = date.today()
        self.trades_today = 0
        self.daily_pnl = 0.0

    def reset_if_new_day(self):
        if date.today() != self.today:
            self.today = date.today()
            self.trades_today = 0
            self.daily_pnl = 0.0

    def allow(self, state: State, action: dict) -> bool:
        # Blindagem absoluta
        if not self.config.get("armed", False):
            print("🛑 [RISK] Sistema desarmado.")
            return False

        if action is None:
            return False

        self.reset_if_new_day()

        now = time.time()

        # Cooldown ativo
        if now < self.cooldown_until:
            print("⏳ [RISK] Em cooldown.")
            return False

        kind = action["type"]

        # Limite de posições simultâneas
        max_pos = self.config.get("max_parallel_positions", 1)

        if kind == "BUY":
            open_positions = self.config.get("_open_positions", 0)
            if open_positions >= max_pos:
                print("🚫 [RISK] Limite de posições atingido.")
                return False

        # Regras estruturais do motor
        if state == State.IN_POSITION and kind == "BUY":
            return False

        if state == State.IDLE and kind == "SELL":
            return False

        # Limite diário de trades
        if self.trades_today >= self.config.get("max_daily_trades", 999):
            print("🛑 [RISK] Limite diário de trades atingido.")
            return False

        # Limite de perda diária
        if self.daily_pnl <= self.config.get("max_daily_loss", -999):
            print("🛑 [RISK] Limite de perda diária atingido.")
            return False

        return True

    def on_executed(self, action: dict):
        """
        Chamado após uma execução real ou virtual.
        Atualiza métricas de segurança.
        """
        self.trades_today += 1

        pnl = action.get("pnl")
        if pnl is not None:
            self.daily_pnl += pnl

    def on_trade_result(self, result: str):
        """
        Chamado pelo Engine após uma venda.
        """
        if result == "LOSS":
            cooldown = self.config.get("cooldown_after_loss", 0)
            if cooldown > 0:
                self.cooldown_until = time.time() + cooldown
