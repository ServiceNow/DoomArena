from typing import Annotated, Literal, Union
from pydantic import BaseModel, Field
from tapeagents.core import Action, Observation, Prompt, SetNextNode, Tape
from tapeagents.dialog_tape import AssistantStep, UserStep
from tapeagents.llms import LLM

from doomarena.core.success_filters import SuccessFilter


class Email(BaseModel):
    to: str = ""
    from_: str = ""
    subject: str = ""
    content: str

    def llm_dict(self):
        d = {}
        if self.to:
            d["to"] = self.to
        if self.from_:
            d["from"] = self.from_
        d["content"] = self.content
        return d


class ListedEmailsResults(Observation):
    kind: Literal["listed_emails_results"] = "listed_emails_results"
    emails: list[Email]

    def llm_dict(self):
        return {
            "kind": "listed_emails_results",
            "emails": [email.llm_dict() for email in self.emails],
        }


class SendEmail(Action):
    kind: Literal["send_email"] = "send_email"
    email: Email


class ListEmails(Action):
    kind: Literal["list_emails"] = "list_emails"
    max: int = -1  # most recent or all


class SearchEmail(Action):
    kind: Literal["search_email"] = "search_email"
    query: str


class ParsingFailure(Action):
    kind: Literal["parsing_failure"] = "parsing_failure"
    content: str = ""
    raw_output: str = ""
    cleaned_output: str = ""


PossibleActions = Annotated[
    Union[ListedEmailsResults | SendEmail | ListEmails | AssistantStep | SearchEmail],
    Field(discriminator="kind"),
]


class SendEmailResults(Observation):
    kind: Literal["send_email_results"] = "send_email_results"
    content: str = "Email sent successfully"


LLMailStep = Annotated[
    Union[
        AssistantStep,
        UserStep,
        SendEmail,
        ListEmails,
        ListedEmailsResults,
        ParsingFailure,
        SetNextNode,
        SendEmailResults,
        SearchEmail,
    ],
    Field(discriminator="kind"),
]


class LLMailTape(Tape[None, LLMailStep]):
    @property
    def last_action(self) -> LLMailStep | None:
        # Iterate over the steps in reverse order to find the last action
        for step in reversed(self.steps):
            if isinstance(step, Action):
                return step
        return None

    @property
    def last_user_message(self) -> UserStep | None:
        # Iterate over the steps in reverse order to find the last action
        for step in reversed(self.steps):
            if isinstance(step, UserStep):
                return step
        return None


class SubmissionResult(Exception):
    def __init__(self, result):
        self.result = result


class Results(BaseModel):
    agent_successful: bool


class MailInjectTestCase(BaseModel):
    user_message: str
    success_filter: SuccessFilter | dict[str, SuccessFilter] | list[SuccessFilter] = {}
    emails: list[Email]
    max_loops: int = 3
    defenses: list[str] = []

    # for storing results only
    results: Results | None = None
    final_tape: LLMailTape | None = None
    llm: LLM | str | None = None

    def model_post_init(self, context):
        if isinstance(self.success_filter, SuccessFilter):
            self.success_filter = {
                self.success_filter.success_filter_name: self.success_filter
            }
        elif isinstance(self.success_filter, list):
            self.success_filter = {
                success_filter.success_filter_name: success_filter
                for success_filter in self.success_filter
            }
