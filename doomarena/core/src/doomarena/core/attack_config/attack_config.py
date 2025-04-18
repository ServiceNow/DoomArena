from typing import Any, final
from pydantic import BaseModel
from ..attacks.attacks import Attacks
from doomarena.core.filters import AttackFilter
from doomarena.core.success_filters import SuccessFilter


@final
class AttackConfig(BaseModel):
    """
    A class to represent an attack configuration.

    Attributes:
        attackable_component: The attack component object (optional).
        attack: The attack object.
        filter: A callable filter function (optional).
        success_filter: A callable to determine attack success (optional).
    """

    attackable_component: dict  # TODO: replace with pydantic
    attack: Attacks
    filter: AttackFilter | None = None
    success_filter: SuccessFilter
