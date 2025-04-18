import pytest
from doomarena.core.attack_gateways.attack_gateway import AttackGateway
from doomarena.core.attack_gateways.register_attack_gateway import (
    register_attack_gateway,
    ATTACK_GATEWAY_REGISTRY,
)
from doomarena.core.attack_gateways.get_attack_gateway import (
    get_attack_gateway,
)


# Mock Env class for testing
class MockEnv:
    def __init__(self):
        self.attribute = "test_value"


# Mock Gateway class for testing
class MockAttackGateway(AttackGateway):
    def reset(self, **kwargs):
        return "reset_called"

    def step(self, **kwargs):
        return "step_called"

    def attack_success(self):
        return True


@pytest.fixture(autouse=True)
def clear_registry():
    """Fixture to clear the ATTACK_GATEWAY_REGISTRY before each test."""
    ATTACK_GATEWAY_REGISTRY.clear()


# Tests for attack_gateway.py
def test_dynamic_attribute_delegation():
    env = MockEnv()
    gateway = MockAttackGateway(env, attack_configs=[])
    assert gateway.attribute == "test_value"


def test_attribute_error_for_nonexistent_attribute():
    env = MockEnv()
    gateway = MockAttackGateway(env, attack_configs=[])
    with pytest.raises(AttributeError):
        _ = gateway.nonexistent_attribute


def test_abstract_methods():
    with pytest.raises(TypeError):
        AttackGateway(MockEnv(), attack_configs=[])


def test_subclass_implementation():
    gateway = MockAttackGateway(MockEnv(), attack_configs=[])
    assert gateway.reset() == "reset_called"
    assert gateway.step() == "step_called"
    assert gateway.attack_success()


# Tests for register_attack_gateway.py
def test_registration_functionality():
    @register_attack_gateway("mock_gateway")
    class MockGateway:
        pass

    assert "mock_gateway" in ATTACK_GATEWAY_REGISTRY
    assert ATTACK_GATEWAY_REGISTRY["mock_gateway"] is MockGateway


def test_registry_overwrite():
    @register_attack_gateway("mock_gateway")
    class MockGateway1:
        pass

    @register_attack_gateway("mock_gateway")
    class MockGateway2:
        pass

    assert (
        ATTACK_GATEWAY_REGISTRY["mock_gateway"] is not MockGateway1
        and ATTACK_GATEWAY_REGISTRY["mock_gateway"] is MockGateway2
    )


def test_decorator_does_not_alter_class():
    @register_attack_gateway("mock_gateway")
    class MockGateway:
        def method(self):
            return "method_called"

    gateway = MockGateway()
    assert gateway.method() == "method_called"


# Tests for get_attack_gateway.py
def test_valid_gateway_retrieval():
    @register_attack_gateway("mock_gateway")
    class MockGateway:
        def __init__(self, arg1):
            self.arg1 = arg1

    gateway = get_attack_gateway("mock_gateway", arg1="test_value")
    assert gateway.arg1 == "test_value"


def test_invalid_gateway_retrieval():
    with pytest.raises(
        ValueError, match="Attack Gateway 'nonexistent_gateway' is not registered."
    ):
        get_attack_gateway("nonexistent_gateway", arg1="test_value")


def test_error_handling():
    with pytest.raises(
        ValueError, match="Attack Gateway 'nonexistent_gateway' is not registered."
    ):
        get_attack_gateway("nonexistent_gateway", value="test")


if __name__ == "__main__":
    pytest.main(["-v", __file__])
