"""
🧪 Test Client for Afrikaans Agent MCP Server
Tests the node pipeline: [Input] → [Tool Node] → [Cypher Query Node] → [Output Stream]
"""

import requests
import json
import sseclient

def test_health_check():
    """[Health Test Node] - Test basic server connectivity"""
    print("🔍 Testing health check...")
    response = requests.get("http://localhost:8000/health")
    print(f"✅ Health check: {response.json()}")

def test_tools_endpoint():
    """[Tools Test Node] - Test MCP tool registration"""
    print("\n🔍 Testing tools endpoint...")
    response = requests.get("http://localhost:8000/tools")
    tools = response.json()
    print(f"✅ Available tools: {json.dumps(tools, indent=2)}")

def test_query_streaming():
    """[Streaming Test Node] - Test SSE streaming with mock query"""
    print("\n🔍 Testing query streaming...")
    
    # Test data
    test_query = {
        "query_type": "vocabulary",
        "topic": "hello",
        "difficulty": "beginner"
    }
    
    print(f"📤 Sending query: {test_query}")
    
    # Send POST request and stream response
    response = requests.post(
        "http://localhost:8000/query",
        json=test_query,
        stream=True,
        headers={'Accept': 'text/event-stream'}
    )
    
    if response.status_code == 200:
        client = sseclient.SSEClient(response)
        print("📡 Streaming response:")
        for event in client.events():
            data = json.loads(event.data)
            print(f"  📥 {data}")
            if data.get('status') == 'complete':
                break
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")

if __name__ == "__main__":
    print("🚀 Testing Afrikaans Agent MCP Server Node Pipeline")
    print("=" * 50)
    
    try:
        test_health_check()
        test_tools_endpoint()
        test_query_streaming()
        print("\n✅ All tests completed!")
    except requests.exceptions.ConnectionError:
        print("❌ Server not running. Start with: uvicorn main:app --reload")
    except Exception as e:
        print(f"❌ Test failed: {e}") 