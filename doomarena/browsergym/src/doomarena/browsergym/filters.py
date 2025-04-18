from typing import Literal
from browsergym.core.env import BrowserEnv
from doomarena.core.filters import AttackFilter


class FilterByUrl(AttackFilter):
    filter_name: Literal["filter_by_url"] = "filter_by_url"
    allowed_urls: list[str]  # use ["*"] to allow all urls

    def __call__(self, observation: dict, env: BrowserEnv) -> bool:
        """Check if of the the page's urls is in the allowed urls"""
        pages = env.unwrapped.context.pages
        for page in pages:
            for url in self.allowed_urls:
                if url in page.url or url == "*":
                    return True
        return False


class StartAtStepFilter(AttackFilter):
    filter_name: Literal["start_at_step"] = "start_at_step"
    start_at_step: int = 1
    current_step: int = 0  # New attribute to store the current step

    def __call__(self, *args, **kwargs) -> bool:
        self.current_step += 1  # Store the current step
        return self.current_step >= self.start_at_step


class UsedOnceFilter(AttackFilter):
    filter_name: Literal["used_once"] = "used_once"
    used: bool = False

    def __call__(self, *args, **kwargs) -> bool:
        if self.used:
            return False
        self.used = True
        return True
