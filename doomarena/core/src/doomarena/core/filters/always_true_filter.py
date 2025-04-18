from typing import Literal
from doomarena.core.filters import AttackFilter


class AlwaysTrueFilter(AttackFilter):
    filter_name: Literal["always_true"] = "always_true"

    def __call__(self, *args, **kwargs) -> bool:
        return True
