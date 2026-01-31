# strategies/binary/impulse.py

import time
from strategies.binary.base import BaseBinaryStrategy


class ImpulseBinary(BaseBinaryStrategy):
    name = "impulse-binary"

    def __init__(self, symbols, base_threshold=2, expiry=60):
        self.symbols = symbols
        self.base_threshold = base_threshold
        self.expiry = expiry

        # Aprendizado
        self.context_stats = {}  # (pattern, zone, tempo) -> stats
        self.by_symbol = {}  # symbol -> {win, loss}

        # Eventos temporais
        self.last_event_ts = None
        self.last_event_type = None

        self.windows = {
            "5M_CLOSED": 40,
            "4H_CLOSED": 180,
        }

        # Saturação / cooldown
        self.last_decision = None  # (symbol, pattern, event)
        self.last_decision_ts = None
        self.cooldown = 120
        self.symbol_cooldown = {}

        # Convicção progressiva
        self.conviction = {}  # (symbol, pattern) -> score
        self.conviction_threshold = 2

        # Metacognição
        self.min_quality = 3

        # Metamemória
        self.quality_memory = []  # [(quality, result)]
        self.quality_memory_limit = 20

    # ==================================================
    # AUXILIARES COGNITIVOS
    # ==================================================

    def _market_rhythm(self, window):
        energy = sum(abs(x) for x in window)
        if energy >= 5:
            return "FAST"
        if energy <= 2:
            return "SLOW"
        return "NORMAL"

    def _dissonance(self, zone, micro_trend):
        if zone == "top" and micro_trend > 0:
            return "STRONG"
        if zone == "bottom" and micro_trend < 0:
            return "STRONG"
        if zone == "middle":
            return "MODERATE"
        return "NONE"

    def _decision_quality(self, rhythm, dissonance, conviction, energy):
        score = 0

        if rhythm == "FAST":
            score += 2
        elif rhythm == "NORMAL":
            score += 1

        if dissonance == "NONE":
            score += 2
        elif dissonance == "MODERATE":
            score += 1

        if conviction >= self.conviction_threshold:
            score += 1

        if energy >= 5:
            score += 1

        return score

    def _threshold(self, pattern, zone, tempo):
        key = (pattern, zone, tempo)
        ctx = self.context_stats.get(key)
        return ctx.get("threshold", self.base_threshold) if ctx else self.base_threshold

    def symbol_bias(self, symbol):
        rec = self.by_symbol.get(symbol)
        if not rec:
            return 0

        total = rec["win"] + rec["loss"]
        if total < 5:
            return 0

        rate = rec["win"] / total
        if rate > 0.65:
            return -1
        if rate < 0.35:
            return 1
        return 0

    # ==================================================
    # DECIDE
    # ==================================================

    def decide(self, state, world, context=None):
        now = time.time()

        # Eventos temporais
        event = world.get("_event", {})
        events = event.get("time_event", [])

        if events:
            if "4H_CLOSED" in events:
                self.last_event_type = "4H_CLOSED"
            elif "5M_CLOSED" in events:
                self.last_event_type = "5M_CLOSED"
            self.last_event_ts = now

        if not self.last_event_type or not self.last_event_ts:
            return None

        window_limit = self.windows.get(self.last_event_type, 0)
        if now - self.last_event_ts > window_limit:
            return None

        # Saturação global
        if self.last_decision and self.last_decision_ts:
            if (
                self.last_decision[2] == self.last_event_type
                and now - self.last_decision_ts < window_limit
            ):
                return None

        if state.name != "IDLE":
            return None

        for symbol in self.symbols:
            # Cooldown por símbolo
            last_ts = self.symbol_cooldown.get(symbol)
            if last_ts and now - last_ts < self.cooldown:
                continue

            data = world.get(symbol)
            if not data:
                continue

            binary = data.get("binary")
            macro = data.get("macro")
            if not binary or not macro:
                continue

            zone = macro.get("zone")
            window = binary.get("window", [])
            micro_trend = binary.get("micro_trend", 0)
            prev_trend = binary.get("prev_trend", 0)

            if len(window) < 4:
                continue

            energy = sum(abs(x) for x in window)
            if energy < 4:
                continue

            dissonance = self._dissonance(zone, micro_trend)
            if dissonance == "STRONG":
                self.conviction[(symbol, "bottom_reversal")] = 0
                self.conviction[(symbol, "top_reversal")] = 0
                continue

            dissonance_penalty = 1 if dissonance == "MODERATE" else 0
            rhythm = self._market_rhythm(window)
            rhythm_penalty = 1 if rhythm == "SLOW" else 0
            tempo = "fast" if abs(micro_trend) >= 3 else "slow"

            # ---------------- BUY ----------------
            pattern = "bottom_reversal"
            base = self._threshold(pattern, zone, tempo)
            bias = self.symbol_bias(symbol)
            effective = base + bias + rhythm_penalty + dissonance_penalty

            if zone == "bottom" and prev_trend < 0 and micro_trend >= effective:
                key = (symbol, pattern)
                self.conviction[key] = self.conviction.get(key, 0) + 1

                if self.conviction[key] >= self.conviction_threshold:
                    quality = self._decision_quality(
                        rhythm, dissonance, self.conviction[key], energy
                    )

                    if quality < self.min_quality:
                        continue

                    return self._emit(
                        symbol,
                        "BUY",
                        pattern,
                        zone,
                        tempo,
                        micro_trend,
                        window,
                        rhythm,
                        dissonance,
                        now,
                        quality,
                    )
            else:
                self.conviction[(symbol, pattern)] = 0

            # ---------------- SELL ----------------
            pattern = "top_reversal"
            base = self._threshold(pattern, zone, tempo)
            bias = self.symbol_bias(symbol)
            effective = base + bias + rhythm_penalty + dissonance_penalty

            if zone == "top" and prev_trend > 0 and micro_trend <= -effective:
                key = (symbol, pattern)
                self.conviction[key] = self.conviction.get(key, 0) + 1

                if self.conviction[key] >= self.conviction_threshold:
                    quality = self._decision_quality(
                        rhythm, dissonance, self.conviction[key], energy
                    )

                    if quality < self.min_quality:
                        continue

                    return self._emit(
                        symbol,
                        "SELL",
                        pattern,
                        zone,
                        tempo,
                        micro_trend,
                        window,
                        rhythm,
                        dissonance,
                        now,
                        quality,
                    )
            else:
                self.conviction[(symbol, pattern)] = 0

        return None

    # ==================================================
    # EMIT
    # ==================================================

    def _emit(
        self,
        symbol,
        side,
        pattern,
        zone,
        tempo,
        micro_trend,
        window,
        rhythm,
        dissonance,
        now,
        quality,
    ):
        bias = self.symbol_bias(symbol)
        base = self._threshold(pattern, zone, tempo)
        effective = base + bias

        self.last_decision = (symbol, pattern, self.last_event_type)
        self.last_decision_ts = now
        self.symbol_cooldown[symbol] = now
        self.conviction[(symbol, pattern)] = 0

        return {
            "symbol": symbol,
            "side": side,
            "amount": 1.0,
            "meta": {
                "binary": True,
                "expiry": self.expiry,
                "pattern": pattern,
                "context": {"zone": zone, "tempo": tempo},
                "intent": {
                    "event": self.last_event_type,
                    "rhythm": rhythm,
                    "dissonance": dissonance,
                    "quality": quality,
                },
                "reason": {
                    "micro_trend": micro_trend,
                    "window": list(window),
                    "effective_threshold": effective,
                },
            },
        }

    # ==================================================
    # ADAPT — APRENDIZADO REAL
    # ==================================================

    def adapt(self, diagnosis: dict):
        result = diagnosis.get("result")
        if result not in ("WIN", "LOSS"):
            return

        symbol = diagnosis.get("symbol")
        pattern = diagnosis.get("pattern")
        zone = diagnosis.get("zone")
        tempo = diagnosis.get("tempo")
        quality = diagnosis.get("quality")

        # Metamemória de qualidade
        if quality is not None:
            self.quality_memory.append((quality, result))
            if len(self.quality_memory) > self.quality_memory_limit:
                self.quality_memory.pop(0)

            if len(self.quality_memory) >= 8:
                wins = [q for q, r in self.quality_memory if r == "WIN"]
                losses = [q for q, r in self.quality_memory if r == "LOSS"]

                avg_win = sum(wins) / len(wins) if wins else 0
                avg_loss = sum(losses) / len(losses) if losses else 0

                if avg_loss >= avg_win and self.min_quality < 6:
                    self.min_quality += 1
                elif avg_win > avg_loss + 1 and self.min_quality > 2:
                    self.min_quality -= 1

        # Aprendizado por símbolo
        if symbol:
            rec = self.by_symbol.setdefault(symbol, {"win": 0, "loss": 0})
            if result == "WIN":
                rec["win"] += 1
            else:
                rec["loss"] += 1

        # Aprendizado contextual
        if pattern and zone and tempo:
            key = (pattern, zone, tempo)
            ctx = self.context_stats.setdefault(
                key,
                {"win": 0, "loss": 0, "threshold": self.base_threshold},
            )

            if result == "WIN":
                ctx["win"] += 1
            else:
                ctx["loss"] += 1

            total = ctx["win"] + ctx["loss"]
            if total >= 8:
                winrate = ctx["win"] / total
                if winrate < 0.45:
                    ctx["threshold"] = min(6, ctx["threshold"] + 1)
                elif winrate > 0.6:
                    ctx["threshold"] = max(1, ctx["threshold"] - 1)

    # ==================================================
    # PERSISTÊNCIA
    # ==================================================

    def export(self):
        return {
            "base_threshold": self.base_threshold,
            "context_stats": self.context_stats,
            "by_symbol": self.by_symbol,
            "min_quality": self.min_quality,
        }

    def import_state(self, data):
        if not data:
            return
        self.base_threshold = data.get("base_threshold", self.base_threshold)
        self.context_stats = data.get("context_stats", self.context_stats)
        self.by_symbol = data.get("by_symbol", self.by_symbol)
        self.min_quality = data.get("min_quality", self.min_quality)
