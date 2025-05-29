# server.py
from fastmcp import FastMCP

# mcp = FastMCP("Demo 🚀")

# @mcp.tool()
# def add(a: int, b: int) -> int:
#     """Add two numbers"""
#     return a + b

# if __name__ == "__main__":
#     mcp.run()

from fastmcp import Client

config = {
    "mcpServers": {
        "add": {
            "command": "/Users/gabriel.huang/mamba/envs/raa6/bin/python",
            "args": [
                "/Users/gabriel.huang/code/DoomArena/doomarena/mcp/src/doomarena/mcp/add_server.py"
            ],
        }
    }
}


async def main():
    # Connect via stdio to a local script
    # async with Client(config) as client:
    async with Client(
        "/Users/gabriel.huang/code/DoomArena/doomarena/mcp/src/doomarena/mcp/add_server.py"
    ) as client:
        tools = await client.list_tools()
        print(f"Available tools: {tools}")
        result = await client.call_tool("add", {"a": 5, "b": 3})
        print(f"Result: {result}")

        result = await client.call_tool("sort", {"a": 5, "b": 3})
        print(f"Result: {result}")

        print("Done!")


if __name__ == "__main__":
    import anyio

    anyio.run(main)
