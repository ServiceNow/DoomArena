import pytest
from unittest.mock import MagicMock, patch
from doomarena.core.attacks.adversarial_user_agent_attack import (
    AdversarialUserAgentAttack,
    AdversarialUserAgentSimulator,
)
from doomarena.core.attacks import ATTACK_REGISTRY


# Test for the constructor and initial state
def test_adversarial_user_agent_attack_init():
    model = "test-model"
    provider = "test-provider"
    system_prompt = "test-system-prompt"

    attack_instance = AdversarialUserAgentAttack(
        model=model, provider=provider, system_prompt=system_prompt
    )

    assert attack_instance.model == model
    assert attack_instance.provider == provider
    assert attack_instance.system_prompt == system_prompt
    assert isinstance(attack_instance.adversarial_user, AdversarialUserAgentSimulator)


# Test that the class is correctly registered
def test_adversarial_user_agent_attack_registration():
    assert "adversarial_user_agent_attack" in ATTACK_REGISTRY
    assert (
        ATTACK_REGISTRY["adversarial_user_agent_attack"] == AdversarialUserAgentAttack
    )


# Test for get_next_attack method
@patch("doomarena.core.attacks.adversarial_user_agent_attack.generate_with_backoff")
def test_get_next_attack(mock_generate_with_backoff):
    mock_generate_with_backoff.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content="mock_attack_payload"))]
    )

    attack_instance = AdversarialUserAgentAttack(
        model="test-model", provider="test-provider", system_prompt="test-system-prompt"
    )

    conversational_history = [{"role": "user", "content": "history_item"}]
    result = attack_instance.get_next_attack(
        conversational_history=conversational_history
    )

    mock_generate_with_backoff.assert_called_once()
    assert result == "mock_attack_payload"


if __name__ == "__main__":
    pytest.main(["-v", __file__])
