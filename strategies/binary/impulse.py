from strategies.binary.base import BaseBinaryStrategy


class ImpulseBinary(BaseBinaryStrategy):
    name = "impulse-binary"

    def __init__(self, symbols, base_threshold=2, expiry=60):
        self.symbols = symbols
        self.base_threshold = base_threshold
        self.expiry = expiry

        # (pattern, zone, tempo) -> {win, loss, threshold}
        self.context_stats = {}

    def decide(self, state, world, context=None):
        if state.name != "IDLE":
            return None

        for symbol in self.symbols:
            data = world.get(symbol)
            if not data:
                continue

            binary = data.get("binary")
            macro = data.get("macro")

            if not binary or not macro:
                continue

            zone = macro.get("zone")
            micro_trend = binary.get("micro_trend", 0)
            window = binary.get("window", [])

            if len(window) < 4:
                continue

            tempo = "fast" if abs(micro_trend) >= 3 else "slow"

            # Fundo + impulso para cima → CALL
            if zone == "bottom" and micro_trend >= self._threshold(
                "bottom_impulse_up", zone, tempo
            ):
                return self._emit(
                    symbol=symbol,
                    side="BUY",
                    pattern="bottom_impulse_up",
                    zone=zone,
                    tempo=tempo,
                    micro_trend=micro_trend,
                    window=window,
                )

            # Topo + impulso para baixo → PUT
            if zone == "top" and micro_trend <= -self._threshold(
                "top_impulse_down", zone, tempo
            ):
                return self._emit(
                    symbol=symbol,
                    side="SELL",
                    pattern="top_impulse_down",
                    zone=zone,
                    tempo=tempo,
                    micro_trend=micro_trend,
                    window=window,
                )

        return None

    def _threshold(self, pattern, zone, tempo):
        key = (pattern, zone, tempo)
        ctx = self.context_stats.get(key)
        if not ctx:
            return self.base_threshold
        return ctx.get("threshold", self.base_threshold)

    def _emit(self, symbol, side, pattern, zone, tempo, micro_trend, window):
        return {
            "symbol": symbol,
            "side": side,
            "amount": 1.0,
            "meta": {
                "binary": True,
                "expiry": self.expiry,
                "pattern": pattern,
                "context": {
                    "zone": zone,
                    "tempo": tempo,
                },
                "reason": {
                    "zone": zone,
                    "tempo": tempo,
                    "micro_trend": micro_trend,
                    "window": list(window),
                    "threshold": self._threshold(pattern, zone, tempo),
                },
            },
        }

    def adapt(self, diagnosis):
        """
        Espera algo como:
        {
            "pattern": "...",
            "result": "WIN" | "LOSS",
            "zone": "...",
            "tempo": "fast" | "slow",
        }
        """
        pattern = diagnosis.get("pattern")
        result = diagnosis.get("result")
        zone = diagnosis.get("zone")
        tempo = diagnosis.get("tempo")

        if not all([pattern, result, zone, tempo]):
            return

        key = (pattern, zone, tempo)
        ctx = self.context_stats.setdefault(
            key,
            {"win": 0, "loss": 0, "threshold": self.base_threshold},
        )

        if result == "WIN":
            ctx["win"] += 1
        elif result == "LOSS":
            ctx["loss"] += 1

        total = ctx["win"] + ctx["loss"]
        if total >= 8:
            winrate = ctx["win"] / total

            # Ajuste local por contexto
            if winrate < 0.45:
                ctx["threshold"] = min(5, ctx["threshold"] + 1)
            elif winrate > 0.6:
                ctx["threshold"] = max(1, ctx["threshold"] - 1)

    def export(self):
        return {
            "base_threshold": self.base_threshold,
            "context_stats": self.context_stats,
        }

    def import_state(self, data):
        if not data:
            return
        self.base_threshold = data.get("base_threshold", self.base_threshold)
        self.context_stats = data.get("context_stats", self.context_stats)
