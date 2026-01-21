import json
from collections import Counter, defaultdict
from pathlib import Path


class CognitiveMetrics:
    def __init__(self, events_path: str):
        self.path = Path(events_path)

    def load_events(self) -> list[dict]:
        if not self.path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {self.path}")

        events = []
        with open(self.path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    events.append(json.loads(line))
                except Exception:
                    continue  # ignora linhas corrompidas

        return events

    def analyze(self) -> dict:
        events = self.load_events()

        counters = {
            "total": 0,
            "no_action": 0,
            "approved": 0,
            "blocked": 0,
            "errors": 0,
        }

        states = Counter()
        actions = Counter()
        modes = Counter()
        reasons = Counter()

        for e in events:
            counters["total"] += 1

            state = e.get("state")
            if state:
                states[state] += 1

            mode = e.get("mode")
            if mode:
                modes[mode] += 1

            result = e.get("result")
            if result == "NO_ACTION":
                counters["no_action"] += 1
            elif result == "APPROVED":
                counters["approved"] += 1
            elif result == "BLOCKED_BY_RISK":
                counters["blocked"] += 1
            elif result in ("ERROR", "FAILED"):
                counters["errors"] += 1

            action = e.get("action")
            if isinstance(action, dict):
                actions[action.get("type")] += 1
                if "reason" in action:
                    reasons[action["reason"]] += 1

        return {
            "counters": counters,
            "states": states,
            "actions": actions,
            "modes": modes,
            "reasons": reasons,
        }

    def report(self) -> None:
        data = self.analyze()

        print("\n🧠 RESUMO COGNITIVO DO SISTEMA")
        print("-" * 40)

        c = data["counters"]
        print(f"Eventos totais:        {c['total']}")
        print(f"Ciclos sem ação:       {c['no_action']}")
        print(f"Ações aprovadas:       {c['approved']}")
        print(f"Bloqueios por risco:   {c['blocked']}")
        print(f"Erros/Falhas:          {c['errors']}")

        print("\nEstados mais comuns:")
        total_states = sum(data["states"].values()) or 1
        for state, count in data["states"].most_common():
            pct = (count / total_states) * 100
            print(f"  {state:<12} {pct:6.2f}%")

        print("\nTipos de ação:")
        for k, v in data["actions"].most_common():
            print(f"  {k:<8} {v}")

        print("\nModos de execução:")
        for k, v in data["modes"].most_common():
            print(f"  {k:<10} {v}")

        if data["reasons"]:
            print("\nMotivos de saída:")
            for k, v in data["reasons"].most_common():
                print(f"  {k:<10} {v}")


if __name__ == "__main__":
    metrics = CognitiveMetrics("storage/events.jsonl")
    metrics.report()
