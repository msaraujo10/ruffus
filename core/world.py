from core.state_machine import State


class World:
    """
    Representa o estado vivo do sistema:
    - preços por símbolo
    - estado por símbolo
    - preço de entrada por símbolo
    """

    def __init__(self, symbols: list[str], store):
        self.symbols = symbols
        self.store = store

        saved = self.store.load()

        self.prices = {s: None for s in symbols}
        self.states = {}
        self.entries = {}

        for s in symbols:
            data = saved.get(s, {})
            self.states[s] = State[data["state"]] if "state" in data else State.IDLE
            self.entries[s] = data.get("entry")

    def update(self, feed: dict):
        for symbol, price in feed.items():
            if symbol in self.prices:
                self.prices[symbol] = price

    def set_state(self, symbol: str, state: State):
        self.states[symbol] = state
        self.persist()

    def set_entry(self, symbol: str, price: float | None):
        self.entries[symbol] = price
        self.persist()

    def snapshot(self) -> dict:
        return {
            "prices": dict(self.prices),
            "states": dict(self.states),
            "entries": dict(self.entries),
        }

    def persist(self):
        data = {}
        for s in self.symbols:
            data[s] = {
                "state": self.states[s].name,
                "entry": self.entries.get(s),
            }
        self.store.save(data)
