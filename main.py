import time

from core.engine import Engine
from core.state_machine import State
from core.decision import DecisionEngine
from core.risk import RiskManager
from core.world import World
from adapters.virtual import VirtualBroker
from storage.store_json import JsonStore


def main():
    print("🧠 RUFFUS — V2 ESTÁVEL (MODO VIRTUAL | MULTI-ATIVO)")

    config = {
        "stop_loss": -0.5,
        "take_profit": 1.2,
        "sleep": 1,
        "symbols": ["BTCUSDT", "ETHUSDT", "SOLUSDT"],
    }

    broker = VirtualBroker(config["symbols"])
    store = JsonStore()

    world = World(config["symbols"], store)
    decision = DecisionEngine(config, store)
    risk = RiskManager(config)
    engine = Engine(broker, decision, risk)

    engine.boot()
    engine.state.set(State.IDLE)

    while True:
        try:
            feed = broker.tick()
            world.update(feed)

            engine.tick(world.snapshot())
            time.sleep(config["sleep"])

        except KeyboardInterrupt:
            print("\n⏹ Execução interrompida.")
            break


if __name__ == "__main__":
    main()
