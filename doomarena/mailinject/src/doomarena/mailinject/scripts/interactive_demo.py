"""
This is a basic script just for manually interacting with the agent and the environment.
"""

import logging
import os

from doomarena.mailinject.scripts.llm_configs import MODEL_FOR_TESTING


from tapeagents.llms import LiteLLM
from tapeagents.dialog_tape import AssistantStep, UserStep
from tapeagents.orchestrator import main_loop

from doomarena.mailinject.agent import LLMailAgent
from doomarena.mailinject.environment import LLMailEnvironment
from doomarena.mailinject.types import LLMailTape
from doomarena.mailinject.environment.assets import GPT4o_GENERATED_EMAILS_V1

from doomarena.mailinject.scripts.llm_configs import MODEL_FOR_TESTING

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,  # Set the logging level to DEBUG
        format="%(asctime)s - %(levelname)s - %(message)s",  # Customize the format
    )

    env = LLMailEnvironment(emails=GPT4o_GENERATED_EMAILS_V1)

    llm = MODEL_FOR_TESTING

    start_tape = LLMailTape(
        steps=[
            AssistantStep(
                content="Welcome! I'm here to streamline your inbox. Let me know if you need summaries, answers, or emails sent."
            ),
            UserStep(content="Summarize the two most recent emails"),
        ]
    )

    agent = LLMailAgent.create(llm=llm, templates={})

    final_tape = main_loop(agent, start_tape, env, max_loops=3).get_final_tape()
    print(final_tape)
