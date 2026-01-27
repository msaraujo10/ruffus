from strategies.canonical.simple_trend import SimpleTrendStrategy
from strategies.canonical.always_buy import AlwaysBuyStrategy


STRATEGIES = {
    "simple_trend": SimpleTrendStrategy,
    "always_buy": AlwaysBuyStrategy,
}


def load_strategy(name: str, config: dict):
    if name not in STRATEGIES:
        available = ", ".join(STRATEGIES.keys())
        raise ValueError(f"Estratégia desconhecida: {name}. Disponíveis: {available}")

    return STRATEGIES[name](config)
