# main.py

import time

from core.engine import Engine
from core.decision import DecisionEngine
from core.risk import RiskManager
from core.world import World
from adapters.virtual import VirtualBroker


def main():
    print("🧠 RUFFUS — V2 ESTÁVEL (MODO VIRTUAL)")

    config = {
        "stop_loss": -0.5,
        "take_profit": 1.2,
        "sleep": 1,
        "symbols": ["TESTEUSDT"],
    }

    broker = VirtualBroker()
    decision = DecisionEngine(config)
    risk = RiskManager(config)
    engine = Engine(broker, decision, risk)

    world = World(config["symbols"])

    engine.boot()

    while True:
        try:
            feed = broker.tick()
            # feed deve ser algo como:
            # {"TESTEUSDT": {"price": 1.0123}}

            world.update(feed)
            snapshot = world.snapshot()

            engine.tick(snapshot)

            time.sleep(config["sleep"])

        except KeyboardInterrupt:
            print("\n⏹ Execução interrompida.")
            break


if __name__ == "__main__":
    main()
