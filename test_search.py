from ddgs import DDGS

def test_search():
    try:
        print("Testing web search...")
        with DDGS() as ddgs:
            results = list(ddgs.text("python programming", max_results=3))
            print("Search results:")
            for i, result in enumerate(results, 1):
                print(f"{i}. {result.get('title')}")
                print(f"   {result.get('href')}")
                print(f"   {result.get('body', '')[:100]}...")
                print()
                
        print("\nTesting news search...")
        with DDGS() as ddgs:
            results = list(ddgs.news("latest technology", max_results=3))
            print("News results:")
            for i, result in enumerate(results, 1):
                print(f"{i}. {result.get('title')}")
                print(f"   {result.get('url')}")
                print(f"   {result.get('excerpt', '')[:100]}...")
                print()
                
    except Exception as e:
        print(f"Error during search: {str(e)}")

if __name__ == "__main__":
    test_search()
