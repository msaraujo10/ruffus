import time

from core.engine import Engine
from core.state_machine import State
from core.decision import DecisionEngine
from core.risk import RiskManager
from core.world import World

from adapters.virtual import VirtualBroker
from adapters.bybit import BybitBroker
from storage.store_json import JSONStore


MODE = "VIRTUAL"  # "VIRTUAL" ou "REAL"


def main():
    print(f"🧠 RUFFUS — V2 ESTÁVEL ({MODE})")

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
    else:
        broker = BybitBroker(config["symbols"])

    store = JSONStore(config["store_path"])
    world = World(config["symbols"], store)
    decision = DecisionEngine(config)
    risk = RiskManager(config)

    engine = Engine(
        broker=broker,
        world=world,
        decision=decision,
        risk=risk,
        store=store,
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


if __name__ == "__main__":
    main()
