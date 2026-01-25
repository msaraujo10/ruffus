import json
import os
from datetime import datetime


class FeedbackEngine:
    """
    Lê eventos do sistema (events.jsonl), resume o comportamento recente
    e produz diagnósticos cognitivos sobre o estado do robô,
    incluindo agora a relação com o humano.
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
        human_confirmed = 0
        human_cancelled = 0
        consecutive_cancels = 0
        max_consecutive_cancels = 0

        for e in events:
            etype = e.get("type")
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

            if etype == "human_confirmed":
                human_confirmed += 1
                consecutive_cancels = 0

            elif etype == "human_cancelled":
                human_cancelled += 1
                consecutive_cancels += 1
                max_consecutive_cancels = max(
                    max_consecutive_cancels, consecutive_cancels
                )

        return {
            "events": len(events),
            "buys": buys,
            "sells": sells,
            "blocked": blocked,
            "errors": errors,
            "human_confirmed": human_confirmed,
            "human_cancelled": human_cancelled,
            "max_consecutive_cancels": max_consecutive_cancels,
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

            # ----------------------------
            # SINAIS HUMANOS
            # ----------------------------
            hc = summary["human_confirmed"]
            hcan = summary["human_cancelled"]

            if hcan > hc and hcan >= 3:
                signals.append("Humano tem negado mais propostas do que aprovado.")
                recommendations.append("Reduzir agressividade da estratégia.")

            if summary["max_consecutive_cancels"] >= 3:
                signals.append("Múltiplas negações humanas consecutivas.")
                recommendations.append(
                    "Sistema possivelmente desalinhado com o operador."
                )

        total = summary.get("events", 0) or 1

        metrics = {
            "block_rate": summary.get("blocked", 0) / total,
            "buy_ratio": summary.get("buys", 0) / total,
            "sell_ratio": summary.get("sells", 0) / total,
            "error_rate": summary.get("errors", 0) / total,
            "human_cancel_ratio": summary.get("human_cancelled", 0) / total,
        }

        diagnosis = {
            "health": health,
            "summary": summary,
            "metrics": metrics,
            "problems": problems,
            "signals": signals,
            "recommendations": recommendations,
        }

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
