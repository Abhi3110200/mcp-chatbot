import asyncio
import sys
from pathlib import Path

# Add the current directory to the path so we can import from servers
sys.path.append(str(Path(__file__).parent))

async def test_math_server():
    print("\n=== Testing Math Server ===")
    try:
        from mcp.client import Client
        import json
        
        # Start the math server in a subprocess
        math_server = await asyncio.create_subprocess_exec(
            sys.executable, "servers/math.py",
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        # Create a client to communicate with the server using stdio transport
        client = Client()
        await client.connect(stdio=(math_server.stdout, math_server.stdin))
        
        # Test add function
        add_result = await client.call("add", {"a": 5, "b": 3})
        print(f"5 + 3 = {add_result}")
        
        # Test sqrt function
        sqrt_result = await client.call("sqrt", {"x": 16})
        print(f"sqrt(16) = {sqrt_result}")
        
        # Clean up
        math_server.terminate()
        await math_server.wait()
        
        return True
    except Exception as e:
        print(f"Math server test failed: {e}")
        import traceback
        traceback.print_exc()
        if 'math_server' in locals():
            math_server.terminate()
        return False

async def test_search_server():
    print("\n=== Testing Search Server ===")
    try:
        from mcp.client import Client
        
        # Start the search server in a subprocess
        search_server = await asyncio.create_subprocess_exec(
            sys.executable, "servers/search.py",
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        # Create a client to communicate with the server using stdio transport
        client = Client()
        await client.connect(stdio=(search_server.stdout, search_server.stdin))
        
        # Test web search
        print("Testing web search...")
        web_results = await client.call("web_search", {"query": "Python programming", "max_results": 2})
        print(f"Found {len(web_results)} results")
        for i, result in enumerate(web_results, 1):
            print(f"{i}. {result.get('title', 'No title')}")
        
        # Test news search
        print("\nTesting news search...")
        news_results = await client.call("search_news", {"query": "AI", "max_results": 2})
        print(f"Found {len(news_results)} news items")
        for i, result in enumerate(news_results, 1):
            print(f"{i}. {result.get('title', 'No title')} - {result.get('source', 'No source')}")
        
        # Clean up
        search_server.terminate()
        await search_server.wait()
        
        return True
    except Exception as e:
        print(f"Search server test failed: {e}")
        import traceback
        traceback.print_exc()
        if 'search_server' in locals():
            search_server.terminate()
        return False

async def main():
    print("Starting MCP server tests...")
    
    # Test math server
    math_ok = await test_math_server()
    
    # Test search server
    search_ok = await test_search_server()
    
    # Print summary
    print("\n=== Test Summary ===")
    print(f"Math Server: {'✅ PASS' if math_ok else '❌ FAIL'}")
    print(f"Search Server: {'✅ PASS' if search_ok else '❌ FAIL'}")
    
    if not (math_ok and search_ok):
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
