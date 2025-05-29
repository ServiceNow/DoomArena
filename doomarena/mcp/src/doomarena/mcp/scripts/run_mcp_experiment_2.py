import asyncio
from typing import Optional
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from anthropic import Anthropic
from dotenv import load_dotenv
from openai import OpenAI
import litellm
import json
import sys

load_dotenv()  # load environment variables from .env


def get_server_params(server_script_path: str) -> StdioServerParameters:
    """Create server parameters based on script type"""
    is_python = server_script_path.endswith(".py")
    is_js = server_script_path.endswith(".js")
    if not (is_python or is_js):
        raise ValueError("Server script must be a .py or .js file")

    command = (
        sys.executable if is_python else "node"
    )  # use current Python interpreter for .py files
    return StdioServerParameters(command=command, args=[server_script_path], env=None)


# class MCPClient:
#     def __init__(self, server_params: StdioServerParameters):
#         # Initialize session and client objects
#         self.session: Optional[ClientSession] = None
#         self.exit_stack = AsyncExitStack()
#         self.anthropic = Anthropic()
#         self.stdio = None
#         self.write = None

#         self.server_params = server_params

#     @classmethod
#     async def create(cls, server_params: StdioServerParameters):
#         """Factory method to create an MCPClient instance. Use this to ensure proper async initialization."""
#         client = cls(server_params)
#         await client.initialize_mcp_servers()
#         return client

#     async def initialize_mcp_servers(self):
#         stdio_transport = await self.exit_stack.enter_async_context(stdio_client(self.server_params))
#         self.stdio, self.write = stdio_transport
#         self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))

#         await self.session.initialize()

#         # List available tools
#         response = await self.session.list_tools()
#         tools = response.tools
#         print("\nConnected to server with tools:", [tool.name for tool in tools])

#     async def aclose(self):
#         """Close the client session. Must be called to clean up resources."""
#         await self.exit_stack.aclose()
#         self.session = None
#         self.stdio = None
#         self.write = None

#     async def process_query(self, query: str) -> str:
#         """Process a query using GPT-4o-mini via LiteLLM and available tools"""

#         # Initial user message
#         messages = [
#             {"role": "user", "content": query}
#         ]

#         # Get tools from session and convert to OpenAI function-call format
#         response = await self.session.list_tools()
#         available_tools_openai = [{
#             "type": "function",
#             "function": {
#                 "name": tool.name,
#                 "description": tool.description,
#                 "parameters": tool.inputSchema
#             },
#         } for tool in response.tools]

#         # Initial GPT-4o call with available tools
#         response = litellm.completion(
#             model="gpt-4o-mini",
#             messages=messages,
#             tools=available_tools_openai,
#             tool_choice="auto"
#         )

#         # Process first response
#         response_message = response.choices[0].message
#         final_text = []

#         # Check for tool calls
#         tool_calls = response_message.get("tool_calls", [])
#         if tool_calls:
#             # Add assistant message with tool calls
#             messages.append({
#                 "role": "assistant",
#                 # "content": assistant_message_content,
#                 "tool_calls": tool_calls
#             })

#             for tool_call in tool_calls:
#                 tool_name = tool_call["function"]["name"]
#                 tool_args = json.loads(tool_call["function"]["arguments"])
#                 tool_use_id = tool_call["id"]

#                 # Call the actual tool via session
#                 result = await self.session.call_tool(tool_name, tool_args)

#                 # Trace
#                 final_text.append(f"[Calling tool {tool_name} with args {tool_args}]")

#                 # Add tool response to messages
#                 messages.append({
#                     "tool_call_id": tool_use_id,
#                     "role": "tool",
#                     "name": tool_name,
#                     "content": result.model_dump()['content']
#                 })

#             # Follow-up LLM call after tool response
#             follow_up_response = litellm.completion(
#                 model="gpt-4o-mini",
#                 messages=messages
#             )
#             follow_up_message = follow_up_response.choices[0].message

#             if follow_up_message.get("content"):
#                 final_text.append(follow_up_message["content"])

#         return "\n".join(final_text)

# async def chat_loop(self):
#     """Run an interactive chat loop"""
#     print("\nMCP Client Started!")
#     print("Type your queries or 'quit' to exit.")

#     while True:
#         try:
#             query = input("\nQuery: ").strip()

#             if query.lower() == 'quit':
#                 break

#             response = await self.process_query(query)
#             print("\n" + response)

#         except Exception as e:
#             print(f"\nError: {str(e)}")

# async def cleanup(self):
#     """Clean up resources"""
#     await self.exit_stack.aclose()


