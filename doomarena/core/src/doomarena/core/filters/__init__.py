from abc import abstractmethod
from pydantic import BaseModel


class AttackFilter(BaseModel):
    filter_name: str

    @abstractmethod
    def __call__(self, *args, **kwargs) -> bool:
        raise NotImplementedError


from .always_true_filter import AlwaysTrueFilter
