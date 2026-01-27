import json
import os


class CognitiveMemory:
    def __init__(self, path="storage/memory.json"):
        self.path = path

    def load(self) -> dict | None:
        if not os.path.exists(self.path):
            return None

        with open(self.path, "r", encoding="utf-8") as f:
            return json.load(f)

    def save(self, data: dict):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def observe(self, event: dict):
        """
        Registra uma experiência cognitiva.
        Usado pelo Ruffus-Binary para criar passado próprio.
        """
        data = self.load() or {}
        history = data.setdefault("history", [])
        history.append(event)
        self.save(data)

    def recomendations(self) -> list[str]:
        data = self.load()
        if not data:
            return []
        return data.get("recomendations", [])

    def health(self) -> str:
        data = self.load()
        if not data:
            return "EMPTY"
        return data.get("health", "UNKNOWN")

    def profile(self) -> str:
        data = self.load()

        if not data:
            return "NORMAL"

        health = data.get("health")
        summary = data.get("summary", {})

        total = summary.get("total_events", 0)
        blocked = summary.get("blocked", 0)
        approved = summary.get("approved", 0)

        if health == "RISK_BLOCKED":
            return "PAUSED"

        if total > 0 and blocked / total > 0.6:
            return "CONSERVATIVE"

        if approved >= 10 and blocked < approved:
            return "AGGRESSIVE"

        return "NORMAL"

    def update_profile(self, profile: str, config: dict):
        data = self.load() or {}

        data["profile"] = profile
        data["last_config"] = {
            "take_profit": config.get("take_profit"),
            "stop_loss": config.get("stop_loss"),
            "armed": config.get("armed"),
        }

        self.save(data)
