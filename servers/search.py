from typing import List, Dict, Any
from duckduckgo_search import DDGS
from mcp.server.fastmcp.server import MCPServer
from mcp.server.fastmcp.tools import Tool

# Create the server
app = MCPServer(name="search")

# Define the tools
@Tool(name="web_search")
async def search_web(query: str, max_results: int = 3) -> List[Dict[str, Any]]:
    """Search the web for information."""
    try:
        with DDGS() as ddgs:
            results = []
            for result in ddgs.text(query, max_results=max_results):
                results.append({
                    "title": result.get("title", ""),
                    "url": result.get("href", ""),
                    "snippet": result.get("body", "")
                })
            return results
    except Exception as e:
        return [{"error": f"Search failed: {str(e)}"}]

@Tool(name="search_news")
async def search_news(query: str, max_results: int = 3) -> List[Dict[str, Any]]:
    """Search for news articles."""
    try:
        with DDGS() as ddgs:
            results = []
            for result in ddgs.news(query, max_results=max_results):
                results.append({
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "snippet": result.get("body", ""),
                    "date": result.get("date", ""),
                    "source": result.get("source", "")
                })
            return results
    except Exception as e:
        return [{"error": f"News search failed: {str(e)}"}]

# Register the tools
app.register_tool(search_web)
app.register_tool(search_news)

if __name__ == "__main__":
    app.run(transport="stdio")