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

    def interpret(self, summary: dict) -> list[str]:
        """
        Recebe o resumo numérico e retorna uma lista de insights humanos.
        """
        insights = []

        total = summary.get("total_events", 0)
        approved = summary.get("approved", 0)
        blocked = summary.get("blocked_by_risk", 0)

        by_state = summary.get("by_state", {})
        by_action = summary.get("by_action", {})

        # 1. Nenhuma ação aprovada
        if total > 0 and approved == 0:
            insights.append("Nenhuma ação foi aprovada no período analisado.")

        # 2. Tudo bloqueado por risco
        if total > 0 and blocked == total:
            insights.append("Todas as ações foram bloqueadas pelo sistema de risco.")

        # 3. Apenas um estado observado
        if len(by_state) == 1:
            state = next(iter(by_state.keys()))
            insights.append(f"O robô permaneceu exclusivamente no estado {state}.")

        # 4. Apenas um tipo de ação
        if len(by_action) == 1:
            action = next(iter(by_action.keys()))
            insights.append(f"O robô tentou apenas ações do tipo {action}.")

        return insights