# def run_client(server_params):
#     async def runner():
#         async with await MCPClient.create(server_params) as client:
#             result = await client.process_query("What's the weather?")
#             print(result)

#     asyncio.run(runner())


# async def main():
#     client = MCPClient()
#     try:
#         await client.connect_to_server("/Users/gabriel.huang/code/DoomArena/doomarena/mcp/src/doomarena/mcp/add_server.py")
#         await client.chat_loop()
#     finally:
#         await client.cleanup()


async def process_query(session: ClientSession, query: str) -> str:

    # Initial user message
    messages = [{"role": "user", "content": query}]

    # Get tools from session and convert to OpenAI function-call format
    response = await session.list_tools()
    available_tools_openai = [
        {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.inputSchema,
            },
        }
        for tool in response.tools
    ]

    # Initial GPT-4o call with available tools
    response = litellm.completion(
        model="gpt-4o-mini",
        messages=messages,
        tools=available_tools_openai,
        tool_choice="auto",
    )

    # Process first response
    response_message = response.choices[0].message
    final_text = []

    # Check for tool calls
    tool_calls = response_message.get("tool_calls", [])
    if tool_calls:
        # Add assistant message with tool calls
        messages.append(
            {
                "role": "assistant",
                # "content": assistant_message_content,
                "tool_calls": tool_calls,
            }
        )

        for tool_call in tool_calls:
            tool_name = tool_call["function"]["name"]
            tool_args = json.loads(tool_call["function"]["arguments"])
            tool_use_id = tool_call["id"]

            # Call the actual tool via session
            result = await session.call_tool(tool_name, tool_args)

            # Trace
            final_text.append(f"[Calling tool {tool_name} with args {tool_args}]")

            # Add tool response to messages
            messages.append(
                {
                    "tool_call_id": tool_use_id,
                    "role": "tool",
                    "name": tool_name,
                    "content": result.model_dump()["content"],
                }
            )

        # Follow-up LLM call after tool response
        follow_up_response = litellm.completion(model="gpt-4o-mini", messages=messages)
        follow_up_message = follow_up_response.choices[0].message

        if follow_up_message.get("content"):
            final_text.append(follow_up_message["content"])

    return "\n".join(final_text)


# async def amain(server_params: StdioServerParameters):
#     """Main async function to run the MCP client"""

#     async with stdio_client(server_params) as stdio_transport:
#         stdio, write = stdio_transport
#         async with ClientSession(stdio, write) as session:
#             await session.initialize()
#             response = await session.list_tools()
#             tools = response.tools
#             print("\nConnected to server with tools:", [tool.name for tool in tools])

#             # Prompt user for query or hardcode one
#             query = input("\nEnter a prompt: ")
#             result = await process_query(session, query)
#             print("\nResult:\n", result)

# def main():
#     """Main entry point to run the MCP client"""
#     server_params = get_server_params("/Users/gabriel.huang/code/DoomArena/doomarena/mcp/src/doomarena/mcp/add_server.py")
#     asyncio.run(amain(server_params))

# if __name__ == "__main__":
#     main()


import asyncio
from contextlib import AsyncExitStack
from typing import List


async def handle_server(session: ClientSession, query: str, server_name: str):
    await session.initialize()
    response = await session.list_tools()
    tools = response.tools
    print(f"\n[{server_name}] Connected with tools: {[tool.name for tool in tools]}")

    result = await process_query(session, query)
    print(f"\n[{server_name}] Result:\n{result}")


async def run_all_servers(server_params_list: List[StdioServerParameters]):
    query = input("\nEnter a prompt (applies to all servers): ")

    async with AsyncExitStack() as stack:
        sessions = []

        for server_idx, params in enumerate(server_params_list):
            stdio_transport = await stack.enter_async_context(stdio_client(params))
            stdio, write = stdio_transport
            session = await stack.enter_async_context(ClientSession(stdio, write))
            sessions.append((session, f"server_{server_idx}"))

        # Run query on all connected sessions
        await asyncio.gather(
            *(handle_server(session, query, name) for session, name in sessions)
        )


def main():
    server_params_list = [
        get_server_params(
            "/Users/gabriel.huang/code/DoomArena/doomarena/mcp/src/doomarena/mcp/add_server.py"
        ),
        get_server_params(
            "/Users/gabriel.huang/code/DoomArena/doomarena/mcp/src/doomarena/mcp/sort_server.py"
        ),
        # Add more server paths here
    ]
    asyncio.run(run_all_servers(server_params_list))


if __name__ == "__main__":
    main()
