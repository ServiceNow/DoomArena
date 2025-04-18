from typing import List, Dict, Literal, Any
from doomarena.core.attacks.attacks import Attacks
from doomarena.core.attacks import register_attacks
from litellm import completion
from openai import BaseModel, OpenAIError
from tenacity import retry, wait_random_exponential, stop_after_attempt


# Add these functions before the FewShotToolCallingAgent class
def retry_if_rate_limit_error(exception):
    return isinstance(exception, OpenAIError) and "token rate limit" in str(exception)


@retry(
    wait=wait_random_exponential(min=1, max=30),
    stop=stop_after_attempt(10),
    retry=retry_if_rate_limit_error,
)
def generate_with_backoff(**kwargs):
    return completion(**kwargs)


class AdversarialUserAgentSimulator(BaseModel):
    messages: List[Dict[str, Any]] = []
    model: str
    provider: str
    system_prompt: str

    def generate_next_message(self, messages: List[Dict[str, Any]]) -> str:
        res = generate_with_backoff(
            model=self.model, custom_llm_provider=self.provider, messages=messages
        )
        message = res.choices[0].message
        self.messages.append({"role": "assistant", "content": message.content})
        return message.content

    def step(self, content: List[Dict[str, Any]]) -> str:
        if not self.messages:
            self.messages.append({"role": "system", "content": self.system_prompt})

        self.messages.extend(content)
        return self.generate_next_message(self.messages)


@register_attacks("adversarial_user_agent_attack")
class AdversarialUserAgentAttack(Attacks):
    """Represents a sequence of attacks by a malicious user agent"""

    attack_name: Literal["adversarial_user_agent_attack"] = (
        "adversarial_user_agent_attack"
    )
    model: str
    provider: str
    system_prompt: str
    adversarial_user: AdversarialUserAgentSimulator | None = None

    def model_post_init(self, __config: Any) -> None:
        self.adversarial_user = AdversarialUserAgentSimulator(
            model=self.model, provider=self.provider, system_prompt=self.system_prompt
        )

    def get_next_attack(self, **kwargs) -> str:
        return self.adversarial_user.step(kwargs["conversational_history"])
