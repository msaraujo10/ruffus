import os
from datetime import datetime


class ControlPanel:
    def __init__(self):
        self._last_render = None

    def clear(self):
        os.system("cls" if os.name == "nt" else "clear")

    def render(self, engine, world, feedback):
        """
        Exibe o estado vivo do sistema em tempo real.
        Não executa nada. Apenas observa.
        """

        self.clear()

        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

        state = engine.state.current().name
        mode = engine.mode
        symbols = world.symbols
        prices = world.prices

        open_positions = []
        if hasattr(engine.strategy, "entries"):
            open_positions = list(engine.strategy.entries.keys())

        health = "—"
        if feedback:
            try:
                health = feedback.health()
            except Exception:
                health = "UNKNOWN"

        last_action = None
        if feedback:
            try:
                last_action = feedback.last_action()
            except Exception:
                last_action = None

        print("╔══════════════════════════════════════════════╗")
        print("║            🧠 RUFFUS CONTROL PANEL           ║")
        print("╠══════════════════════════════════════════════╣")
        print(f"║ Time        : {now:<28} ║")
        print(f"║ Mode        : {mode:<28} ║")
        print(f"║ State       : {state:<28} ║")
        print(f"║ Health      : {health:<28} ║")
        print("╠══════════════════════════════════════════════╣")
        print("║ Symbols / Prices                             ║")

        for s in symbols:
            p = prices.get(s)
            txt = f"{s}: {p:.6f}" if isinstance(p, (int, float)) else f"{s}: —"
            print(f"║  {txt:<44}║")

        print("╠══════════════════════════════════════════════╣")
        print("║ Open Positions                               ║")

        if open_positions:
            for s in open_positions:
                print(f"║  {s:<44}║")
        else:
            print(f"║  — none —                                   ║")

        print("╠══════════════════════════════════════════════╣")
        print("║ Last Action                                  ║")

        if last_action:
            msg = f"{last_action.get('type')} {last_action.get('symbol')} @ {last_action.get('price')}"
            print(f"║  {msg:<44}║")
        else:
            print(f"║  —                                          ║")

        print("╚══════════════════════════════════════════════╝")
