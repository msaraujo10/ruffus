import time

from core.engine import Engine
from core.decision import DecisionEngine
from core.risk import RiskManager
from core.world import World

from adapters.virtual import VirtualBroker
from storage.store_json import StoreJSON


def main():
    print("🧠 RUFFUS — V2 ESTÁVEL (MODO VIRTUAL + PERSISTENTE)")

    config = {
        "stop_loss": -0.5,
        "take_profit": 1.2,
        "sleep": 1,
        "symbols": ["BTCUSDT", "ETHUSDT", "SOLUSDT"],
    }

    # Infraestrutura
    broker = VirtualBroker(config["symbols"])
    world = World(config["symbols"])
    decision = DecisionEngine(config)
    risk = RiskManager(config)
    store = StoreJSON("storage/state.json")

    # Núcleo
    engine = Engine(
        broker=broker,
        world=world,
        decision=decision,
        risk=risk,
        store=store,
    )

    # Boot com restauração automática
    engine.boot()

    while True:
        try:
            # Simula feed de mercado multi-ativo
            feed = broker.tick()  # ex: {"BTCUSDT": 1.01, "ETHUSDT": 0.99, ...}

            engine.tick(feed)

            time.sleep(config["sleep"])

        except KeyboardInterrupt:
            print("\n⏹ Execução interrompida.")
            break


if __name__ == "__main__":
    main()
