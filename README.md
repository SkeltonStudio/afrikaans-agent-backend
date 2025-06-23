# 🎯 Afrikaans Agent MCP Server

A node-based FastAPI server that exposes a custom MCP (Model Context Protocol) server over SSE for ElevenLabs agents to query a Neo4j knowledge graph.

## 🔄 Node Pipeline Flow

Like Blender GeoNodes, each function is a node in the pipeline:

```
[Input] → [Tool Node] → [Cypher Query Node] → [Output Stream]
```

### Node Breakdown:
- **[Input Node]**: Receives queries from ElevenLabs agent
- **[Tool Node]**: Defines MCP tool schema for ElevenLabs
- **[Cypher Query Node]**: Converts natural language to Neo4j queries
- **[Output Stream Node]**: Streams results via Server-Sent Events (SSE)

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Neo4j Connection
Edit `main.py` and uncomment the Neo4j connection in the `startup_event()` function:

```python
neo4j_node = Neo4jNode("bolt://localhost:7687", "neo4j", "your_password")
```

### 3. Start the Server
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Test the Pipeline
```bash
python test_client.py
```

## 📡 API Endpoints

### Health Check
```bash
GET /health
```

### MCP Tools Registration
```bash
GET /tools
```

### Query Knowledge Graph (SSE Stream)
```bash
POST /query
Content-Type: application/json

{
  "query_type": "vocabulary",
  "topic": "hello",
  "difficulty": "beginner"
}
```

## 🛠️ MCP Tool Schema

The server exposes one tool for ElevenLabs:

```json
{
  "name": "query_afrikaans_knowledge_graph",
  "description": "Query the Afrikaans knowledge graph for educational content",
  "inputSchema": {
    "type": "object",
    "properties": {
      "query_type": {
        "type": "string",
        "enum": ["vocabulary", "story", "culture", "grammar", "general"]
      },
      "topic": {
        "type": "string",
        "description": "Specific topic or question"
      },
      "difficulty": {
        "type": "string",
        "enum": ["beginner", "intermediate", "advanced"],
        "default": "beginner"
      }
    }
  }
}
```

## 🗄️ Neo4j Schema

Expected node types in your Neo4j database:

- **Word**: `{afrikaans, english, pronunciation, language}`
- **Story**: `{title, content, difficulty}`
- **CulturalItem**: `{name, description, category}`
- **GrammarRule**: `{rule, explanation, examples}`

## 🔧 Development

### Adding New Query Types
1. Add new pattern to `QueryProcessorNode.generate_cypher_query()`
2. Update the MCP tool schema enum
3. Test with the client

### Debugging
- Check logs for node flow: `[Input] → [Tool Node] → [Cypher Query Node] → [Output Stream]`
- Use the test client to verify each node
- Monitor SSE stream for real-time responses

## 🎯 Integration with ElevenLabs

This server provides the backend for your conversational Afrikaans agent:

1. **Voice Input** → ElevenLabs processes speech
2. **Text Query** → Sent to this MCP server
3. **Knowledge Graph** → Neo4j returns structured data
4. **SSE Stream** → Real-time response back to ElevenLabs
5. **Voice Output** → ElevenLabs speaks the response

## 🚀 Next Steps

- [ ] Add visual content nodes
- [ ] Implement conversation memory
- [ ] Add pronunciation guides
- [ ] Create interactive stories
- [ ] Build cultural context nodes

---

**Like debugging Blender GeoNodes, watch each node flow and optimize the pipeline!** 🎨 