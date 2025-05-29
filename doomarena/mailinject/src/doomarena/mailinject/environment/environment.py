from typing import Callable
import logging

from tapeagents.environment import Environment
from tapeagents.core import Action
from tapeagents.dialog_tape import AssistantStep, UserStep

from ..types import (
    SubmissionResult,
    Email,
    LLMailTape,
    ListEmails,
    ListedEmailsResults,
    ParsingFailure,
    SendEmail,
    SendEmailResults,
    SearchEmail,
)
from .bm25 import email_retrieval

logger = logging.getLogger(__name__)


class LLMailEnvironment(Environment[LLMailTape]):
    def __init__(self, emails: list[Email], challenge_mode: None | Callable = None):
        self.emails = emails
        self.challenge_mode = challenge_mode

    def react(self, tape: LLMailTape) -> LLMailTape:
        new_tape = tape.model_copy(deep=True)

        action = tape.last_action
        assert isinstance(
            action, Action
        ), f"Last tape step should be an action for environment to react. Got {action}."

        if isinstance(action, SendEmail):
            logger.info(
                f"Sent email: TO: {action.email.to}\nCONTENT: {action.email.content}"
            )
            new_tape.steps.append(SendEmailResults())

            if self.challenge_mode:
                logger.info(
                    f"Evaluating challenge success for email {action.llm_dict()}"
                )
                success = self.challenge_mode(action.email)
                raise SubmissionResult(success)
        elif isinstance(action, ListEmails):
            if action.max == -1:
                emails = self.emails
            else:
                emails = self.emails[: action.max]
            # Add an observation
            new_tape.steps.append(ListedEmailsResults(emails=emails))
        elif isinstance(action, (AssistantStep)):
            if self.challenge_mode:
                raise SubmissionResult(False)

            logger.info(f"Assistant Sent Message: {action.content}")
            user_message = input("Enter your response: ")
            new_tape.steps.append(UserStep(content=user_message))
        elif isinstance(action, SearchEmail):
            emails = email_retrieval(corpus=self.emails, query=action.query)
            new_tape.steps.append((ListedEmailsResults(emails=emails)))
        elif isinstance(action, ParsingFailure):
            if self.challenge_mode:
                raise SubmissionResult(False)

            logger.info(f"Parsing Failure: {action.content}")
            # Agent will attempt to recover from parsing failure
        else:
            if self.challenge_mode:
                raise SubmissionResult(False)
            self.raise_unexpected_action(action)

        return new_tape
