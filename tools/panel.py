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
        if snap["mode"] == "PAUSED":
            print("🔴 SISTEMA PAUSADO PELO RISCO")

    def render_intent(self, snap):
        print("\n🎯 INTENÇÃO")
        print("-" * 60)
        if snap["pending_action"]:
            print(snap["pending_action"])
        else:
            print("Nenhuma")

    def render(self):
        snap = self.engine.cognitive_snapshot()
        if snap["state"] != "ERROR":
            self.clear()
        self.render_header()
        self.render_state(snap)
        self.render_intent(snap)
        self.render_events(snap)

        if snap["state"] == "AWAIT_CONFIRMATION":
            print("\n⏸ Aguardando confirmação humana")
            print("[C] Confirmar   [X] Cancelar")

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

    def run(self):
        while True:
            try:
                self.clear()

                snap = self.engine.cognitive_snapshot()

                self.render_header()
                self.render_state(snap)
                self.render_intent(snap)
                self.render_events(snap)

                time.sleep(self.refresh)

            except KeyboardInterrupt:
                print("\n⏹ Painel encerrado.")
                break
