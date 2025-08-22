from mcp.server.fastmcp.server import MCPServer
from mcp.server.fastmcp.tools import Tool
import math

# Create the server
app = MCPServer()

# Define the tools
@Tool(name="add")
async def add(a: float, b: float) -> float:
    """Add two numbers together."""
    return a + b

@Tool(name="sqrt")
async def sqrt(x: float) -> float:
    """Calculate the square root of a number."""
    if x < 0:
        raise ValueError("Cannot take square root of a negative number")
    return math.sqrt(x)

# Register the tools
app.register_tool(add)
app.register_tool(sqrt)

if __name__ == "__main__":
    app.run(transport="stdio")
