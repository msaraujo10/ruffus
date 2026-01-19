class World:
    """
    Representa o mundo sincronizado.
    Mantém o estado de múltiplos símbolos.
    """

    def __init__(self, symbols: list[str]):
        self.symbols = symbols
        self.prices: dict[str, float] = {}

    def update(self, feed: dict):
        """
        Recebe um feed do broker:
        {
            "BTCUSDT": 43210.5,
            "ETHUSDT": 2345.1,
            ...
        }
        """
        for symbol, price in feed.items():
            self.prices[symbol] = price

    def snapshot(self) -> dict:
        """
        Retorna o estado atual do mundo.
        """
        return {
            "prices": dict(self.prices),
        }
