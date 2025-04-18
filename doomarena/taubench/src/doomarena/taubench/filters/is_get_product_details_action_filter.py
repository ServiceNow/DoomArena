from typing import Literal
from doomarena.core.filters import AttackFilter


class IsGetProductDetailsActionFilter(AttackFilter):
    filter_name: Literal["is_get_product_details_action_filter"] = (
        "is_get_product_details_action_filter"
    )

    def __call__(self, action):
        return action.name == "get_product_details"
