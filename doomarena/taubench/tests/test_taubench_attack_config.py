import pytest
from typing import Literal
from unittest.mock import MagicMock
from doomarena.core.attack_config.attack_config import (
    AttackConfig,
)
from doomarena.core.success_filters import (
    AlwaysTrueSuccessFilter,
)
from doomarena.core.filters import AlwaysTrueFilter
from doomarena.core.attacks.attacks import Attacks


class MockAttack(Attacks):
    attack_name: Literal["mock_attack"] = "mock_attack"

    def get_next_attack(self, **kwargs):
        return "attack"


# Test for AttackConfig initialization and attributes
def test_taubench_attack_config_init():
    attackable_component = {"component_key": "component_value"}
    attack = MockAttack()  # Mocked attack instance

    filter_function = AlwaysTrueFilter()
    success_function = AlwaysTrueSuccessFilter()

    config_instance = AttackConfig(
        attackable_component=attackable_component,
        attack=attack,
        filter=filter_function,
        success_filter=success_function,
    )

    assert config_instance.attackable_component == attackable_component
    assert config_instance.attack == attack
    assert config_instance.filter == filter_function
    assert config_instance.success_filter == success_function


# Test for get_attack_config with AttackConfig
def test_get_taubench_attack_config():

    attackable_component = {"component_key": "component_value"}
    attack = MockAttack()  # Mocked attack instance

    config_instance = AttackConfig(
        attackable_component=attackable_component,
        attack=attack,
        filter=AlwaysTrueFilter(),
        success_filter=AlwaysTrueSuccessFilter(),
    )

    assert isinstance(config_instance, AttackConfig)
    assert config_instance.attackable_component == attackable_component
    assert config_instance.attack == attack


if __name__ == "__main__":
    pytest.main(["-v", __file__])
