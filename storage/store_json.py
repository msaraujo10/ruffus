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

    def record_trade(self, action: dict, status: str, mode: str) -> None:
        data = self.load() or {}

        trades = data.get("trades", [])

        event = {
            "symbol": action.get("symbol"),
            "side": action.get("type"),
            "price": action.get("price"),
            "reason": action.get("reason"),
            "status": status,
            "mode": mode,
            "time": datetime.utcnow().isoformat(),
        }

        trades.append(event)
        data["trades"] = trades

        self.save(data)
