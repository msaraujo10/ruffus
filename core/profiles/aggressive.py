from .base import Profile


class AggressiveProfile(Profile):
    name = "aggressive"

    def apply(self, config: dict) -> dict:
        cfg = dict(config)

        cfg.update(
            {
                "stop_loss": -1.0,
                "take_profit": 2.5,
                "armed": True,
                "max_parallel_positions": 4,
                "cooldown_after_loss": 60,
            }
        )

        return cfg
