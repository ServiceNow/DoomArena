import pytest
from doomarena.core.attacks.attacks import Attacks
from doomarena.core.attacks.register_attacks import (
    ATTACK_REGISTRY,
    register_attacks,
)
from doomarena.core.attacks import get_attacks
from typing import Literal


@register_attacks("dummy_attack")
class RegisteredDummyAttack(Attacks):
    attack_name: Literal["registed_dummy_attack"] = "registed_dummy_attack"

    def get_next_attack(self, **kwargs):
        return "dummy attack"


# Tests for attacks.py
def test_attacks_abstract_class():
    with pytest.raises(TypeError):
        instance = (
            Attacks()
        )  # This should raise TypeError because it's an abstract class


# Tests for register_attacks.py
def test_register_attacks_decorator():
    assert "dummy_attack" in ATTACK_REGISTRY
    assert ATTACK_REGISTRY["dummy_attack"] == RegisteredDummyAttack


# Tests for get_attacks.py
def test_get_attacks_unregistered():
    with pytest.raises(ValueError) as excinfo:
        get_attacks("unregistered_attack")
    assert "Attack 'unregistered_attack' is not registered." in str(excinfo.value)


def test_get_attacks_registered():
    instance = get_attacks("dummy_attack")
    assert isinstance(instance, RegisteredDummyAttack)
    assert instance.get_next_attack() == "dummy attack"


if __name__ == "__main__":
    pytest.main(["-v", __file__])
