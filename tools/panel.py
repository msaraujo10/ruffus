import time
import os
from datetime import datetime


class Panel:
    def __init__(self, engine, refresh: float = 2.0):
        self.engine = engine
        self.refresh = refresh

    def clear(self):
        os.system("cls" if os.name == "nt" else "clear")

    def render_header(self):
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        print("🧠 RUFFUS — Painel Vivo")
        print("=" * 60)
        print(f"{now}")
        print("=" * 60)

    def render_state(self, snap):
        print("\n🧠 ESTADO DO SISTEMA")
        print("-" * 60)
        print(f"Modo: {snap['mode']}")
        print(f"State: {snap['state']}")
        print(f"Saúde: {snap['health']}")

    def render_intent(self, snap):
        print("\n🎯 PROPOSTA DO SISTEMA")
        print("-" * 60)

        intent = snap.get("intent")

        if not intent:
            print("Nenhuma")
            return

        print(f"Ação:   {intent.get('type')}")
        print(f"Ativo:  {intent.get('symbol')}")
        print(f"Preço: {intent.get('price')}")

        reason = intent.get("reason")
        if reason:
            print(f"Motivo: {reason}")

        if snap.get("awaiting_human"):
            print("\n⏳ Aguardando confirmação humana...")

    def render_events(self, snap):
        print("\n📜 ÚLTIMOS EVENTOS")
        print("-" * 60)

        events = snap.get("last_events", [])
        if not events:
            print("Nenhum evento.")
            return

        for e in events:
            tag = e.get("result") or e.get("type")
            print(f"- {tag}")

    def render(self):
        self.clear()
        snap = self.engine.cognitive_snapshot()

        self.render_header()
        self.render_state(snap)
        self.render_intent(snap)
        self.render_events(snap)
