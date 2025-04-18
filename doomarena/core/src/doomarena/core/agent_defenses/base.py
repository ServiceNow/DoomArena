from typing import List, Dict, Literal

from abc import ABC, abstractmethod

from pydantic import BaseModel


class SafetyCheck(ABC):
    @abstractmethod
    def check(self, messages: List[Dict[str, str]]) -> str:
        pass


class AttackSafetyCheck(BaseModel, ABC):

    defense_name: str
    abort_on_detection: bool = True

    @abstractmethod
    def attack_detected(self, messages: List[Dict[str, str]]) -> bool:
        pass


class AlwaysDetectedSafetyCheck(AttackSafetyCheck):
    defense_name: Literal["always_detected"] = "always_detected"

    def attack_detected(self, messages: List[Dict[str, str]]) -> bool:
        return True
