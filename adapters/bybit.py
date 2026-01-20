from pybit.unified_trading import HTTP


class BybitBroker:
    """
    Broker real em modo OBSERVADOR.
    Lê preços reais da Bybit, mas NÃO executa ordens.
    """

    def __init__(self, symbols: list[str]):
        self.symbols = symbols
        self.session = HTTP(testnet=False)

    def tick(self) -> dict:
        """
        Retorna:
        {
            "BTCUSDT": 43210.5,
            "ETHUSDT": 2310.2,
            ...
        }
        """
        feed = {}

        try:
            for symbol in self.symbols:
                r = self.session.get_tickers(category="spot", symbol=symbol)
                if r.get("retCode") != 0:
                    continue

                price = float(r["result"]["list"][0]["lastPrice"])
                feed[symbol] = price

        except Exception as e:
            print("⚠ Erro ao consultar Bybit:", e)

        return feed

    def buy(self, action):
        print(f"[OBSERVADOR] BUY ignorado: {action}")
        return True

    def sell(self, action):
        print(f"[OBSERVADOR] SELL ignorado: {action}")
        return True
