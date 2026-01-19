import time

from core.engine_old import Engine
from core.state_machine import State
from core.decision_old import DecisionEngine
from core.risk import RiskManager
from core.world_old import World
from adapters.virtual_old import VirtualBroker


def main():
    print("🧠 RUFFUS — V2 ESTÁVEL (MODO VIRTUAL)")

    config = {
        "stop_loss": -0.5,
        "take_profit": 1.2,
        "sleep": 1,
        "symbols": ["BTCUSDT", "ETHUSDT", "SOLUSDT", "ADAUSDT"],
    }

    broker = VirtualBroker(config["symbols"])
    world = World(config["symbols"])
    decision = DecisionEngine(config)
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
