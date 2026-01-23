class BaseStrategy:
    """
    Contrato base para qualquer estratégia do RUFFUS.
    """

    def __init__(self, config: dict):
        self.config = config

    def decide(self, world: dict, state):
        """
        Recebe:
            world -> snapshot do mundo
            state -> estado atual do Engine

        Retorna:
            None
            ou
            {
                "type": "BUY" | "SELL",
                "symbol": str,
                "price": float,
                "reason": str,
            }
        """
        raise NotImplementedError

    def export(self) -> dict:
        """
        Retorna o estado interno da estratégia.
        """
        return {}

    def import_state(self, data: dict):
        """
        Restaura o estado interno da estratégia.
        """
        pass
