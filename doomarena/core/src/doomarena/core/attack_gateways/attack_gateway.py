from abc import ABC, abstractmethod
from doomarena.core.attack_config.attack_config import AttackConfig
import logging
from typing import Any, List


class AttackGateway(ABC):
    def __init__(self, env, attack_configs: List[AttackConfig]):
        self.attack_configs = attack_configs
        self.env = env
        self.run_success_filter_setups(attack_configs)

    def run_success_filter_setups(self, attack_configs: List[AttackConfig]):
        for attack_config in attack_configs:
            if hasattr(attack_config.success_filter, "setup_success_filter"):
                attack_config.success_filter.setup_success_filter()
        logging.info("Success filter setups complete")

    def __getattr__(self, name):
        # Dynamically delegate to env class
        if hasattr(self.env, name):
            return getattr(self.env, name)
        raise AttributeError(
            f"'{type(self).__name__}' object has no attribute '{name}'"
        )

    @abstractmethod
    def reset(self, **kwargs) -> Any:
        raise NotImplementedError

    @abstractmethod
    def step(self, **kwargs) -> Any:
        raise NotImplementedError

    # @abstractmethod  # making it optional / some gateways may not need this
    def attack_success(self, **kwargs) -> bool:
        # Return whether any attack has been successful
        raise NotImplementedError
