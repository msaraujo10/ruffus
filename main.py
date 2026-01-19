import time

from core.engine import Engine
from core.decision import DecisionEngine
from core.risk import RiskManager
from core.world import World
from adapters.virtual import VirtualBroker


def main():
    print("🧠 RUFFUS — V2 ESTÁVEL (MODO VIRTUAL | MULTI-ATIVO)")

    config = {
        "stop_loss": -0.5,
        "take_profit": 1.2,
        "sleep": 1,
        "symbols": ["BTCUSDT", "ETHUSDT", "SOLUSDT"],
    }

    broker = VirtualBroker(config["symbols"])
    decision = DecisionEngine(config)
    risk = RiskManager(config)

    world = World(config["symbols"])
    engine = Engine(broker, decision, risk, config["symbols"])

    engine.boot()

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
