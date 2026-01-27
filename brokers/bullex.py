import time
import random

from brokers.bullex_api import BullexAPI


class BullexBroker:
    def __init__(self, symbols, mode="ASSISTED", account="DEMO", armed=False):
        self.symbols = symbols
        self.mode = mode
        self.api = BullexAPI(account=account)
        self.armed = armed

        self.contracts = []
        self.events = []

        # Estado cognitivo por símbolo
        self._world = {
            s: {
                "window": [],
                "pulse": 0,
                "micro_trend": 0,
                "macro_pos": 50.0,
                "zone": "middle",
                "last_price": None,
            }
            for s in symbols
        }

    # --------------------------------------------------
    # TRADUÇÃO COGNITIVA
    # --------------------------------------------------
    def _update_micro(self, bw, price):
        last = bw["last_price"]

        if last is None:
            bw["last_price"] = price
            return

        delta = price - last
        pulse = 1 if delta > 0 else -1

        bw["window"].append(pulse)
        if len(bw["window"]) > 6:
            bw["window"].pop(0)

        bw["pulse"] = pulse
        bw["micro_trend"] = sum(bw["window"])
        bw["last_price"] = price

    def _update_macro(self, bw):
        """
        Por enquanto ainda sintético.
        Depois virá do 4H real.
        """
        bw["macro_pos"] += random.uniform(-1.0, 1.0)
        bw["macro_pos"] = max(0, min(100, bw["macro_pos"]))

        if bw["macro_pos"] < 30:
            bw["zone"] = "bottom"
        elif bw["macro_pos"] > 70:
            bw["zone"] = "top"
        else:
            bw["zone"] = "middle"

    # --------------------------------------------------
    # TICK PRINCIPAL
    # --------------------------------------------------
    def tick(self):
        now = time.time()

        # --------------------------------------------------
        # 1. Resolve contratos expirados
        # --------------------------------------------------
        for c in self.contracts:
            if c.resolved:
                continue

            if now >= c.expiry_at:
                c.resolved = True
                c.result = random.choice(["WIN", "LOSS"])

                self.events.append(
                    {
                        "type": "binary_result",
                        "id": c.id,
                        "symbol": c.symbol,
                        "result": c.result,
                        "stake": c.stake,
                        "pattern": getattr(c, "pattern", None),
                        "zone": getattr(c, "zone", None),
                        "tempo": getattr(c, "tempo", None),
                    }
                )

        # --------------------------------------------------
        # 2. Gera mundo cognitivo
        # --------------------------------------------------
        feed = {}

        for symbol in self.symbols:
            bw = self._world[symbol]

            # Futuro real:
            # candle = self.api.get_last_candle(symbol, timeframe="5m")
            # price = candle["close"]

            # Simulação atual
            price = bw["last_price"] or random.uniform(1.0, 2.0)
            price += random.uniform(-0.001, 0.001)

            self._update_micro(bw, price)
            self._update_macro(bw)

            feed[symbol] = {
                "price": price,
                "binary": {
                    "pulse": bw["pulse"],
                    "window": list(bw["window"]),
                    "micro_trend": bw["micro_trend"],
                },
                "macro": {
                    "zone": bw["zone"],
                    "pos": round(bw["macro_pos"], 2),
                },
            }

        return feed

    # --------------------------------------------------
    # EXECUÇÃO BINÁRIA
    # --------------------------------------------------
    def buy(self, action):
        import uuid

        ok = self.api.place_demo_order(
            action["symbol"],
            action["side"],
            action["amount"],
            action.get("meta", {}).get("expiry", 60),
        )

        if not ok:
            return False

        contract = type("Contract", (), {})()
        contract.id = str(uuid.uuid4())
        contract.symbol = action["symbol"]
        contract.side = action["side"]
        contract.stake = action["amount"]
        contract.expiry_at = time.time() + action.get("meta", {}).get("expiry", 60)
        contract.resolved = False
        contract.result = None

        contract.pattern = action.get("meta", {}).get("pattern")
        ctx = action.get("meta", {}).get("context", {})
        contract.zone = ctx.get("zone")
        contract.tempo = ctx.get("tempo")

        self.contracts.append(contract)
        return True
