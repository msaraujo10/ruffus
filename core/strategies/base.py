class BaseStrategy:
    """
    Contrato base de toda estratégia.

    Toda estratégia deve:
    - decidir ações
    - aceitar adaptação cognitiva
    """

    def decide(self, state, world, context):
        """
        Retorna uma ação ou None.
        """
        raise NotImplementedError

    def adapt(self, diagnosis: dict):
        """
        Recebe o diagnóstico do sistema.

        Nesta fase:
        - não faz nada
        - apenas existe como contrato

        Fases futuras irão:
        - alterar parâmetros internos
        - mudar agressividade
        - pausar entradas
        """
        pass
