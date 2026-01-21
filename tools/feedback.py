import json
import os


class FeedbackEngine:
    def __init__(self, events_path: str):
        self.events_path = events_path

    def load_events(self) -> list[dict]:
        events = []

        if not os.path.exists(self.events_path):
            return events

        with open(self.events_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    events.append(json.loads(line))
                except Exception:
                    continue

        return events

    def summary(self) -> dict:
        events = self.load_events()

        summary = {
            "total_events": len(events),
            "blocked_by_risk": 0,
            "approved": 0,
            "by_state": {},
            "by_action": {},
        }

        for e in events:
            result = e.get("result")
            state = e.get("state")
            action = e.get("action", {})
            kind = action.get("type")

            if result == "BLOCKED_BY_RISK":
                summary["blocked_by_risk"] += 1
            elif result == "APPROVED":
                summary["approved"] += 1

            if state:
                summary["by_state"][state] = summary["by_state"].get(state, 0) + 1

            if kind:
                summary["by_action"][kind] = summary["by_action"].get(kind, 0) + 1

        return summary
