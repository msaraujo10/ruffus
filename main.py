import time

from core.engine import Engine
from core.state_machine import StateMachine
from core.decision import DecisionEngine
from core.risk import RiskManager
from core.world import World

from adapters.virtual import VirtualBroker
from storage.store_json import StoreJSON


def main():
    print("🧠 RUFFUS — V2 ESTÁVEL (MODO VIRTUAL | MULTI-ATIVO)")

    config = {
        "symbols": ["BTCUSDT", "ETHUSDT", "SOLUSDT"],
        "stop_loss": -0.5,
        "take_profit": 1.2,
        "sleep": 1,
    }

    store = StoreJSON("data/state.json")

    broker = VirtualBroker(config["symbols"])
    decision = DecisionEngine(config)
    risk = RiskManager(config)
    world = World(config["symbols"], store)
    engine = Engine(broker, decision, risk, world, store)

    state_machine = StateMachine()
    engine.boot(state_machine)

    while True:
        try:
            feed = broker.tick()  # { "BTCUSDT": price, ... }
            world.update(feed)

            engine.tick(world.snapshot())

            time.sleep(config["sleep"])

        except KeyboardInterrupt:
            print("\n⏹ Execução interrompida.")
            break


if __name__ == "__main__":
    main()
