from abc import abstractmethod
from typing import Literal
from doomarena.core.attack_config.attack_config import AttackConfig
from doomarena.core.attack_gateways.attack_gateway import AttackGateway
from doomarena.core.attacks.attacks import Attacks
from doomarena.mailinject.environment.assets import EMAILS_1, EMAILS_2, EMAILS_3
from doomarena.mailinject.environment.environment import LLMailEnvironment
from doomarena.mailinject.experiments import run_mailinject_testcase
from doomarena.mailinject.success_filters import EmailDestinationAndBodyOk
from doomarena.mailinject.types import MailInjectTestCase
from tapeagents.llms import LLM




class LLMailAttackGateway(AttackGateway):

    def __init__(self, 
                 scenario: Literal["1", "2", "3"],
                 llm: LLM,
                 attack_configs: list[AttackConfig] | None = None, 
                 defenses: list | None = None,
                 success_filters: list| None = None):
        
        assert scenario in ["1", "2", "3"], "Scenario must be one of '1', '2', or '3'"
        self.attack_configs = attack_configs or []
        self.defenses = defenses or []
        self.scenario = scenario
        self.success_filters = success_filters or []
        self.llm = llm

        # initialize environment and inject attacks
        self.reset()

    def reset(self):

    def step(self, **kwargs):
        pass # not used

    def run_experiment(self, tape):
        run_mailinject_testcase(self.experiment_args)