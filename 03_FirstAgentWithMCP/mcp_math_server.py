# MCP Math Server - The "Tool Provider"

# This server exposes the EXACT SAME tools that were
# hardcoded in first_agent.py, but now they live here
# as a reusable MCP server.

# ANY MCP-compatible client can use these tools:
# - Your LangChain agent (first_agent_with_mcp.py)
# - Claude Desktop
# - Codex
# - Cursor IDE
# - VS Code Copilot
# - Any custom MCP client

# That's the whole point of MCP: define once, use everywhere.

# Usage:
# This file is auto-launched by the agent script.
# To test standalone: python mcp_math_server.py
# To inspect:
# fastmcp dev mcp_math_server.py

from mcp.server.fastmcp import FastMCP
import math
import sys

mcp = FastMCP("Math")

# These are the SAME tools from first_agent.py
# but now exposed via MCP instead of @tool

@mcp.tool()
def add(a: float, b: float) -> float:
    """
    Add two numbers together.
    The agent will use this when it detects an addition problem
    """
    print(f"[math-server] add(a={a}, b={b})", file=sys.stderr)
    return a + b

@mcp.tool()
def multiply(a: float, b: float) -> float:
    """
    Multiply two numbers together.
    Used for multiplication tasks
    """
    print(f"[math-server] multiply(a={a}, b={b})", file=sys.stderr)
    return a * b

@mcp.tool()
def divide(a: float , b: float) -> str:
    """
    Divide the first number by the second.
    Include error handling for divide by zero.
    """

    if b == 0:
        return "Error: cannot divide by zero."
    print(f"[math-server] divide(a={a}, b={b})", file=sys.stderr)
    return str(a / b)

@mcp.tool()
def square_root(number: float) -> str:
    """
    Calculate the square root of a number.
    Include error handling for negative input.
    """

    if number < 0:
        return "Error: cannot find square root of negative number."
    
    return str(math.sqrt(number))

# RUN THE SERVER
if __name__ == "__main__":
    mcp.run(transport='stdio')