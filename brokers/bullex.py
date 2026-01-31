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

        # Mundo cognitivo por símbolo
        self._world = {
            s: {
                "window": [],
                "pulse": 0,
                "micro_trend": 0,
                "prev_trend": 0,
                "last_price": None,
                # Macro
                "macro_ref": None,
                "macro_pos": 50.0,
                "zone": "middle",
                # Tempo
                "last_5m_ts": None,
                "last_4h_ts": None,
            }
            for s in symbols
        }

    # --------------------------------------------------
    # MICRO (5M)
    # --------------------------------------------------
    def _update_micro(self, bw, price):
        last = bw["last_price"]

        if last is None:
            bw["last_price"] = price
            return

        bw["prev_trend"] = bw["micro_trend"]

        delta = price - last
        pulse = 1 if delta > 0 else -1

        bw["window"].append(pulse)
        if len(bw["window"]) > 6:
            bw["window"].pop(0)

        bw["pulse"] = pulse
        bw["micro_trend"] = sum(bw["window"])
        bw["last_price"] = price

    # --------------------------------------------------
    # MACRO (4H)
    # --------------------------------------------------
    def _update_macro(self, bw, symbol):
        candle = self.api.get_last_candle(symbol, timeframe="4h")
        price = candle["close"]

        ref = bw["macro_ref"]
        if ref is None:
            bw["macro_ref"] = price
            bw["macro_pos"] = 50.0
            bw["zone"] = "middle"
            return

        delta = price - ref
        bw["macro_pos"] += delta * 10
        bw["macro_pos"] = max(0, min(100, bw["macro_pos"]))
        bw["macro_ref"] = price

        if bw["macro_pos"] < 30:
            bw["zone"] = "bottom"
        elif bw["macro_pos"] > 70:
            bw["zone"] = "top"
        else:
            bw["zone"] = "middle"

    # --------------------------------------------------
    # TICK — TEMPO BINÁRIO SEMÂNTICO
    # --------------------------------------------------
    def tick(self):
        now = time.time()

        changed = False
        micro_updated = False
        macro_updated = False
        contract_resolved = False

        feed = {}

        # ----------------------------------------------
        # 1. Contratos expirados (EVENTO REAL)
        # ----------------------------------------------
        for c in self.contracts:
            if c.resolved:
                continue

            if now >= c.expiry_at:
                c.resolved = True
                c.result = random.choice(["WIN", "LOSS"])
                contract_resolved = True
                changed = True

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

        # ----------------------------------------------
        # 2. Candles (EVENTO REAL)
        # ----------------------------------------------
        for symbol in self.symbols:
            bw = self._world[symbol]

            # ----- 5M
            candle_5m = self.api.get_last_candle(symbol, timeframe="5m")
            ts5 = candle_5m["ts"]

            if bw["last_5m_ts"] != ts5:
                bw["last_5m_ts"] = ts5
                self._update_micro(bw, candle_5m["close"])
                micro_updated = True
                changed = True

            # ----- 4H
            candle_4h = self.api.get_last_candle(symbol, timeframe="4h")
            ts4 = candle_4h["ts"]

            if bw["last_4h_ts"] != ts4:
                bw["last_4h_ts"] = ts4
                self._update_macro(bw, symbol)
                macro_updated = True
                changed = True

            feed[symbol] = {
                "price": bw["last_price"],
                "binary": {
                    "pulse": bw["pulse"],
                    "window": list(bw["window"]),
                    "micro_trend": bw["micro_trend"],
                    "prev_trend": bw["prev_trend"],
                },
                "macro": {
                    "zone": bw["zone"],
                    "pos": round(bw["macro_pos"], 2),
                },
            }

        # ----------------------------------------------
        # 3. Sem evento → sem pensamento
        # ----------------------------------------------
        if not changed:
            return None

        # ----------------------------------------------
        # 4. Evento temporal semântico
        # ----------------------------------------------
        event_meta = {"time_event": []}

        if micro_updated:
            event_meta["time_event"].append("5M_CLOSED")

        if macro_updated:
            event_meta["time_event"].append("4H_CLOSED")

        if contract_resolved:
            event_meta["time_event"].append("CONTRACT_EXPIRED")

        feed["_event"] = event_meta

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
