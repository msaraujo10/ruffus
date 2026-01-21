import json
from pathlib import Path
from datetime import datetime


class ReplayAnalyzer:
    """
    Lê eventos persistidos pelo JSONStore e reconstrói
    a linha mental do robô em linguagem humana.
    """

    def __init__(self, path: str):
        self.path = Path(path)

    def load(self) -> list[dict]:
        if not self.path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {self.path}")

        with open(self.path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Esperamos que os eventos estejam em data["events"]
        return data.get("events", [])

    def format_event(self, ev: dict) -> str:
        ts = ev.get("timestamp") or ev.get("time") or "?"
        try:
            ts = datetime.fromisoformat(ts).strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            pass

        state = ev.get("state", "?")
        action = ev.get("action")
        result = ev.get("result", "?")

        lines = []
        lines.append(f"[{ts}]")
        lines.append(f"STATE: {state}")

        if action:
            typ = action.get("type")
            sym = action.get("symbol", "?")
            price = action.get("price", "?")
            lines.append(f"ACTION: {typ} {sym} @ {price}")
        else:
            lines.append("ACTION: NONE")

        lines.append(f"RESULT: {result}")

        if result == "BLOCKED_BY_RISK":
            reason = ev.get("reason") or "Regra de risco"
            lines.append(f"REASON: {reason}")

        return "\n".join(lines)

    def run(self):
        events = self.load()

        if not events:
            print("Nenhum evento encontrado.")
            return

        for ev in events:
            print(self.format_event(ev))
            print("-" * 40)


if __name__ == "__main__":
    # Ajuste o caminho conforme seu projeto
    analyzer = ReplayAnalyzer("storage/state.json")
    analyzer.run()
