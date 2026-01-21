import time
import os, json
from core.engine import Engine
from core.state_machine import State
from core.decision import DecisionEngine
from core.risk import RiskManager
from core.world import World
from tools.feedback import FeedbackEngine
from tools.memory import CognitiveMemory

from adapters.virtual import VirtualBroker
from adapters.bybit import BybitBroker
from storage.store_json import JSONStore

MODE = "VIRTUAL"  # OBSERVADOR | REAL | VIRTUAL


def main():
    mode = MODE
    print(f"🧠 RUFFUS — V2 ESTÁVEL ({mode})")

    config = {
        "stop_loss": -0.5,
        "take_profit": 1.2,
        "sleep": 1,
        "symbols": ["BTCUSDT", "ETHUSDT", "SOLUSDT"],
        "store_path": "storage/state.json",
        "armed": True,
    }

    memory = CognitiveMemory()
    health = memory.health()

    if health == "RISK_BLOCKED":
        print("🧠 Sistema em estado RISK_BLOCKED. Desarmando automaticamente.")
        config["armed"] = False

    elif health == "UNSTABLE":
        print("🧠 Sistema instável. Forçando modo OBSERVADOR.")
        mode = "OBSERVADOR"

    if mode == "VIRTUAL":
        replay()
        return

    # Escolha do broker
    if mode == "VIRTUAL":
        broker = VirtualBroker(config["symbols"])

    elif mode == "OBSERVADOR":
        broker = BybitBroker(
            config["symbols"],
            mode=mode,
            armed=config.get("armed", False),
        )

    elif mode == "REAL":
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
        mode=mode,
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
