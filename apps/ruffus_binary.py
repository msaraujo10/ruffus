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
    memory = CognitiveMemory("storage/binary/memory.json")
    store = JSONStore("storage/binary/state.json")
    feedback = FeedbackEngine(
        events_path="storage/binary/events.jsonl",
        memory_path="storage/binary/memory.json",
        journal_path="storage/binary/journal.jsonl",
    )

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

            # Nenhum evento real → nenhum pensamento
            if feed is None:
                time.sleep(1)
                continue

            engine.step(feed)
            panel.render()

            time.sleep(binary_config["sleep"])

        except KeyboardInterrupt:
            print("\n⏹ Execução interrompida.")
            break


if __name__ == "__main__":
    main()
