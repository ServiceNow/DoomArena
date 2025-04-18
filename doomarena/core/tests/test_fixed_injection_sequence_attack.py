import pytest
from typing import Literal
from doomarena.core.attacks.fixed_injection_sequence_attacks import (
    FixedInjectionSequenceAttacks,
)
from doomarena.core.attacks import ATTACK_REGISTRY


# Test for the constructor and initial state
def test_fixed_injection_sequence_attacks_init():
    sequence = ["attack1", "attack2"]
    fallback = "fallback"
    attack_instance = FixedInjectionSequenceAttacks(
        injection_sequence=sequence, fallback_instruction=fallback
    )

    assert attack_instance.injection_sequence == sequence
    assert attack_instance.fallback_instruction == fallback
    assert attack_instance.current_index == 0


# Test for getting next attack
def test_get_next_attack():
    sequence = ["attack1", "attack2"]
    fallback = "fallback"
    attack_instance = FixedInjectionSequenceAttacks(
        injection_sequence=sequence, fallback_instruction=fallback
    )

    assert attack_instance.get_next_attack() == "attack1"
    assert attack_instance.current_index == 1
    assert attack_instance.get_next_attack() == "attack2"
    assert attack_instance.current_index == 2
    assert attack_instance.get_next_attack() == fallback
    assert (
        attack_instance.current_index == 2
    )  # Ensure index doesn't increase after fallback


# Test that the class is correctly registered
def test_fixed_injection_sequence_attacks_registration():
    assert "fixed_injection_sequence_attacks" in ATTACK_REGISTRY
    assert (
        ATTACK_REGISTRY["fixed_injection_sequence_attacks"]
        == FixedInjectionSequenceAttacks
    )


if __name__ == "__main__":
    pytest.main(["-v", __file__])
