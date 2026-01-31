import time
import os
import json


from core.engine import Engine
from core.risk import RiskManager
from core.world import World
from core.profiles.registry import load_profile
from strategies.canonical.registry import load_strategy

from tools.feedback import FeedbackEngine
from tools.memory import CognitiveMemory
from tools.panel import Panel


from adapters.virtual import VirtualBroker
from adapters.bybit import BybitBroker
from storage.store_json import JSONStore

MODE = "ASSISTED"


def main():
    print(f"🧠 RUFFUS — V2 ESTÁVEL ({MODE})")

    os.makedirs("storage", exist_ok=True)

    memory = CognitiveMemory("storage/memory.json")

    feedback = FeedbackEngine(
        events_path="storage/events.jsonl",
        memory_path="storage/memory.json",
        journal_path="storage/journal.jsonl",
    )
    health = memory.health()

    config = {
        "profile": "moderate",
        "stop_loss": -0.5,
        "take_profit": 1.2,
        "sleep": 1,
        "symbols": [
            "ETHUSDT",
            "SOLUSDT",
            "BNBUSDT",
            "XRPUSDT",
            "ADAUSDT",
            "AVAXUSDT",
            "LINKUSDT",
        ],
        "store_path": "storage/state.json",
        "armed": True,
        "strategy": "simple_trend",
    }

    profile = load_profile(config["profile"])
    config = profile.apply(config)

    if MODE == "VIRTUAL":
        broker = VirtualBroker(config["symbols"])
    elif MODE in ("REAL", "ASSISTED"):
        broker = BybitBroker(config["symbols"], mode="REAL", armed=config["armed"])
    else:
        broker = BybitBroker(config["symbols"], mode="OBSERVADOR", armed=False)

    store = JSONStore(config["store_path"])
    world = World(config["symbols"], store)
    strategy = load_strategy(config["strategy"], config)
    risk = RiskManager(config)
    # NÃO recriar feedback aqui

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
    from tools import web

    web.engine_ref = engine

    import threading
    import uvicorn

    def run_web():
        uvicorn.run(web.app, host="127.0.0.1", port=8000, log_level="error")

    threading.Thread(target=run_web, daemon=True).start()

    panel = Panel(engine)

    while True:
        try:
            feed = broker.tick()
            engine.step(feed)
            panel.render()

            time.sleep(config["sleep"])

        except KeyboardInterrupt:
            print("\n⏹ Execução interrompida.")
            break


if __name__ == "__main__":
    main()
