from .base import Profile


class ConservativeProfile(Profile):
    name = "conservative"

    def apply(self, config: dict) -> dict:
        cfg = dict(config)

        cfg.update(
            {
                "stop_loss": -0.3,
                "take_profit": 0.6,
                "armed": True,
                "max_parallel_positions": 1,
                "cooldown_after_loss": 600,
            }
        )

        return cfg
