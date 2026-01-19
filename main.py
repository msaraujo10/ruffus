import time

from core.engine import Engine
from core.decision import DecisionEngine
from core.risk import RiskManager
from core.state_machine import State
from adapters.virtual import VirtualBroker


def main():
    print("🧠 RUFFUS — V2 ESTÁVEL (MODO VIRTUAL)")

    config = {
        "stop_loss": -0.5,
        "take_profit": 1.2,
        "sleep": 1,
    }

    broker = VirtualBroker()
    decision = DecisionEngine(config)
    risk = RiskManager(config)

    engine = Engine(broker, decision, risk)
    engine.state.set(State.IDLE)

    while True:
        try:
            price = broker.tick()

            market = {
                "price": price,
                "symbol": "TESTE",
            }

            engine.tick(market)

            time.sleep(config["sleep"])

        except KeyboardInterrupt:
            print("\n⏹ Execução interrompida.")
            break


if __name__ == "__main__":
    main()
