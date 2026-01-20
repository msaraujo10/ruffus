from pybit.unified_trading import HTTP


class BybitBroker:
    """
    Broker real da Bybit.

    Modos:
    - OBSERVADOR: nunca executa ordens (apenas loga)
    - REAL: executa ordens apenas se armed == True
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
        Retorna preços reais da Bybit:
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
                else:
                    last = r["result"]["list"][0]["lastPrice"]
                    prices[symbol] = float(last)
            except Exception as e:
                print(f"[BYBIT] Erro ao buscar {symbol}: {e}")
                prices[symbol] = None

        return prices

    def buy(self, action: dict) -> bool:
        symbol = action["symbol"]
        price = action.get("price")

        if self.mode != "REAL" or not self.armed:
            print(f"[OBSERVADOR] BUY ignorado: {action}")
            return False

        print(f"🚨 [REAL BUY] {symbol} @ {price}")
        # Aqui futuramente entra a ordem real:
        # self.session.place_order(...)

        return True

    def sell(self, action: dict) -> bool:
        symbol = action["symbol"]
        price = action.get("price")

        if self.mode != "REAL" or not self.armed:
            print(f"[OBSERVADOR] SELL ignorado: {action}")
            return False

        print(f"🚨 [REAL SELL] {symbol} @ {price}")
        # self.session.place_order(...)

        return True
