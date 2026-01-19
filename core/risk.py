from core.state_machine import State


class RiskManager:
    """
    Camada de proteção.
    Decide se uma ação é permitida.
    """

    def __init__(self, config: dict):
        self.config = config

    def allow(self, state: State, action: dict | None) -> bool:
        """
        Retorna True se a ação pode ser executada.
        """

        if action is None:
            return False

        kind = action["type"]

        # Nunca comprar se já estiver em posição
        if state == State.IN_POSITION and kind == "BUY":
            return False

        # Nunca vender se estiver ocioso
        if state == State.IDLE and kind == "SELL":
            return False

        return True

    def on_executed(self, action: dict):
        """
        Hook para futuras métricas:
        - contagem de trades
        - lucro diário
        - bloqueios
        """
        pass
