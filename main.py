import time

from core.engine import Engine
from adapters.virtual import VirtualBroker


def main():
    print("🧠 RUFFUS — V2 ESTÁVEL (MODO VIRTUAL)")

    # Configuração mínima inline (depois vira arquivo)
    config = {
        "stop_loss": -0.5,
        "take_profit": 1.2,
        "sleep": 1,
    }

    broker = VirtualBroker()
    engine = Engine(broker, config)

    while True:
        try:
            price = broker.tick()

            market = {
                "price": price,
            }

            engine.tick(market)

            time.sleep(config["sleep"])

        except KeyboardInterrupt:
            print("\n⏹ Execução interrompida.")
            break


if __name__ == "__main__":
    main()
