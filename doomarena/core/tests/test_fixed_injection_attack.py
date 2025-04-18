import pytest
from doomarena.core.attacks import (
    FixedInjectionAttack,
)
from doomarena.core.attacks import ATTACK_REGISTRY


# Test for the constructor and initial state
def test_fixed_injection_attack_init():
    injection_str = "attack_payload"
    attack_instance = FixedInjectionAttack(injection_str=injection_str)

    assert attack_instance.injection_str == injection_str


# Test for get_next_attack method
def test_get_next_attack():
    injection_str = "attack_payload"
    attack_instance = FixedInjectionAttack(injection_str=injection_str)

    assert attack_instance.get_next_attack() == injection_str
    # Ensure the method consistently returns the same string
    assert attack_instance.get_next_attack() == injection_str


# Test that the class is correctly registered
def test_fixed_injection_attack_registration():
    assert "fixed_injection_attack" in ATTACK_REGISTRY
    assert ATTACK_REGISTRY["fixed_injection_attack"] == FixedInjectionAttack


if __name__ == "__main__":
    pytest.main(["-v", __file__])
