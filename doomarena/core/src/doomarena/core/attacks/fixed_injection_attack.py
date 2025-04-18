from typing import Literal
from doomarena.core.attacks.attacks import Attacks
from doomarena.core.attacks import register_attacks


@register_attacks("fixed_injection_attack")
class FixedInjectionAttack(Attacks):
    attack_name: Literal["fixed_injection_attack"] = "fixed_injection_attack"
    injection_str: str

    def get_next_attack(self, **kwargs) -> str:
        return self.injection_str
