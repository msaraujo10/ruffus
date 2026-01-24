import json
import os
from collections import deque


class TimelineEngine:
    def __init__(self, path: str, max_items: int = 50):
        self.path = path
        self.max_items = max_items

    def read(self):
        if not os.path.exists(self.path):
            return []

        items = deque(maxlen=self.max_items)

        with open(self.path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    e = json.loads(line)
                    items.append(e)
                except Exception:
                    continue

        return list(items)

    def summarize(self):
        events = self.read()

        summary = []
        for e in events:
            ts = e.get("ts")
            state = e.get("state")
            action = e.get("action")
            result = e.get("result")

            if action:
                msg = f"{action['type']} {action['symbol']} @ {action.get('price')}"
            else:
                msg = "—"

            summary.append(f"{ts} | {state} | {msg} | {result}")

        return summary
