from tau_bench.envs.user import BaseUserSimulationEnv


class AdversarialUserSimulationEnv(BaseUserSimulationEnv):
    """
    A simulation environment for adversarial user interactions.
    """

    def __init__(self) -> None:
        self.total_cost = 0.0

    def reset(self, instruction: str) -> str:
        """
        Resets the state of the object with the given instruction.

        Returns:
            str: An empty string indicating the reset operation.
        """
        return ""

    def step(self, content: str, instruction) -> str:
        """
        Simulates a step in an interaction by printing the assistant's content and the user's instruction, then returning the instruction.

        Args:
            content (str): The content to be displayed as the assistant's response.
            instruction: The user's instruction or input.

        Returns:
            str: The user's instruction.
        """
        print(f"\n\nASSISTANT:{content}\n\nUSER: {instruction}")
        return instruction

    def get_total_cost(self) -> float:
        """
        Retrieve the total cost.

        Returns:
            float: The total cost value.
        """
        return self.total_cost
