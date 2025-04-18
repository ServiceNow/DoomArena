import pytest
from typing import Literal
from unittest.mock import Mock, MagicMock
from doomarena.taubench.attack_gateway import (
    TauBenchAttackGateway,
)
from doomarena.core.attack_config.attack_config import (
    AttackConfig,
)
from doomarena.core.filters import AttackFilter
from doomarena.core.success_filters import SuccessFilter
from doomarena.core.attacks.attacks import Attacks


@pytest.fixture
def mock_env():
    """Fixture for a mock environment."""
    env = Mock()
    # Mock task with ID and success status
    env.task = Mock()
    env.task.id = "test_id"
    env.task.instruction = "test_instruction"
    env.task.success = True
    return env


@pytest.fixture
def mock_user():
    """Fixture for a mock user."""
    return MagicMock()


class MyTestFilter(AttackFilter):
    filter_name: Literal["test_filter"] = "test_filter"

    def __call__(self, action):
        return action.kwargs.get("target") == "test_target"


class MyTestSuccessFilter(SuccessFilter):
    success_filter_name: Literal["test_success_filter"] = "test_success_filter"

    def __call__(self, gateway, actions=None):
        return True


class MyTestAttack(Attacks):
    attack_name: Literal["test_attack"] = "test_attack"

    def get_next_attack(self, **kwargs):
        return "test_attack"


@pytest.fixture
def attack_configs():
    """Fixture for mock attack configurations."""
    return [
        AttackConfig(
            attackable_component={
                "type": "database",
                "database_name": "test_db",
                "primary_key": "id",
                "nested_path": ["data"],
                "modification_type": "update",
            },
            attack=MyTestAttack(),
            filter=MyTestFilter(),
            success_filter=MyTestSuccessFilter(),
        )
    ]


@pytest.fixture
def taubench_attack_gateway(mock_env, mock_user, attack_configs):
    """Fixture for the TauBenchAttackGateway instance."""
    return TauBenchAttackGateway(
        env=mock_env, user=mock_user, attack_configs=attack_configs, task_name=None
    )


def test_check_if_db_name_and_pk_exist(taubench_attack_gateway, attack_configs):
    attack_config = attack_configs[0]
    result = taubench_attack_gateway.check_if_db_name_and_pk_exist(attack_config)
    assert result is True


def test_get_adv_env_action_modification(
    taubench_attack_gateway, mock_env, attack_configs
):
    mock_env.data = {"test_db": {"123": {"data": "original_value"}}}
    action = Mock()
    action.kwargs = {"id": "123"}
    attack_config = attack_configs[0]

    secret = taubench_attack_gateway._get_adv_env_action(action, attack_config)
    assert secret is None


def test_modify_field(taubench_attack_gateway):
    data = {"key1": {"key2": "value"}}
    keys = ["key1", "key2"]
    value = "modified_value"

    taubench_attack_gateway.modify_field(data, keys, value, "partial")
    assert data["key1"]["key2"] == "modified_value"


def test_modify_db_field(taubench_attack_gateway):
    database = {"123": {"key1": "value"}}
    keys = ["key1"]
    taubench_attack_gateway.modify_db_field(database, "123", keys, "new_value", "full")
    assert database["123"]["key1"] == "new_value"


def test_get_matching_attack_config(taubench_attack_gateway, attack_configs):
    action = Mock()
    action.kwargs = {"target": "test_target"}

    config, idx = taubench_attack_gateway.get_matching_attack_config(action)
    assert config == attack_configs[0]
    assert idx == 0


def test_reset(mock_env, taubench_attack_gateway):
    mock_env.reset.return_value = "reset_done"
    result = taubench_attack_gateway.reset(task_index=0)
    assert result == "reset_done"


def test_attack_success(taubench_attack_gateway):
    result = taubench_attack_gateway.attack_success()
    assert result is True


def test_attack_success_no_task_id():
    """Test attack success when task ID is not available."""
    # Create environment with task instruction only
    env = Mock()
    task_mock = Mock()
    task_mock.id = None  # Explicitly set task ID to None
    task_mock.instruction = "test_instruction"
    env.task = task_mock

    gateway = TauBenchAttackGateway(
        env=env,
        user=Mock(),
        attack_configs=[
            AttackConfig(
                attackable_component={"type": "test_component"},
                attack=MyTestAttack(),
                filter=MyTestFilter(),
                success_filter=MyTestSuccessFilter(),
            )
        ],
        task_name=None,
    )

    # Execute attack and verify success
    result = gateway.attack_success()
    assert result is True


if __name__ == "__main__":
    pytest.main(["-v", __file__])
