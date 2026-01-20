import json
from pathlib import Path


class StoreJSON:
    def __init__(self, path="data/state.json"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def save(self, data: dict):
        with self.path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def load(self) -> dict | None:
        if not self.path.exists():
            return None

        with self.path.open("r", encoding="utf-8") as f:
            return json.load(f)
