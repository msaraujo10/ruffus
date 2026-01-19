class World:
    """
    Representa a realidade observável do robô.
    Aqui vivem:
    - preço atual
    - símbolo atual
    - estado da posição
    - preço de entrada
    - preço máximo desde a entrada
    """

    def __init__(self, symbols: list[str]):
        self.symbols = symbols

        self.price = None
        self.symbol = None

        self.in_position = False
        self.entry_price = None
        self.max_price = None

    def update(self, feed: dict):
        """
        Atualiza o mundo a partir do broker.
        feed = {"price": float, "symbol": str}
        """
        self.price = feed["price"]
        self.symbol = feed["symbol"]

        if self.in_position:
            if self.max_price is None:
                self.max_price = self.price
            else:
                self.max_price = max(self.max_price, self.price)

    def on_buy(self, price: float):
        self.in_position = True
        self.entry_price = price
        self.max_price = price

    def on_sell(self):
        self.in_position = False
        self.entry_price = None
        self.max_price = None

    def snapshot(self) -> dict:
        """
        Visão atual do mundo para o cérebro.
        """
        return {
            "price": self.price,
            "symbol": self.symbol,
            "in_position": self.in_position,
            "entry_price": self.entry_price,
            "max_price": self.max_price,
        }
