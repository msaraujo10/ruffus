class DecisionEngine:
    def __init__(self, config):
        self.config = config

    # Chamado quando o sistema está em IDLE
    def when_idle(self, world):
        """
        Retorna uma ação ou None.
        Exemplo de retorno:
        {
            "type": "BUY",
            "symbol": "BTCUSDT",
            "price": 43210.5
        }
        """

        # Por enquanto é apenas um esqueleto:
        # futuramente aqui entram:
        # - leitura de mercado
        # - filtros
        # - indicadores
        # - ranking de ativos

        return None

    # Chamado quando o sistema está em IN_TRADE
    def when_in_trade(self, world):
        """
        Retorna uma ação ou None.
        Exemplo de retorno:
        {
            "type": "SELL",
            "reason": "TAKE_PROFIT",
            "cooldown": 90
        }
        """

        # Aqui futuramente entram:
        # - cálculo de lucro
        # - stop
        # - trailing
        # - escudo

        return None
