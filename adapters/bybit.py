from pybit.unified_trading import HTTP


class BybitBroker:
    def __init__(self, symbols, api_key=None, api_secret=None, testnet=False):
        self.symbols = symbols
        self.session = HTTP(
            testnet=testnet,
            api_key=api_key,
            api_secret=api_secret,
            recv_window=10000,
        )

    def tick(self) -> dict:
        """
        Retorna um snapshot de preços reais da Bybit no formato:
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
            print("⚠ Erro Bybit.tick:", e)

        return prices

    def buy(self, action: dict) -> bool:
        raise NotImplementedError

    def sell(self, action: dict) -> bool:
        raise NotImplementedError
