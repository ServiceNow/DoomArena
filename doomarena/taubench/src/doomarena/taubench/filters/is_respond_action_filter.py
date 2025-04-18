from typing import Literal
from doomarena.core.filters import AttackFilter


class IsRespondActionFilter(AttackFilter):
    filter_name: Literal["is_respond_action_filter"] = "is_respond_action_filter"

    def __call__(self, action):
        return action.name == "respond"
