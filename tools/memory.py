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

    def health(self) -> str | None:
        data = self.load()
        if not data:
            return None
        return data.get("health")
