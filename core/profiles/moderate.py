from .base import Profile


class ModerateProfile(Profile):
    name = "moderate"

    def apply(self, config: dict) -> dict:
        cfg = dict(config)

        cfg.update(
            {
                "stop_loss": -0.5,
                "take_profit": 1.2,
                "armed": True,
                "max_parallel_positions": 2,
                "cooldown_after_loss": 300,
            }
        )

        return cfg
