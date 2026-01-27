class BaseBinaryStrategy:
    name = "base-binary"

    def decide(self, state, world, context=None):
        return None

    def adapt(self, diagnosis):
        pass

    def export(self):
        return {}

    def import_state(self, data):
        pass
