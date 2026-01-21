from pybit.unified_trading import HTTP


class BybitBroker:
    """
    Broker real para Bybit.

    Modos:
    - OBSERVADOR: nunca executa ordens (apenas loga)
    - REAL: executa ordens reais

    Nunca lança exceção para fora.
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

        self._last_snapshot: dict = {}

    # -------------------------------------------------
    # MERCADO
    # -------------------------------------------------
    def tick(self) -> dict:
        """
        Retorna:
        {
            "BTCUSDT": 90481.0,
            "ETHUSDT": 3047.2,
            ...
        }

        Nunca lança exceção.
        Em falha, retorna último snapshot válido ou {}.
        """
        prices = {}

        try:
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

            self._last_snapshot = prices
            return prices

        except Exception:
            return self._last_snapshot or {}

    # -------------------------------------------------
    # POSIÇÕES
    # -------------------------------------------------
    def get_open_position(self, symbol: str) -> dict | None:
        """
        Retorna algo como:
        {
            "symbol": "BTCUSDT",
            "entry_price": 90481.2,
            "qty": 0.001
        }

        Ou None se não houver posição.
        """
        try:
            r = self.session.get_positions(category="spot", symbol=symbol)

            if r.get("retCode") != 0:
                return None

            positions = r["result"]["list"]
            for p in positions:
                size = float(p.get("size", 0))
                if size > 0:
                    return {
                        "symbol": symbol,
                        "entry_price": float(p.get("avgPrice", 0)),
                        "qty": size,
                    }

            return None

        except Exception:
            return None

    # -------------------------------------------------
    # EXECUÇÃO
    # -------------------------------------------------
    def buy(self, action: dict) -> bool:
        if self.mode == "OBSERVADOR" or not self.armed:
            print(f"[OBSERVADOR] BUY ignorado: {action}")
            return False

        try:
            # Aqui entrará a lógica real de ordem
            # (market, qty, etc.)
            return True
        except Exception:
            return False

    def sell(self, action: dict) -> bool:
        if self.mode == "OBSERVADOR" or not self.armed:
            print(f"[OBSERVADOR] SELL ignorado: {action}")
            return False

        try:
            # Lógica real de venda
            return True
        except Exception:
            return False
