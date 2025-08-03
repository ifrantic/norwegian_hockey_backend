# tests/test_claude.py
import asyncio
import httpx

async def test_claude():
    base_url = "http://localhost:8000"
    
    # Test natural language queries
    queries = [ 
        "Show me 5 teams",  # Simple test first
        "List all positions in team_members",  # Check what positions exist
        "List players with position 'goalkeeper' or GK1",
        "Show me all players from Panthers best team ",
    ]
    
    timeout = httpx.Timeout(60.0)  # Add timeout
    
    async with httpx.AsyncClient(timeout=timeout) as client:
        for query in queries:
            print(f"\n🤖 Query: {query}")
            
            try:
                response = await client.post(
                    f"{base_url}/api/query",
                    json={"query": query}
                )
                
                if response.status_code != 200:
                    print(f"❌ HTTP {response.status_code}: {response.text}")
                    continue
                
                result = response.json()
                
                if result.get("success"):
                    print(f"✅ SQL: {result['sql']}")
                    print(f"📊 Found {result['row_count']} rows")
                    
                    # Show first few results
                    for i, row in enumerate(result['data'][:3]):
                        print(f"   {i+1}: {row}")
                else:
                    print(f"❌ Error: {result.get('error')}")
                    
            except Exception as e:
                print(f"❌ Exception: {e}")

if __name__ == "__main__":
    asyncio.run(test_claude())