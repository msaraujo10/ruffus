from pybit.unified_trading import HTTP


class BybitBroker:
    """
    Broker real com três modos:

    - OBSERVADOR: nunca executa ordens
    - REAL + armed=False: simula, mas bloqueia execução
    - REAL + armed=True: executa ordens reais (futuro)
    """

    def __init__(
        self, symbols: list[str], mode: str = "OBSERVADOR", armed: bool = False
    ):
        self.symbols = symbols
        self.mode = mode
        self.armed = armed

        self.session = HTTP(
            testnet=False,
            recv_window=10000,
        )

    def tick(self) -> dict:
        """
        Retorna:
        {
            "BTCUSDT": 90481.0,
            "ETHUSDT": 3047.2,
            ...
        }
        """
        prices = {}

        for symbol in self.symbols:
            try:
                r = self.session.get_tickers(category="spot", symbol=symbol)

                if r.get("retCode") != 0:
                    prices[symbol] = None
                    continue

                last = float(r["result"]["list"][0]["lastPrice"])
                prices[symbol] = last

            except Exception:
                prices[symbol] = None

        return prices

    # --------------------------
    # EXECUÇÃO CONTROLADA
    # --------------------------

    def buy(self, action: dict) -> bool:
        if self.mode == "OBSERVADOR" or not self.armed:
            print(f"[OBSERVADOR] BUY ignorado: {action}")
            return False

        # FUTURO: execução real aqui
        print(f"[REAL] BUY enviado: {action}")
        return True

    def sell(self, action: dict) -> bool:
        if self.mode == "OBSERVADOR" or not self.armed:
            print(f"[OBSERVADOR] SELL ignorado: {action}")
            return False

        # FUTURO: execução real aqui
        print(f"[REAL] SELL enviado: {action}")
        return True
