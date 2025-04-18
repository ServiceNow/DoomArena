from abc import abstractmethod
from pydantic import BaseModel


class SuccessFilter(BaseModel):
    success_filter_name: str

    @abstractmethod
    def __call__(self, *args, **kwargs) -> bool:
        raise NotImplementedError

    def setup_success_filter(self, *args, **kwargs):
        pass

    def get_goal_description(self):
        return ""


from .always_true_success_filter import AlwaysTrueSuccessFilter
