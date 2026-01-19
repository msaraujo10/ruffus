from datetime import datetime, timedelta


class RiskManager:
    def __init__(self, config):
        self.config = config
        self.cooldown_until = None
        self.stop_loss = config["stop_loss"]
        self.take_profit = config["take_profit"]

    def in_cooldown(self):
        if not self.cooldown_until:
            return False
        return datetime.utcnow() < self.cooldown_until

    def start_cooldown(self, seconds):
        self.cooldown_until = datetime.utcnow() + timedelta(seconds=seconds)

    def allow(self, state, action):
        """
        Decide se uma ação pode ser executada.
        Retorna True ou False.
        """

        # Nunca faz nada em cooldown
        if self.in_cooldown():
            return False

        if action is None:
            return False

        # Regras por estado
        if state == "IDLE":
            if action["type"] == "BUY":
                return True

        if state == "IN_TRADE":
            if action["type"] == "SELL":
                return True

        return False

    def on_executed(self, action):
        """
        Chamado após uma ação real ser executada.
        Usado para iniciar cooldowns, etc.
        """
        if action["type"] == "SELL":
            cooldown = action.get("cooldown", 0)
            if cooldown > 0:
                self.start_cooldown(cooldown)
