class BaseStrategy:
    """
    Contrato base de toda estratégia.

    Toda estratégia deve:
    - decidir ações
    - aceitar adaptação cognitiva
    - ser serializável
    - ser restaurável
    - tolerar aprendizado histórico
    """

    def decide(self, state, world, context):
        """
        Retorna uma ação (dict) ou None.
        """
        raise NotImplementedError

    def adapt(self, diagnosis: dict):
        """
        Recebe o diagnóstico do sistema.

        Nesta fase:
        - não faz nada
        - apenas existe como contrato

        Fases futuras poderão:
        - alterar parâmetros internos
        - mudar agressividade
        - pausar entradas
        """
        pass

    def learn(self, events: list):
        """
        Recebe eventos recentes para aprendizado.

        Estratégias simples podem ignorar.
        Estratégias evolutivas podem usar.
        """
        pass

    def export(self) -> dict:
        """
        Retorna o estado interno serializável da estratégia.
        Estratégias sem memória podem retornar {}.
        """
        return {}

    def import_state(self, data: dict):
        """
        Restaura o estado interno da estratégia.
        Estratégias sem memória podem ignorar.
        """
        pass
