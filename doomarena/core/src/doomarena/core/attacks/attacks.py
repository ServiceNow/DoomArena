from typing import Any
from abc import ABC, abstractmethod
from pydantic import BaseModel


class Attacks(BaseModel, ABC):

    attack_name: str  # must override in subclass

    @abstractmethod
    def get_next_attack(self, **kwargs) -> Any:
        raise NotImplementedError
