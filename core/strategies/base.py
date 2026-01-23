class BaseStrategy:
    """
    Contrato base para qualquer estratégia do RUFFUS.
    """

    def __init__(self, config: dict):
        self.config = config

    def decide(self, state, world, context):
        mode = context["mode"]
        health = context["health"]
        profile = context["profile"]

        # exemplo de uso:
        if mode == "PAUSED":
            return None

        if health == "RISK_BLOCKED":
            return None

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
