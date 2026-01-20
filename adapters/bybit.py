from pybit.unified_trading import HTTP


class BybitObserver:
    """
    Observador passivo da Bybit.
    Não compra, não vende.
    Apenas retorna preços reais no formato esperado pelo World.
    """

    def __init__(self, symbols, api_key, api_secret, testnet=False):
        self.symbols = symbols

        self.session = HTTP(
            testnet=testnet,
            api_key=api_key,
            api_secret=api_secret,
            recv_window=10000,
        )

    def tick(self) -> dict:
        """
        Retorna algo como:
        {
            "BTCUSDT": 43210.5,
            "ETHUSDT": 2310.2,
            ...
        }
        """
        prices = {}

        try:
            r = self.session.get_tickers(category="spot")

            if r.get("retCode") != 0:
                return prices

            for item in r["result"]["list"]:
                symbol = item["symbol"]
                if symbol in self.symbols:
                    prices[symbol] = float(item["lastPrice"])

        except Exception as e:
            print(f"⚠ Erro ao ler preços da Bybit: {e}")

        return prices
