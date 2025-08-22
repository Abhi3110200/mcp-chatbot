from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
import re
import os
from pathlib import Path
from dotenv import load_dotenv
import asyncio
from groq import BadRequestError

load_dotenv()

async def main():
    BASE_PATH = Path(__file__).parent
    
    # Set up server configurations
    MATH_SERVER = str(BASE_PATH / "servers" / "math.py")
    SEARCH_SERVER = str(BASE_PATH / "servers" / "search.py")

    # Set up environment variables
    os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY", "")
    os.environ["MCP_VERBOSE"] = "1"

    # Initialize MCP client with both math and search servers
    client = MultiServerMCPClient(
        {
            "math": {
                "command": "python",
                "args": [MATH_SERVER],
                "transport": "stdio",
            },
            "search": {
                "command": "python",
                "args": [SEARCH_SERVER],
                "transport": "stdio",
            }
        }
    )

    # Initialize the language model
    model = ChatGroq(model="llama-3.3-70b-versatile")
    
    # Get available tools
    tools = await client.get_tools()
    print("Available tools:", [t.name for t in tools])
    
    # Create the agent
    agent = create_react_agent(model, tools)
    
    # Main interaction loop
    print("MCP Chatbot initialized. Type 'exit' to quit.")
    while True:
        try:
            user_input = input("\nYou: ").strip()
            if user_input.lower() in ('exit', 'quit'):
                print("Goodbye!")
                break
                
            # Process the input
            response = await agent.ainvoke({"messages": [HumanMessage(content=user_input)]})
            print(f"\nAssistant: {response['messages'][-1].content}")
            
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except BadRequestError as e:
            print(f"\nError: {str(e)}")
        except Exception as e:
            print(f"\nAn error occurred: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())