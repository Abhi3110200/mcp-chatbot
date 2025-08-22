import os
import re
import asyncio
from pathlib import Path
from dotenv import load_dotenv

from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

# Load environment variables
load_dotenv()

# -------------------------
# Utility functions
# -------------------------
def _extract_search_query(msg: str) -> str:
    s = msg.strip()
    s = re.sub(r"^(search( the web)?( for)?|find|look up|lookup)\s+", "", s, flags=re.I)
    s = re.sub(r"^for\s+", "", s, flags=re.I)
    s = re.sub(r"^the\s+", "", s, flags=re.I)
    s = re.sub(r"[.?!]+$", "", s)
    return s.strip()

def _needs_web(msg: str) -> bool:
    m = msg.lower().strip()
    mathy = re.sub(r"\b(what's|what is|calculate|compute|solve|evaluate)\b", "", m)
    mathy = mathy.replace("x", "*").replace("×", "*")
    if re.fullmatch(r"[0-9\.\s\+\-\*\/\^\(\)]+", mathy):
        return False

    keywords = [
        "latest", "news", "update", "updates", "recent", "trend", "trends",
        "who is", "what is", "when was", "history", "timeline", "background",
        "document", "docs", "documentation", "tutorial", "guide", "how to",
        "best", "top", "compare", "vs ", "versus", "review", "reviews",
        "pricing", "price", "specs", "features", "release", "changelog",
        "conference", "paper", "research", "breakthrough", "state of the art",
        "sota", "benchmarks", "dataset", "github", "repo", "repository",
    ]
    if any(k in m for k in keywords):
        return True
    if re.search(r"\b(search( the web)?( for)?|find|look\s*up|lookup)\b", m):
        return True
    return False

async def _summarize(model, query: str, snippets: str) -> str:
    sys_msg = SystemMessage(content=(
        "You are a concise summarizer. Read the provided snippets and answer the user's query clearly and briefly. "
        "Do NOT include raw URLs or link markup. If dates are present, keep them. If information is missing, say so."
    ))
    user_msg = HumanMessage(content=f"Query: {query}\n\nSnippets:\n{snippets}")
    try:
        res = await model.ainvoke([sys_msg, user_msg])
        return (res.content or "").strip()
    except Exception as e:
        return f"Summary unavailable: {e}"

# -------------------------
# Main logic
# -------------------------
async def main():
    BASE_DIR = Path(__file__).resolve().parent
    MATH_SERVER = str(BASE_DIR / "servers" / "math.py")
    SEARCH_SERVER = str(BASE_DIR / "servers" / "search.py")

    os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
    os.environ["MCP_VERBOSE"] = "1"

    # Initialize tools list
    tools = []

    # Load tools with error handling for each server
    try:
        print("Starting MCP servers...")
        
        # Start math server
        math_server = await asyncio.create_subprocess_exec(
            sys.executable, MATH_SERVER,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        # Start search server
        search_server = await asyncio.create_subprocess_exec(
            sys.executable, SEARCH_SERVER,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        # Import the client
        from mcp.client import Client
        
        # Connect to math server
        math_client = Client()
        await math_client.connect(stdio=(math_server.stdout, math_server.stdin))
        
        # Connect to search server
        search_client = Client()
        await search_client.connect(stdio=(search_server.stdout, search_server.stdin))
        
        # Get tools from both servers
        math_tools = await math_client.list_tools()
        search_tools = await search_client.list_tools()
        
        # Combine tools
        if math_tools:
            tools.extend(math_tools.tools)
        if search_tools:
            tools.extend(search_tools.tools)
            
        if tools:
            print("✅ Successfully loaded tools:", [t.name for t in tools])
        else:
            print("⚠️ No tools found in any MCP server")
            
    except Exception as e:
        print(f"❌ Error connecting to MCP servers: {e}")
        print("Please ensure the MCP servers are running and accessible.")
        print(f"Math server path: {MATH_SERVER}")
        print(f"Search server path: {SEARCH_SERVER}")
        
        # Clean up if servers were started
        if 'math_server' in locals():
            math_server.terminate()
        if 'search_server' in locals():
            search_server.terminate()
            
        return

    if not tools:
        print("❌ No MCP tools available. Exiting.")
        return

    tool_names = ", ".join([t.name for t in tools])
    print(f"Available tool names: {tool_names}")
    
    model = ChatGroq(model="llama-3.3-70b-versatile")
    model_plain = ChatGroq(model="llama-3.3-70b-versatile")

    # Create agent with available tools
    try:
        print(f"Creating agent with tools: {[t.name for t in tools]}")
        agent = create_react_agent(model, tools)
        print("✅ Agent created successfully")
    except Exception as e:
        print(f"❌ Failed to create agent: {e}")
        print("This might be due to tool compatibility issues. Please check the tool definitions.")
        return

    SYSTEM_INSTRUCTION = (
        f"You are a helpful AI assistant with access to these tools: {tool_names}.\n"
        "Rules for tool usage:\n"
        "1. For math calculations, use the 'evaluate_expression' tool\n"
        "2. For web searches, use the 'web_search' tool with these parameters:\n"
        "   - query: The search query\n"
        "   - max_results: Number of results (1-10)\n"
        "   - include_content: Set to true to get full content\n"
        "3. For news searches, use the 'news_search' tool with similar parameters\n\n"
        "Always provide clear, concise responses. If using a tool, explain what you're doing.\n"
        "If you encounter an error, try rephrasing or breaking down the query."
    )

    user_messages = [
        "what's (3 + 5) x 12?",  # Should use evaluate_expression
        "Search the web for latest news on AI research breakthroughs.",  # Should use web_search
        "What's 15% of 80?",  # Should use evaluate_expression
        "Find recent news about space exploration"  # Should use news_search
    ]

    for i, msg in enumerate(user_messages, start=1):
        base_messages = [
            {"role": "system", "content": SYSTEM_INSTRUCTION},
            {"role": "user", "content": msg},
        ]

        forced_web = False
        forced_result = None
        if _needs_web(msg):
            try:
                search_tool = next(t for t in tools if t.name == "web_search")
                topic = _extract_search_query(msg) or msg
                forced_result = await search_tool.ainvoke(
                    {"query": topic, "max_results": 3, "include_content": True}
                )
                forced_web = True
            except Exception as fe:
                print("⚠️ Forced web_search failed:", fe)

        try:
            if forced_web and isinstance(forced_result, str) and forced_result.strip():
                final_text = await _summarize(model_plain, msg, forced_result)
            else:
                result = await agent.ainvoke({"messages": base_messages})
                final_text = result["messages"][-1].content
        except Exception as e:
            print("⚠️ Agent error:", e)
            final_text = "Sorry, I had trouble answering that."

        # Cleanup any tool markup in the final answer
        if isinstance(final_text, str) and "<function