import asyncio
from Three_PointO_ArchE.tools.enhanced_search_tool import search_web

async def main():
    """Tests the search_web action."""
    query = "latest developments in artificial intelligence"
    print(f"Testing search_web with query: '{query}'")
    result = await search_web(query)
    print("Result:")
    print(result)

if __name__ == "__main__":
    asyncio.run(main())





