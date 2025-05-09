from doomarena.promptceptor.integrations.openai_chat import OpenAIChatPatcher
from openai import OpenAI


def make_calls_openai_chat():
    client = OpenAI()

    # Non-streaming example
    print("\n▶ Running non-streaming chat completion...")
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": "Write a one-sentence bedtime story about a unicorn."
            }
        ],
        stream=False
    )
    print("✅ Non-streaming call completed.\n")
    print(response.choices[0].message.content)

    # Streaming example
    print("▶ Running streaming chat completion...")
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": "Tell me a bedtime story in 2 short lines."
            }
        ],
        stream=True
    )
    for chunk in response:
        print(chunk.choices[0].delta.content, end="", flush=True)
    print("\n✅ Streaming call completed.\n")


if __name__ == "__main__":
    output_folder = OpenAIChatPatcher().patch_client()
    make_calls_openai_chat()

    print("📂 Output has been logged to:")
    print(f"   {output_folder}")
    print("\n🧪 To inspect or recompute missing outputs:")
    print(f"   $ python -m doomarena.promptceptor {output_folder}")
    print("   or")
    print(f"   $ promptceptor {output_folder}")
