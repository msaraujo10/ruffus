import json
import os


class FeedbackEngine:
    """
    Observador cognitivo do sistema.

    Nesta fase:
    - Não interfere em decisões
    - Não altera estado
    - Apenas observa ciclos
    - Lê eventos históricos (jsonl) quando necessário
    """

    def __init__(self, events_path: str):
        self.events_path = events_path

    def observe(self, state: str, world: dict, action: dict | None):
        """
        Recebe tudo que o robô está vendo.
        Por enquanto, apenas observa.
        """
        # Fase 9.2 é passiva. Nada acontece aqui ainda.
        pass

    def load_events(self) -> list[dict]:
        """
        Carrega eventos do arquivo .jsonl
        """
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
                except Exception:
                    continue

        return events
