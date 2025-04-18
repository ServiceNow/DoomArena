from typing import Literal
from doomarena.core.success_filters import SuccessFilter


class AlwaysTrueSuccessFilter(SuccessFilter):
    success_filter_name: Literal["always_true"] = "always_true"

    def __call__(self, *args, **kwargs) -> bool:
        return True
