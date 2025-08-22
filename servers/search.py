from mcp.server import Server
from mcp.interface import tool
from typing import List, Optional
from duckduckgo_search import DDGS

class SearchServer(Server):
    def __init__(self):
        super().__init__()
        self.ddgs = DDGS()

    @tool
    def search_web(self, query: str, max_results: int = 5) -> List[dict]:
        """Search the web for information.
        
        Args:
            query: The search query
            max_results: Maximum number of results to return (default: 5)
            
        Returns:
            A list of search results with title, link, and snippet
        """
        try:
            results = self.ddgs.text(query, max_results=max_results)
            return [{
                "title": r.get("title", ""),
                "link": r.get("href", ""),
                "snippet": r.get("body", "")
            } for r in results]
        except Exception as e:
            return [{"error": f"Search failed: {str(e)}"}]

    @tool
    def search_news(self, query: str, max_results: int = 5) -> List[dict]:
        """Search for news articles.
        
        Args:
            query: The search query
            max_results: Maximum number of results to return (default: 5)
            
        Returns:
            A list of news articles with title, link, and snippet
        """
        try:
            results = self.ddgs.news(query, max_results=max_results)
            return [{
                "title": r.get("title", ""),
                "link": r.get("url", ""),
                "snippet": r.get("excerpt", ""),
                "date": r.get("date", "")
            } for r in results]
        except Exception as e:
            return [{"error": f"News search failed: {str(e)}"}]

if __name__ == "__main__":
    server = SearchServer()
    server.run()