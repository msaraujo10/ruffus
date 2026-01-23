from core.strategies.simple_trend import SimpleTrendStrategy


STRATEGIES = {
    "simple_trend": SimpleTrendStrategy,
}


def load_strategy(name: str, config: dict):
    if name not in STRATEGIES:
        raise ValueError(f"Estratégia desconhecida: {name}")

    return STRATEGIES[name](config)
