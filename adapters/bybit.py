from pybit.unified_trading import HTTP


class BybitBroker:
    """
    Broker real da Bybit.

    Pode operar em dois modos:
    - OBSERVADOR: nunca envia ordens reais, apenas loga.
    - REAL: executa ordens reais na exchange.
    """

    def __init__(self, symbols, api_key=None, api_secret=None, mode="OBSERVADOR"):
        self.symbols = symbols
        self.mode = mode.upper()

        if self.mode not in ("OBSERVADOR", "REAL"):
            raise ValueError("BybitBroker: mode deve ser 'OBSERVADOR' ou 'REAL'")

        # Só inicializa sessão real se for REAL
        self.session = None
        if self.mode == "REAL":
            if not api_key or not api_secret:
                raise ValueError("API Key/Secret obrigatórios em modo REAL")

            self.session = HTTP(
                testnet=False,
                api_key=api_key,
                api_secret=api_secret,
                recv_window=10000,
            )

    # -------------------------------------------------
    # FEED DE MERCADO
    # -------------------------------------------------
    def tick(self) -> dict:
        """
        Retorna:
            { "BTCUSDT": 90481.0, "ETHUSDT": 3047.2, ... }
        """
        prices = {}

        if not self.session:
            # Em OBSERVADOR sem API ainda, não buscamos nada real
            return prices

        for s in self.symbols:
            r = self.session.get_tickers(category="spot", symbol=s)
            if r.get("retCode") == 0:
                price = float(r["result"]["list"][0]["lastPrice"])
                prices[s] = price

        return prices

    # -------------------------------------------------
    # COMPRA
    # -------------------------------------------------
    def buy(self, action: dict) -> bool:
        symbol = action["symbol"]
        price = action["price"]

        if self.mode == "OBSERVADOR":
            print(f"[OBSERVADOR] BUY ignorado: {action}")
            return False

        try:
            # Aqui depois entra cálculo real de quantidade, filtros etc.
            r = self.session.place_order(
                category="spot",
                symbol=symbol,
                side="Buy",
                orderType="Market",
                qty="0.001",  # placeholder seguro por enquanto
            )

            ok = r.get("retCode") == 0
            print(f"[REAL] BUY {symbol} @ {price} -> {'OK' if ok else 'ERRO'}")
            return ok

        except Exception as e:
            print(f"[REAL] Erro BUY {symbol}: {e}")
            return False

    # -------------------------------------------------
    # VENDA
    # -------------------------------------------------
    def sell(self, action: dict) -> bool:
        symbol = action["symbol"]
        price = action["price"]

        if self.mode == "OBSERVADOR":
            print(f"[OBSERVADOR] SELL ignorado: {action}")
            return False

        try:
            r = self.session.place_order(
                category="spot",
                symbol=symbol,
                side="Sell",
                orderType="Market",
                qty="0.001",  # placeholder seguro
            )

            ok = r.get("retCode") == 0
            print(f"[REAL] SELL {symbol} @ {price} -> {'OK' if ok else 'ERRO'}")
            return ok

        except Exception as e:
            print(f"[REAL] Erro SELL {symbol}: {e}")
            return False
