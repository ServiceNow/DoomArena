from abc import abstractmethod
from typing import Literal
from doomarena.core.attacks.attacks import Attacks
from doomarena.mailinject.types import Email


class EmailAttack(Attacks):
    attack_name: Literal["email_attack"] = "email_attack"

    @abstractmethod
    def get_next_attack(self, **kwargs) -> Email:
        pass


class FixedEmailAttack(EmailAttack):
    attack_name: Literal["fixed_email_attack"] = "fixed_email_attack"
    email: Email

    def get_next_attack(self, **kwargs) -> Email:
        return self.email
