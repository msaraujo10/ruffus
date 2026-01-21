import json
import os
from datetime import datetime


class FeedbackEngine:
    """
    Lê eventos do sistema (events.jsonl), resume o comportamento recente
    e produz diagnósticos cognitivos sobre o estado do robô.
    """

    def __init__(self, events_path: str = "storage/events.jsonl"):
        self.events_path = events_path

    # -------------------------------------------------
    # LEITURA DE EVENTOS
    # -------------------------------------------------
    def read_events(self, limit: int = 100) -> list[dict]:
        if not os.path.exists(self.events_path):
            return []

        events = []
        with open(self.events_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

        return events[-limit:]

    # -------------------------------------------------
    # RESUMO
    # -------------------------------------------------
    def summary(self, events: list[dict]) -> dict:
        buys = 0
        sells = 0
        blocked = 0
        errors = 0

        for e in events:
            result = e.get("result")
            action = e.get("action", {})

            if result == "APPROVED" and action.get("type") == "BUY":
                buys += 1
            elif result == "APPROVED" and action.get("type") == "SELL":
                sells += 1
            elif result == "BLOCKED_BY_RISK":
                blocked += 1
            elif result in ("FAILED", "ERROR"):
                errors += 1

        return {
            "events": len(events),
            "buys": buys,
            "sells": sells,
            "blocked": blocked,
            "errors": errors,
        }

    # -------------------------------------------------
    # DIAGNÓSTICO
    # -------------------------------------------------
    def diagnose(self, limit: int = 100) -> dict:
        events = self.read_events(limit)
        summary = self.summary(events)

        problems = []
        signals = []
        recommendations = []

        health = "OK"

        if summary["events"] == 0:
            health = "NO_DATA"
            signals.append("Nenhum evento registrado ainda.")
            recommendations.append("Deixe o sistema rodar por mais tempo.")
        else:
            if summary["blocked"] > summary["buys"]:
                health = "RISK_BLOCKED"
                problems.append("Muitas ações bloqueadas pelo RiskManager.")
                recommendations.append("Revisar configuração de risco.")
                recommendations.append("Verificar se o sistema está armado.")

            if summary["errors"] > 0:
                health = "UNSTABLE"
                problems.append("Ocorreram erros recentes.")
                recommendations.append("Verificar logs e integridade dos brokers.")

            if summary["buys"] == 0 and summary["events"] > 20:
                problems.append("Nenhuma entrada executada.")
                recommendations.append("Ajustar critérios do DecisionEngine.")

        diagnosis = {
            "health": health,
            "summary": summary,
            "problems": problems,
            "signals": signals,
            "recommendations": recommendations,
        }

        # Persistência cognitiva
        self.persist_memory(diagnosis)

        return diagnosis

    # -------------------------------------------------
    # MEMÓRIA COGNITIVA
    # -------------------------------------------------
    def persist_memory(self, diagnosis: dict) -> None:
        try:
            path = "storage/memory.json"
            os.makedirs(os.path.dirname(path), exist_ok=True)

            payload = dict(diagnosis)
            payload["updated_at"] = datetime.utcnow().isoformat()

            with open(path, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=4, ensure_ascii=False)

        except Exception as e:
            print(f"[MEMORY] Falha ao persistir memória: {e}")
