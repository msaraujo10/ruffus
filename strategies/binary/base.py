# strategies/binary/base.py


class BaseBinaryStrategy:
    """
    Contrato mínimo para estratégias binárias.
    O Engine só exige:
    - decide(...)
    - adapt(...)
    - export()
    - import_state(...)
    """

    name = "base-binary"

    def decide(self, state, world, context=None):
        """
        Deve retornar:
        - dict(action) ou
        - None
        """
        return None

    def adapt(self, diagnosis: dict):
        """
        Recebe feedback pós-operação.
        Estratégias concretas DEVEM sobrescrever.
        """
        return

    def export(self) -> dict:
        """
        Estado persistente da estratégia.
        """
        return {}

    def import_state(self, data: dict | None):
        """
        Restaura estado persistido.
        """
        return
