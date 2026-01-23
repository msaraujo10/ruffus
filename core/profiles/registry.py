from .conservative import ConservativeProfile
from .moderate import ModerateProfile
from .aggressive import AggressiveProfile


_PROFILES = {
    "conservative": ConservativeProfile,
    "moderate": ModerateProfile,
    "aggressive": AggressiveProfile,
}


def load_profile(name: str):
    if not name:
        raise ValueError("Perfil não informado no config.")

    key = name.lower()
    if key not in _PROFILES:
        raise ValueError(f"Perfil inválido: {name}")

    return _PROFILES[key]()
