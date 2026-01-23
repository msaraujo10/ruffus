class Profile:
    """
    Contrato base de um perfil operacional.
    """

    name: str = "base"

    def apply(self, config: dict) -> dict:
        """
        Recebe o config base e retorna um novo config
        ajustado conforme o perfil.
        """
        return dict(config)
