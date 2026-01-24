import time
import os
import json

from core.engine import Engine
from core.state_machine import State
from core.risk import RiskManager
from core.world import World
from core.profiles.registry import load_profile
from core.strategies.registry import load_strategy

from tools.feedback import FeedbackEngine
from tools.memory import CognitiveMemory
from tools.panel import Panel

from adapters.virtual import VirtualBroker
from adapters.bybit import BybitBroker
from storage.store_json import JSONStore


# Modo inicial apenas como “intenção de boot”
# OBSERVADOR | REAL | VIRTUAL | ASSISTED
MODE = "OBSERVADOR"


def main():
    print(f"🧠 RUFFUS — V2 ESTÁVEL ({MODE})")

    # ----------------------------
    # Diagnóstico cognitivo
    # ----------------------------
    memory = CognitiveMemory()
    health = memory.health()

    # ----------------------------
    # Configuração base
    # ----------------------------
    config = {
        "profile": "moderate",
        "stop_loss": -0.5,
        "take_profit": 1.2,
        "sleep": 1,
        "symbols": ["BTCUSDT", "ETHUSDT", "SOLUSDT"],
        "store_path": "storage/state.json",
        "armed": True,
        "strategy": "simple_trend",
    }

    # ----------------------------
    # Aplicação de Perfil
    # ----------------------------
    profile_name = config.get("profile", "moderate")
    profile = load_profile(profile_name)
    config = profile.apply(config)

    print(f"🧬 Perfil ativo: {profile.name}")

    # ----------------------------
    # Broker conforme modo inicial
    # ----------------------------
    if MODE == "VIRTUAL":
        broker = VirtualBroker(config["symbols"])

    elif MODE == "OBSERVADOR":
        broker = BybitBroker(
            config["symbols"],
            mode="OBSERVADOR",
            armed=config.get("armed", False),
        )

    elif MODE in ("REAL", "ASSISTED"):
        broker = BybitBroker(
            config["symbols"],
            mode="REAL",
            armed=config.get("armed", False),
        )

    else:
        raise ValueError("MODE inválido")

    # ----------------------------
    # Domínio
    # ----------------------------
    store = JSONStore(config["store_path"])
    world = World(config["symbols"], store)
    strategy = load_strategy(config.get("strategy", "simple_trend"), config)
    risk = RiskManager(config)
    feedback = FeedbackEngine("storage/events.jsonl")

    # ----------------------------
    # Engine
    # ----------------------------
    engine = Engine(
        broker=broker,
        world=world,
        strategy=strategy,
        risk=risk,
        store=store,
        feedback=feedback,
        mode=MODE,
    )

    # ----------------------------
    # Aplicação do diagnóstico
    # ----------------------------
    if health == "RISK_BLOCKED":
        print("🔴 Sistema em estado RISK_BLOCKED.")
        engine.set_mode("PAUSED")

    elif health == "UNSTABLE":
        print("🟠 Sistema instável.")
        engine.set_mode("OBSERVADOR")

    # ----------------------------
    # Replay automático em VIRTUAL
    # ----------------------------
    if engine.mode == "VIRTUAL":
        replay()
        return

    # ----------------------------
    # Boot
    # ----------------------------
    engine.boot()

    # ----------------------------
    # Painel
    # ----------------------------
    panel = Panel(engine)

    # ----------------------------
    # Loop principal
    # ----------------------------
    while True:
        try:
            feed = broker.tick()

            engine.step(feed)
            panel.render()

            # Operação assistida
            if engine.state.current().name == "AWAIT_CONFIRMATION":
                cmd = input("Confirmar [c] / Cancelar [x]: ").strip().lower()

                if cmd == "c":
                    engine.confirm()
                elif cmd == "x":
                    engine.cancel()

            time.sleep(config["sleep"])

        except KeyboardInterrupt:
            print("\n⏹ Execução interrompida.")
            break


def replay():
    print("🎞️  MODO REPLAY\n")

    path = "storage/events.jsonl"
    if not os.path.exists(path):
        print("Nenhum evento encontrado.")
        return

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            e = json.loads(line)

            ts = e.get("ts")
            state = e.get("state")
            action = e.get("action")
            result = e.get("result")

            if action:
                msg = f"{action['type']} {action['symbol']} @ {action['price']}"
            else:
                msg = "—"

            print(f"[REPLAY] {ts} | {state} | {msg} | {result}")


if __name__ == "__main__":
    main()
