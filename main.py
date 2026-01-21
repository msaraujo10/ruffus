import time
import os, json
from core.engine import Engine
from core.state_machine import State
from core.decision import DecisionEngine
from core.risk import RiskManager
from core.world import World
from tools.feedback import FeedbackEngine

from adapters.virtual import VirtualBroker
from adapters.bybit import BybitBroker
from storage.store_json import JSONStore


MODE = "OBSERVADOR"  # "VIRTUAL" ou "REAL"


def main():
    print(f"🧠 RUFFUS — V2 ESTÁVEL ({MODE})")

    if MODE == "REPLAY":
        replay()
        return

    config = {
        "stop_loss": -0.5,
        "take_profit": 1.2,
        "sleep": 1,
        "symbols": ["BTCUSDT", "ETHUSDT", "SOLUSDT"],
        "store_path": "storage/state.json",
    }

    # Escolha do broker
    if MODE == "VIRTUAL":
        broker = VirtualBroker(config["symbols"])

    elif MODE == "OBSERVADOR":
        broker = BybitBroker(
            config["symbols"],
            mode=MODE,
            armed=config.get("armed", False),
        )

    elif MODE == "REAL":
        broker = BybitBroker(
            config["symbols"],
            mode="REAL",
            armed=config.get("armed", False),
        )

    else:
        raise ValueError("MODE inválido")

    store = JSONStore(config["store_path"])
    world = World(config["symbols"], store)
    decision = DecisionEngine(config)
    risk = RiskManager(config)

    feedback = FeedbackEngine("storage/events.jsonl")

    engine = Engine(
        broker=broker,
        world=world,
        decision=decision,
        risk=risk,
        store=store,
        feedback=feedback,
        mode=MODE,
    )

    engine.boot()
    engine.state.set(State.IDLE)

    while True:
        try:
            feed = broker.tick()  # { "BTCUSDT": 43210.5, ... }
            world.update(feed)

            snapshot = world.snapshot()
            engine.tick(snapshot)

            store.save(snapshot)

            time.sleep(config["sleep"])

        except KeyboardInterrupt:
            print("\n⏹ Execução interrompida.")
            break


def replay():
    from storage.store_json import JSONStore

    print("🎞️  MODO REPLAY\n")

    path = "storage/events.jsonl"
    if not os.path.exists(path):
        print("Nenhum evento encontrado.")
        return

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            e = json.loads(line)

            ts = e.get("ts")
            state = e.get("state")
            action = e.get("action")
            result = e.get("result")

            if action:
                msg = f"{action['type']} {action['symbol']} @ {action['price']}"
            else:
                msg = "—"

            print(f"[REPLAY] {ts} | {state} | {msg} | {result}")


if __name__ == "__main__":
    main()
