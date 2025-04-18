from doomarena.core.attacks.attacks import Attacks
from doomarena.core.attacks import register_attacks
from typing import Any, Literal


@register_attacks("fixed_injection_sequence_attacks")
class FixedInjectionSequenceAttacks(Attacks):
    """Represents a sequence of attacks with their expected responses"""

    attack_name: Literal["fixed_injection_sequence_attacks"] = (
        "fixed_injection_sequence_attacks"
    )

    current_index: int = 0
    injection_sequence: Any  # todo: find the right type
    fallback_instruction: Any  # todo: find the right type

    def get_next_attack(self, **kwargs) -> str:
        if self.current_index < len(self.injection_sequence):
            instruction = self.injection_sequence[self.current_index]
            self.current_index += 1
            return instruction
        return self.fallback_instruction
