from doomarena.promptceptor.integrations.openai_responses import OpenAIResponsesPatcher
import openai
from openai import OpenAI


# Example function to make API calls
def make_calls_openai():
    client = OpenAI()

    # # Non-streaming response
    print("\n▶ Running non-streaming call...")
    response = client.responses.create(
        model="gpt-4o-mini",
        input="Give me the 5 most important things to know about the universe. As one-line bullet points."
    )
    print("✅ Non-streaming call completed.\n")
    print(response.output_text)

    # Example: streaming call
    print("▶ Running streaming call...")
    response = client.responses.create(
        model="gpt-4o-mini",
        input="Give me the 3 most important things to know about the universe. As one-line bullet points.",
        stream=True
    )
    for chunk in response:
        # print(f"🧩 Chunk: {chunk}")
        print(f".", end="", flush=True)
    print("\n✅ Streaming call completed.\n")


if __name__ == "__main__":

    # ✅ Patch the Responses.create class method
    output_folder = OpenAIResponsesPatcher().patch_client()
    
    make_calls_openai()

    print("📂 Output has been logged to:")
    print(f"   {output_folder}")
    print("\n🧪 To inspect or recompute missing outputs:")
    print(f"   $ python -m doomarena.promptceptor {output_folder}")
    print("   or")
    print(f"   $ promptceptor {output_folder}")