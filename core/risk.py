from core.state_machine import State
from datetime import date


class RiskManager:
    """
    Camada de proteção absoluta.
    Nenhuma ação perigosa passa sem autorização explícita.
    """

    def __init__(self, config: dict):
        self.config = config

        self.today = date.today()
        self.trades_today = 0
        self.daily_pnl = 0.0

    def reset_if_new_day(self):
        if date.today() != self.today:
            self.today = date.today()
            self.trades_today = 0
            self.daily_pnl = 0.0

    def allow(self, state: State, action: dict | None) -> bool:
        self.reset_if_new_day()

        if action is None:
            return False

        kind = action["type"]

        # Nunca comprar se já estiver em posição
        if state == State.IN_POSITION and kind == "BUY":
            return False

        # Nunca vender se estiver ocioso
        if state == State.IDLE and kind == "SELL":
            return False

        # Blindagem absoluta
        if not self.config.get("armed", False):
            print("🛑 [RISK] Sistema desarmado. Ação bloqueada.")
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
