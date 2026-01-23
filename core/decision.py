class DecisionEngine:
    """
    Adaptador entre o Engine e as Strategies.
    """

    def __init__(self, strategy):
        self.strategy = strategy

    def export(self) -> dict:
        return {
            "strategy": self.strategy.export(),
        }

    def import_state(self, data: dict | None):
        if not data:
            return
        if "strategy" in data:
            self.strategy.import_state(data["strategy"])

    def decide(self, state, world: dict):
        return self.strategy.decide(world, state)
