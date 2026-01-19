class World:
    """
    Representa o mundo observado pelo robô.
    Guarda o estado atual de cada símbolo.
    """

    def __init__(self, symbols: list[str]):
        self.symbols = symbols
        self.state = {s: {"price": None} for s in symbols}

    def update(self, feed):
        """
        Recebe dados brutos do broker.
        No modo virtual atual, `feed` é apenas um float.
        """
        # Por enquanto só temos 1 símbolo virtual
        symbol = self.symbols[0]
        self.state[symbol]["price"] = feed

    def snapshot(self) -> dict:
        """
        Retorna uma cópia do mundo para decisão.
        """
        return {k: v.copy() for k, v in self.state.items()}
