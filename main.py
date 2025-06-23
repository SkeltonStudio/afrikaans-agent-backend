"""
🎯 Afrikaans Agent Backend - Node-Based MCP Server
Flow: [Input] → [Tool Node] → [Cypher Query Node] → [Output Stream]

Like Blender GeoNodes, each function is a node in the pipeline!
"""

from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse
from neo4j import GraphDatabase
from pydantic import BaseModel
import json
import asyncio
from typing import Dict, Any, List, Optional
import logging
import os

# 🔧 Configure logging for debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Afrikaans Agent MCP Server", version="1.0.0")

# 🌐 Neo4j Connection Node
class Neo4jNode:
    """[Database Connection Node] - Connects to Neo4j graph database"""
    
    def __init__(self, uri: str, username: str, password: str):
        self.driver = GraphDatabase.driver(uri, auth=(username, password))
        logger.info("🔗 Neo4j connection node initialized")
    
    def close(self):
        self.driver.close()
    
    def query(self, cypher_query: str, parameters: Dict = None) -> List[Dict]:
        """[Cypher Query Node] - Executes Cypher queries and returns results"""
        try:
            with self.driver.session() as session:
                result = session.run(cypher_query, parameters or {})
                records = [dict(record) for record in result]
                logger.info(f"🔍 Query executed: {cypher_query[:50]}... → {len(records)} results")
                return records
        except Exception as e:
            logger.error(f"❌ Query failed: {e}")
            return []

# 🛠️ MCP Tool Definition Node
class MCPToolNode:
    """[Tool Schema Node] - Defines MCP tool specifications for ElevenLabs"""
    
    @staticmethod
    def get_tool_schema() -> Dict[str, Any]:
        """[Schema Definition Node] - Returns MCP tool schema"""
        return {
            "name": "query_afrikaans_knowledge_graph",
            "description": "Query the Afrikaans knowledge graph for educational content, stories, vocabulary, and cultural information",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query_type": {
                        "type": "string",
                        "enum": ["vocabulary", "story", "culture", "grammar", "general"],
                        "description": "Type of Afrikaans content to search for"
                    },
                    "topic": {
                        "type": "string",
                        "description": "Specific topic or question about Afrikaans"
                    },
                    "difficulty": {
                        "type": "string",
                        "enum": ["beginner", "intermediate", "advanced"],
                        "default": "beginner"
                    }
                },
                "required": ["query_type", "topic"]
            }
        }

# 📡 SSE Streaming Node
class SSEStreamNode:
    """[Event Stream Node] - Handles Server-Sent Events for real-time responses"""
    
    @staticmethod
    async def stream_response(data: Dict[str, Any]):
        """[Stream Output Node] - Streams data as SSE events"""
        yield f"data: {json.dumps(data)}\n\n"

# 🔄 Query Processing Node
class QueryProcessorNode:
    """[Query Processing Node] - Converts user input to Cypher queries"""
    
    @staticmethod
    def generate_cypher_query(query_type: str, topic: str, difficulty: str = "beginner") -> str:
        """[Query Generator Node] - Converts natural language to Cypher"""
        
        # Base patterns for different query types
        patterns = {
            "vocabulary": """
                MATCH (w:Word {language: 'Afrikaans'})
                WHERE toLower(w.english) CONTAINS toLower($topic) 
                   OR toLower(w.afrikaans) CONTAINS toLower($topic)
                RETURN w.afrikaans as afrikaans, w.english as english, w.pronunciation as pronunciation
                LIMIT 10
            """,
            "story": """
                MATCH (s:Story)
                WHERE toLower(s.title) CONTAINS toLower($topic) 
                   OR toLower(s.content) CONTAINS toLower($topic)
                RETURN s.title as title, s.content as content, s.difficulty as difficulty
                LIMIT 5
            """,
            "culture": """
                MATCH (c:CulturalItem)
                WHERE toLower(c.name) CONTAINS toLower($topic) 
                   OR toLower(c.description) CONTAINS toLower($topic)
                RETURN c.name as name, c.description as description, c.category as category
                LIMIT 5
            """,
            "grammar": """
                MATCH (g:GrammarRule)
                WHERE toLower(g.rule) CONTAINS toLower($topic) 
                   OR toLower(g.explanation) CONTAINS toLower($topic)
                RETURN g.rule as rule, g.explanation as explanation, g.examples as examples
                LIMIT 5
            """,
            "general": """
                MATCH (n)
                WHERE toLower(n.name) CONTAINS toLower($topic) 
                   OR toLower(n.content) CONTAINS toLower($topic)
                   OR toLower(n.description) CONTAINS toLower($topic)
                RETURN labels(n)[0] as type, n.name as name, n.content as content, n.description as description
                LIMIT 10
            """
        }
        
        return patterns.get(query_type, patterns["general"])

