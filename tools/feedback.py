import json
import os
from datetime import datetime


class FeedbackEngine:
    def __init__(self, events_path: str = "storage/events.jsonl"):
        self.events_path = events_path

    def read_events(self, limit: int = 100) -> list[dict]:
        if not os.path.exists(self.events_path):
            return []

        events = []
        with open(self.events_path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    events.append(json.loads(line.strip()))
                except Exception:
                    continue

        return events[-limit:]

    def summary(self, events: list[dict]) -> dict:
        buys = sells = blocked = errors = 0
        human_confirms = 0
        human_cancels = 0
        human_overrides = {}
        consecutive_cancels = 0
        max_consecutive_cancels = 0

        for e in events:
            etype = e.get("type")
            result = e.get("result")
            action = e.get("action", {})

            if result == "APPROVED" and action.get("type") == "BUY":
                buys += 1
            elif result == "APPROVED" and action.get("type") == "SELL":
                sells += 1
            elif result == "BLOCKED_BY_RISK":
                blocked += 1
            elif result in ("FAILED", "ERROR"):
                errors += 1

            if etype == "human_confirm":
                human_confirms += 1
                consecutive_cancels = 0

            elif etype == "human_cancel":
                human_cancels += 1
                consecutive_cancels += 1
                max_consecutive_cancels = max(
                    max_consecutive_cancels, consecutive_cancels
                )

            elif etype == "human_override_regime":
                regime = e.get("regime")
                if regime:
                    human_overrides[regime] = human_overrides.get(regime, 0) + 1

        return {
            "events": len(events),
            "buys": buys,
            "sells": sells,
            "blocked": blocked,
            "errors": errors,
            "human_confirms": human_confirms,
            "human_cancels": human_cancels,
            "human_overrides": human_overrides,
            "max_consecutive_cancels": max_consecutive_cancels,
        }

    def read_journal(self, limit: int = 20):
        path = "storage/journal.jsonl"
        if not os.path.exists(path):
            return []

        entries = []
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    entries.append(json.loads(line))
                except Exception:
                    continue

        return entries[-limit:]

    def write_journal(self, diagnosis: dict):
        try:
            path = "storage/journal.jsonl"
            os.makedirs(os.path.dirname(path), exist_ok=True)

            entry = {
                "ts": datetime.utcnow().isoformat(),
                "health": diagnosis.get("health"),
                "summary": diagnosis.get("summary"),
                "signals": diagnosis.get("signals"),
                "recommendations": diagnosis.get("recommendations"),
            }

            with open(path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")

        except Exception as e:
            print(f"[JOURNAL] Falha ao escrever diário: {e}")

    def diagnose(self, limit: int = 100) -> dict:
        events = self.read_events(limit)
        summary = self.summary(events)

        problems = []
        signals = []
        recommendations = []

        health = "OK"

        if summary["events"] == 0:
            health = "NO_DATA"
            signals.append("Nenhum evento registrado ainda.")
        else:
            if summary["blocked"] > summary["buys"]:
                health = "RISK_BLOCKED"

            if summary["errors"] > 0:
                health = "UNSTABLE"

            hc = summary["human_confirms"]
            hcan = summary["human_cancels"]

            if hcan > hc and hcan >= 3:
                signals.append("Humano tem negado mais propostas do que aprovado.")

            if summary["max_consecutive_cancels"] >= 3:
                signals.append("Múltiplas negações humanas consecutivas.")

            if summary["human_overrides"]:
                most = max(summary["human_overrides"].items(), key=lambda x: x[1])[0]
                signals.append(f"Humano costuma forçar regime: {most}.")

            journal = self.read_journal(limit=10)

            if len(journal) >= 3:
                last = [e.get("health") for e in journal]

                if last.count("UNSTABLE") == 0:
                    signals.append("Trajetória recente indica estabilidade crescente.")

                if last[-1] == "OK" and last[0] != "OK":
                    signals.append("O organismo está se recuperando ao longo do tempo.")

        diagnosis = {
            "health": health,
            "summary": summary,
            "signals": signals,
            "recommendations": recommendations,
        }

        self.persist_memory(diagnosis)
        self.write_journal(diagnosis)
        return diagnosis

    def health(self) -> str:
        try:
            return self.diagnose(limit=50).get("health", "OK")
        except Exception:
            return "UNSTABLE"

    def persist_memory(self, diagnosis: dict) -> None:
        try:
            path = "storage/memory.json"
            os.makedirs(os.path.dirname(path), exist_ok=True)

            payload = dict(diagnosis)
            payload["updated_at"] = datetime.utcnow().isoformat()

            with open(path, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=4, ensure_ascii=False)

        except Exception as e:
            print(f"[MEMORY] Falha ao persistir memória: {e}")
