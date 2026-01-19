class World:
    """
    Representa o estado sincronizado do mercado.
    No futuro, unirá:
    - preços
    - volumes
    - candles
    - posição atual
    """

    def __init__(self, symbols: list[str]):
        self.symbols = symbols
        self.market = {s: {"price": None} for s in symbols}

    def update(self, feed: dict):
        """
        Recebe dados do broker e atualiza o mundo.
        Exemplo de feed:
        {
            "BTCUSDT": {"price": 64123.5},
            "ETHUSDT": {"price": 3120.4}
        }
        """
        for symbol, data in feed.items():
            if symbol in self.market:
                self.market[symbol].update(data)

    def snapshot(self) -> dict:
        """
        Retorna uma fotografia imutável do mundo atual.
        """
        return {symbol: data.copy() for symbol, data in self.market.items()}
