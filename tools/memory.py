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
        """
        Retorna um perfil cognitivo do sistema:
        - "PAUSED"
        - "CONSERVATIVE"
        - "NORMAL"
        - "AGGRESSIVE"
        """

        data = self.load()

        if not data:
            return "NORMAL"

        health = data.get("health")
        summary = data.get("summary", {})

        total = summary.get("total_events", 0)
        blocked = summary.get("blocked", 0)
        approved = summary.get("approved", 0)

        # Estado crítico: sistema travado por risco
        if health == "RISK_BLOCKED":
            return "PAUSED"

        # Muito bloqueio em relação ao total → conservador
        if total > 0 and blocked / total > 0.6:
            return "CONSERVATIVE"

        # Muitas execuções reais → agressivo
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
