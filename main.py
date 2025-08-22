from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
import re
import os
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

import asyncio
from groq import BadRequestError


async def main():

    BASE_PATH = Path(__file__).parent
    
    MATH_SERVER=str(BASE_PATH / "servers" / "math.py")

    os.environ["GROQ_API_KEY"]=os.getenv("GROQ_API_KEY")
    os.environ["MCP_VERBOSE"] = "1"

    client=MultiServerMCPClient(
        {
            "math": {
                "command": "python",
                "args": [MATH_SERVER],  # Ensure correct absolute path
                "transport": "stdio",
            },
            "weather": {
                "url": "http://127.0.0.1:8000/mcp",
                "transport": "streamable_http",
            },
            "search": {
                "command": "python",
                "args": [str(BASE_PATH / "servers" / "search.py")],
                "transport": "stdio",
            }
        }
    )

    tools = await client.get_tools()
    print("Loaded tools:", [t.name for t in tools])
    tool_names = ", ".join([t.name for t in tools])
    model = ChatGroq(model="llama-3.3-70b-versatile")
    model_plain = ChatGroq(model="llama-3.3-70b-versatile")
    agent = create_react_agent(
        model,
        tools,
    )

    

