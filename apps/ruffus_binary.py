import time
import os

from core.engine import Engine
from core.risk import RiskManager
from core.world import World
from core.profiles.registry import load_profile
from strategies.binary.registry import load_binary_strategies

from tools.feedback import FeedbackEngine
from tools.memory import CognitiveMemory
from tools.panel import Panel

from brokers.bullex import BullexBroker
from storage.store_json import JSONStore

MODE = "ASSISTED"
WEB_PORT = 8001


def main():
    print(f"🧠 RUFFUS-BINARY — BOOT ({MODE})")

    # ------------------------------------------------------------------
    # Configuração própria da linhagem binária
    # ------------------------------------------------------------------
    binary_config = {
        "symbols": [
            "AUDCAD",
            "AUDJPY",
            "AUDUSD",
            "CADJPY",
            "EURGBP",
            "EURCAD",
            "EURJPY",
            "EURUSD",
            "GBPUSD",
            "GBPJPY",
            "USDCAD",
            "USDJPY",
        ],
        "store_path": "storage/binary/state.json",
        "memory_path": "storage/binary/memory.json",
        "events_path": "storage/binary/events.jsonl",
        "sleep": 1,
    }

    os.makedirs("storage/binary", exist_ok=True)

    # ------------------------------------------------------------------
    # Órgãos cognitivos próprios
    # ------------------------------------------------------------------
    memory = CognitiveMemory(binary_config["memory_path"])
    store = JSONStore(binary_config["store_path"])
    feedback = FeedbackEngine(binary_config["events_path"])

    world = World(binary_config["symbols"], store)
    strategy = load_binary_strategies("impulse", binary_config)
    risk = RiskManager({})  # risco ainda neutro no estágio binário inicial

    broker = BullexBroker(
        binary_config["symbols"],
        mode=MODE,
        account="DEMO",
        armed=False,
    )

    engine = Engine(
        broker=broker,
        world=world,
        strategy=strategy,
        risk=risk,
        store=store,
        feedback=feedback,
        mode=MODE,
    )

    engine.boot()

    # ------------------------------------------------------------------
    # Web API própria (porta isolada)
    # ------------------------------------------------------------------
    from tools import web

    web.engine_ref = engine

    import threading
    import uvicorn

    def run_web():
        uvicorn.run(web.app, host="127.0.0.1", port=WEB_PORT, log_level="error")

    threading.Thread(target=run_web, daemon=True).start()

    panel = Panel(engine)

    # ------------------------------------------------------------------
    # Loop vital
    # ------------------------------------------------------------------
    while True:
        try:
            feed = broker.tick()
            engine.step(feed)

            # --------------------------------------------------
            # Fecha o ciclo cognitivo binário (aprendizado)
            # --------------------------------------------------
            if hasattr(broker, "events") and broker.events:
                while broker.events:
                    evt = broker.events.pop(0)

                    if evt.get("type") == "binary_result":
                        diagnosis = {
                            "pattern": evt.get("pattern"),
                            "result": evt.get("result"),
                            "symbol": evt.get("symbol"),
                            "zone": evt.get("zone"),
                            "tempo": evt.get("tempo"),
                        }

                        # 1. A mente binária aprende
                        engine.strategy.adapt(diagnosis)

                        # 2. O evento é registrado na história da espécie
                        feedback.log(
                            {
                                "type": "binary_result",
                                **diagnosis,
                            }
                        )

                        # 3. A memória cognitiva absorve a experiência
                        memory.observe(
                            {
                                "kind": "binary_outcome",
                                "pattern": diagnosis["pattern"],
                                "zone": diagnosis["zone"],
                                "tempo": diagnosis["tempo"],
                                "result": diagnosis["result"],
                            }
                        )

            panel.render()

            # --------------------------------------------------
            # Overlay Cognitivo Binário (mente + raciocínio)
            # --------------------------------------------------
            strategy = engine.strategy
            if hasattr(strategy, "export"):
                data = strategy.export()
                stats = data.get("stats", {})
                threshold = data.get("threshold")

                print("\n🧠 MENTE BINÁRIA")
                print("-" * 60)

                if not stats:
                    print("Nenhum padrão observado ainda.")
                else:
                    for pattern, s in stats.items():
                        win = s.get("win", 0)
                        loss = s.get("loss", 0)
                        total = win + loss
                        winrate = (win / total * 100) if total > 0 else 0

                        print(
                            f"{pattern:25}  "
                            f"WIN: {win:3}  "
                            f"LOSS: {loss:3}  "
                            f"WR: {winrate:5.1f}%"
                        )

                print(f"\nThreshold atual: {threshold}")

            # --------------------------------------------------
            # Mostra o raciocínio da proposta (se houver)
            # --------------------------------------------------
            pa = engine.pending_action
            if pa:
                meta = pa.get("meta", {})
                reason = meta.get("reason")

                if reason:
                    print("\n🧠 RACIOCÍNIO DA PROPOSTA")
                    print("-" * 60)
                    print(f"Zona macro:     {reason.get('zone')}")
                    print(f"Micro-trend:    {reason.get('micro_trend')}")
                    print(f"Janela:         {reason.get('window')}")
                    print(f"Threshold atual:{reason.get('threshold')}")

            if engine.state.current().name == "AWAIT_CONFIRMATION":
                cmd = input("Confirmar [c] / Cancelar [x]: ").strip().lower()
                if cmd == "c":
                    engine.confirm()
                elif cmd == "x":
                    reason = input("Motivo (opcional): ").strip()
                    engine.cancel(reason or None)

            time.sleep(binary_config["sleep"])

        except KeyboardInterrupt:
            print("\n⏹ Execução interrompida.")
            break


if __name__ == "__main__":
    main()
