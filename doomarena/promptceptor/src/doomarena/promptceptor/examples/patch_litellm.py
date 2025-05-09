from doomarena.promptceptor.integrations.litellm import LiteLLMPatcher
import litellm


def make_calls_litellm():
    # Example: non-streaming call
    print("\n▶ Running non-streaming call...")
    response = litellm.completion(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Give me the 5 most important things to know about the universe. As one-line bullet points."}],
        stream=False,
        temperature=0.5
    )
    print("✅ Non-streaming call completed.\n")

    # Example: streaming call
    print("▶ Running streaming call...")
    response = litellm.completion(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Give me the 3 most important things to know about the universe. As one-line bullet points."}],
        stream=True,
        temperature=0.5
    )
    for chunk in response:
        # print(f"🧩 Chunk: {chunk}")
        print(f".", end="", flush=True)

    print("\n✅ Streaming call completed.\n")


if __name__ == "__main__":

    output_folder = LiteLLMPatcher().patch_client()
    
    print("🔧 Patched litellm.completion to log input/output...")

    # Your existing agentic workflow
    make_calls_litellm()

    # Final instructions
    print("📂 Output has been logged to:")
    print(f"   {output_folder}")
    print("\n🧪 To inspect or recompute missing outputs:")
    print(f"   $ python -m doomarena.promptceptor {output_folder}")
    print("   or")
    print(f"   $ promptceptor {output_folder}")
