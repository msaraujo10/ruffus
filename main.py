import time
import json

from adapters.virtual import VirtualBroker
from storage.store_json import JSONStore

from core.engine import Engine
from core.world import World
from core.decision import DecisionEngine
from core.risk import RiskManager


def main():
    print("🧠 RUFFUS — V2 ESTÁVEL (MODO VIRTUAL | MULTI-ATIVO | PERSISTENTE)")

    # Carrega config
    with open("config/config.json", "r", encoding="utf-8") as f:
        config = json.load(f)

    symbols = config["symbols"]

    # Infra
    broker = VirtualBroker(symbols)
    store = JSONStore("data/state.json")

    # Domínio
    world = World(symbols, store)
    decision = DecisionEngine(config)
    risk = RiskManager(config)

    # Orquestrador
    engine = Engine(
        broker=broker,
        world=world,
        decision=decision,
        risk=risk,
        store=store,
    )

    # Boot com restauração
    engine.boot()

    while True:
        try:
            # Feed bruto do broker
            feed = broker.tick()

            # Atualiza o mundo
            world.update(feed)

            # Snapshot imutável
            snapshot = world.snapshot()

            # Ciclo do sistema
            engine.tick(snapshot)

            time.sleep(config.get("sleep", 1))

        except KeyboardInterrupt:
            print("\n⏹ Execução interrompida.")
            break


if __name__ == "__main__":
    main()
