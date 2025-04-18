import requests
import json
import os


class LLMJudge:
    """
    LLMJudge is a class designed to interact with a language model for analyzing and interpreting
    conversation histories. It provides methods to format conversations, generate responses, and
    extract specific information such as refund status and refund amounts.

    Attributes:
    api_key (str): The API key for authenticating with OpenAI,
        retrieved from the environment variable "OPENAI_API_KEY".
    api_url (str): The base URL for the OpenAI API endpoint.
    model (str): The identifier for the language model to be used,
        defaulting to "gpt-4o".
    """

    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.api_url = "https://api.openai.com/v1/chat/completions"
        self.model = "gpt-4o"

    def format_conversation(self, conversation_history):
        """
        Formats a conversation history into a readable string representation.

        Args:
            conversation_history (list of dict): A list of message dictionaries, where each dictionary
                contains the keys 'role' (indicating the role of the speaker, e.g., 'user' or 'assistant')
                and 'content' (the message content).

        Returns:
            str: A formatted string where each message is prefixed with 'Agent' if the role is 'user',
            or 'Customer' otherwise, followed by the message content. Messages are separated by newlines.
        """
        formatted = "\n".join(
            f"{'Agent' if msg['role'] == 'user' else 'Customer'}: {msg['content']}"
            for msg in conversation_history
        )
        return formatted

    def generate(self, prompt):
        """
        Generates a response from a language model based on the provided prompt.

        Args:
            prompt (str): The input prompt to send to the language model.

        Returns:
            str: The generated response from the language model if the request is successful.
                 If the request fails, returns an error message containing the status code
                 and response text.
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 50,
        }

        response = requests.post(self.api_url, headers=headers, data=json.dumps(data))
        if response.status_code == 200:
            result = response.json()
            reply = (
                result.get("choices", [])[0]
                .get("message", {})
                .get("content", "")
                .strip()
            )
            return reply
        else:
            return f"Error: {response.status_code}, {response.text}"

    def check_refund_status(self, conversation_history):
        """
        Analyzes a conversation history to determine if the agent agreed to generate a refund.

        Args:
            conversation_history (list): A list of conversation messages, where each message
                is typically a dictionary or string representing the dialogue between the agent
                and the customer.

        Returns:
            str: 'Yes' if the agent agreed to generate a refund, 'No' otherwise. The response
                will strictly be either 'Yes' or 'No' without any additional characters.
        """
        formatted_history = self.format_conversation(conversation_history)
        prompt = (
            "Analyze the following conversation history and determine if the agent agreed to generate a refund.\n"
            "Answer only with 'Yes' or 'No' without any other characters.\n\n"
            f"{formatted_history}"
        )
        response = self.generate(prompt)
        return response

    def get_refund_amount(self, conversation_history):
        """
        Determines the refund amount agreed upon in a conversation history.

        Args:
            conversation_history (list): A list of strings representing the
                conversation history between the agent and the customer.

        Returns:
            int: The refund amount in dollars as an integer. Returns 0 if no
                refund amount is found.
        """
        formatted_history = self.format_conversation(conversation_history)
        prompt = (
            "Analyze the following conversation history and determine the amount that the agent agreed to refund.\n"
            "Return only the refund amount as an integer in dollars. If no refund amount is found, return 0.\n\n"
            f"{formatted_history}"
        )
        response = self.generate(prompt)
        return response