# 🌐 Initialize Neo4j Node (will be initialized with environment variables)
neo4j_node = None

@app.on_event("startup")
async def startup_event():
    """[Startup Node] - Initialize the system on startup"""
    global neo4j_node
    
    # Get Neo4j credentials from environment variables
    neo4j_uri = os.getenv("NEO4J_URI")
    neo4j_username = os.getenv("NEO4J_USERNAME")
    neo4j_password = os.getenv("NEO4J_PASSWORD")
    
    if neo4j_uri and neo4j_username and neo4j_password:
        try:
            neo4j_node = Neo4jNode(neo4j_uri, neo4j_username, neo4j_password)
            logger.info("🔗 Neo4j connection established from environment variables")
        except Exception as e:
            logger.error(f"❌ Failed to connect to Neo4j: {e}")
            neo4j_node = None
    else:
        logger.info("⚠️ Neo4j credentials not found in environment variables - running in mock mode")
        neo4j_node = None
    
    logger.info("🚀 Afrikaans Agent MCP Server started!")

@app.on_event("shutdown")
async def shutdown_event():
    """[Shutdown Node] - Clean up resources"""
    if neo4j_node:
        neo4j_node.close()
    logger.info("🛑 Server shutdown complete")

# 📥 Input Node - MCP Tool Registration
@app.get("/tools")
async def get_tools():
    """[Tool Registration Node] - Returns available MCP tools"""
    return {
        "tools": [MCPToolNode.get_tool_schema()]
    }

# 🔄 Main Processing Pipeline
@app.post("/query")
async def query_knowledge_graph(request: Request):
    """[Main Pipeline Node] - [Input] → [Tool Node] → [Cypher Query Node] → [Output Stream]"""
    
    # [Input Node] - Parse request
    body = await request.json()
    query_type = body.get("query_type", "general")
    topic = body.get("topic", "")
    difficulty = body.get("difficulty", "beginner")
    
    logger.info(f"📥 Input received: {query_type} - {topic}")
    
    # [Query Generator Node] - Generate Cypher query
    cypher_query = QueryProcessorNode.generate_cypher_query(query_type, topic, difficulty)
    
    # [Database Query Node] - Execute query
    if neo4j_node:
        results = neo4j_node.query(cypher_query, {"topic": topic, "difficulty": difficulty})
    else:
        # Mock response for testing
        results = [{"message": "Neo4j not connected", "topic": topic, "query_type": query_type}]
    
    # [Output Stream Node] - Stream results via SSE
    async def generate_stream():
        yield f"data: {json.dumps({'status': 'processing', 'query': topic})}\n\n"
        
        for i, result in enumerate(results):
            yield f"data: {json.dumps({'status': 'result', 'data': result, 'index': i})}\n\n"
            await asyncio.sleep(0.1)  # Small delay for streaming effect
        
        yield f"data: {json.dumps({'status': 'complete', 'total_results': len(results)})}\n\n"
    
    return EventSourceResponse(generate_stream())

# 🧪 Test Node - Simple health check
@app.get("/health")
async def health_check():
    """[Health Check Node] - Verify system status"""
    return {
        "status": "healthy", 
        "message": "Afrikaans Agent MCP Server is running!",
        "neo4j_connected": neo4j_node is not None
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 