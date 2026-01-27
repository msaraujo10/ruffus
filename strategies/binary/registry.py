from strategies.binary.base import BaseBinaryStrategy
from strategies.binary.impulse import ImpulseBinary


class NullBinaryStrategy(BaseBinaryStrategy):
    name = "null-binary"
    pass


def load_binary_strategies(name=None, config=None):
    symbols = config["symbols"]

    if name == "impulse":
        return ImpulseBinary(symbols)

    # fallback seguro
    return ImpulseBinary(symbols, probability=0.01)
