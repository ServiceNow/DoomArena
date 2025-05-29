# server.py
from fastmcp import FastMCP

mcp = FastMCP("Sort server 🚀")


@mcp.tool()
def sort(a: int, b: int) -> list[int]:
    """Return sorted list of two numbers"""
    return [min(a, b), max(a, b)]


if __name__ == "__main__":
    mcp.run()
