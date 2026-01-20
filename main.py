import time
import json

from core.engine import Engine
from core.decision import DecisionEngine
from core.risk import RiskManager
from core.world import World
from storage.store_json import JSONStore

from adapters.virtual import VirtualBroker
from adapters.bybit import BybitObserver


MODE = "VIRTUAL"  # "VIRTUAL" | "REAL_OBSERVER"


def main():
    print(f"🧠 RUFFUS — V2 ESTÁVEL ({MODE})")

    with open("config/config.json", "r") as f:
        config = json.load(f)

    symbols = config["symbols"]

    # Persistência
    store = JSONStore("data/state.json")

    # Domínio
    world = World(symbols, store)
    decision = DecisionEngine(config)
    risk = RiskManager(config)

    # Fonte de mercado
    if MODE == "VIRTUAL":
        broker = VirtualBroker(symbols)

    elif MODE == "REAL_OBSERVER":
        with open("config/bybit.json", "r") as f:
            keys = json.load(f)

        broker = BybitObserver(
            symbols=symbols,
            api_key=keys["api_key"],
            api_secret=keys["api_secret"],
            testnet=keys.get("testnet", False),
        )

    else:
        raise ValueError("MODE inválido")

    # Orquestrador
    engine = Engine(
        broker=broker,
        world=world,
        decision=decision,
        risk=risk,
        store=store,
    )

    engine.boot()

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
