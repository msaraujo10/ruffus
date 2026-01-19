import json
import time
from core.state_machine import StateMachine
from core.engine import Engine
from core.decision import DecisionEngine
from core.risk import RiskManager
from brokers.virtual import VirtualBroker

# --- Main Execution ---

def main():
    print("🧠 RUFFUS — V2 ESTÁVEL (MODO VIRTUAL)")

    with open("config/config.json", "r", encoding="utf-8") as f:
        config = json.load(f)

    broker = VirtualBroker(start_price=1.0)
    decision = DecisionEngine(config)
    risk = RiskManager(config)
    engine = Engine(broker, decision, risk)

    sm = StateMachine(engine)

    while True:
        sm.tick()
        time.sleep(1)


if __name__ == "__main__":
    main()
