import json
import os
from datetime import datetime


class JSONStore:
    def __init__(self, path: str):
        self.path = path

    def exists(self) -> bool:
        return os.path.exists(self.path)

    def load(self) -> dict | None:
        if not self.exists():
            return None

        with open(self.path, "r", encoding="utf-8") as f:
            return json.load(f)

    def save(self, snapshot: dict) -> None:
        snapshot["meta"] = {
            "version": "2.0",
            "last_update": datetime.utcnow().isoformat(),
        }

        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(snapshot, f, indent=4, ensure_ascii=False)

    def record_event(self, event: dict) -> None:
        """
        Acrescenta o evento em um log sequencial.
        Nunca lança exceção.
        Nunca altera eventos anteriores.
        """
        try:
            path = "storage/events.jsonl"
            with open(path, "a", encoding="utf-8") as f:
                f.write(json.dumps(event, ensure_ascii=False) + "\n")
        except Exception:
            pass  # nunca quebra o robô

        """
        Registra eventos operacionais:
        - decisões
        - bloqueios
        - estados
        - erros
        """
        data = self.load() or {}

        events = data.get("events", [])
        events.append(event)

        data["events"] = events
        self.save(data)

    def record_trade(self, trade: dict) -> None:
        """
        Registra apenas ações financeiras.
        """
        data = self.load() or {}

        trades = data.get("trades", [])
        trades.append(trade)

        data["trades"] = trades
        self.save(data)
