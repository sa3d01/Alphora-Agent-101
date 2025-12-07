# RAG (Retrieval-Augmented Generation) Module

This module implements the RAG system for Alphora Agent 101, enabling semantic search over SOP documentation.

## Components

### 1. `embeddings.py`
- **Purpose**: Generate vector embeddings for text using sentence-transformers
- **Model**: `all-MiniLM-L6-v2` (384 dimensions, fast and efficient)
- **Key Functions**:
    - `embed_text()`: Generate embedding for a single text
    - `embed_batch()`: Efficiently embed multiple texts
    - `compute_similarity()`: Calculate cosine similarity between embeddings

### 2. `ingestion.py`
- **Purpose**: Process and store SOPs in the vector database
- **Features**:
    - Document chunking (paragraph and sentence-based strategies)
    - Batch ingestion for multiple SOPs
    - Multi-tenant data isolation
- **Key Classes**:
    - `DocumentChunker`: Splits documents into semantic chunks
    - `SOPIngester`: Handles database storage with embeddings

### 3. `retrieval.py`
- **Purpose**: Semantic search over stored SOPs using pgvector
- **Search Methods**:
    - `search()`: General semantic search with similarity threshold
    - `search_by_category()`: Filter by category without semantic search
    - `hybrid_search()`: Combine category filtering with semantic search
    - `get_sop_by_title()`: Retrieve specific SOP by exact title
- **Key Features**:
    - Multi-tenant isolation (tenant_id filtering)
    - Similarity scoring (cosine distance)
    - Top-k results with configurable threshold

### 4. `sample_sops.py`
- **Purpose**: Sample SOPs for testing and demonstration
- **Included SOPs**:
    - Password Reset Procedure (detailed, step-by-step)
    - System Restart Procedure (Windows and Linux)
    - VPN Access Setup (with security requirements)
    - Backup Verification Procedure

### 5. `init_database.py`
- **Purpose**: Initialize database with sample SOPs
- **Usage**: Run once to populate the database

## Setup Instructions

### 1. Install Dependencies

```bash
cd ai-service
pip install -r requirements.txt
```

### 2. Setup PostgreSQL with pgvector

```bash
# Install PostgreSQL (if not already installed)
# On Ubuntu/Debian:
sudo apt-get install postgresql postgresql-contrib

# Install pgvector extension
sudo apt-get install postgresql-15-pgvector

# Or using Docker:
docker run -d \
  --name alphora-postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=alphora_agent \
  -p 5432:5432 \
  pgvector/pgvector:pg15
```

### 3. Create Database Schema

```bash
psql -h localhost -U postgres -d alphora_agent -f ../db/schema.sql
```

### 4. Initialize with Sample SOPs

```bash
cd rag
python init_database.py
```

**Expected Output:**
```
Initializing RAG database...
Connecting to: localhost:5432/alphora_agent

Found 4 sample SOPs to ingest

Ingesting SOPs...
Created 8 chunks for SOP: Password Reset Procedure
Successfully ingested 8 chunks
Created 6 chunks for SOP: System Restart Procedure
Successfully ingested 6 chunks
Created 7 chunks for SOP: VPN Access Setup
Successfully ingested 7 chunks
Created 4 chunks for SOP: Backup Verification Procedure
Successfully ingested 4 chunks

==================================================
INGESTION COMPLETE
==================================================
Total SOPs: 4
Successful: 4
Failed: 0
Total chunks created: 25
==================================================

✅ Database initialized successfully!
```

## Usage Examples

### Example 1: Semantic Search

```python
from rag.retrieval import SOPRetriever

# Initialize retriever
db_config = {
    'host': 'localhost',
    'port': '5432',
    'database': 'alphora_agent',
    'user': 'postgres',
    'password': 'postgres'
}
retriever = SOPRetriever(db_config)

# Search for relevant SOPs
results = retriever.search(
    query="User cannot login and needs password reset",
    tenant_id="tenant1",
    top_k=3,
    similarity_threshold=0.5
)

for result in results:
    print(f"Title: {result['title']}")
    print(f"Similarity: {result['similarity']:.2f}")
    print(f"Content: {result['content'][:200]}...")
    print("-" * 50)
```

### Example 2: Hybrid Search (Category + Semantic)

```python
# When you know the category (from classification)
results = retriever.hybrid_search(
    query="How do I safely restart a server?",
    tenant_id="tenant1",
    category="system_restart",
    top_k=3
)
```

### Example 3: Get Statistics

```python
stats = retriever.get_statistics("tenant1")
print(f"Total SOPs: {stats['total_sops']}")
print(f"Total Chunks: {stats['total_chunks']}")
print(f"Categories: {stats['categories']}")
```

## API Integration

The RAG system is integrated into the FastAPI application:

### Endpoint: `POST /rag`

```bash
curl -X POST http://localhost:8000/rag \
  -H "Content-Type: application/json" \
  -d '{
    "ticketId": "T-1001",
    "tenantId": "tenant1",
    "subject": "Cannot login",
    "description": "User forgot their password and needs help resetting it"
  }'
```

**Response:**
```json
{
  "query": "Cannot login User forgot their password and needs help resetting it",
  "tenant_id": "tenant1",
  "results": [
    {
      "sop_id": 1,
      "title": "Password Reset Procedure",
      "content": "Password Reset Standard Operating Procedure\n\nPurpose: This procedure outlines...",
      "category": "password_reset",
      "similarity": 0.87,
      "chunk_index": 0
    }
  ],
  "total_results": 1
}
```

## Architecture

```
┌─────────────────┐
│  Ticket Query   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Embedding     │  ← sentence-transformers
│   Generation    │     (all-MiniLM-L6-v2)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   pgvector      │  ← Vector similarity search
│   Database      │     (cosine distance)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Ranked SOPs    │  ← Top-k results with scores
└─────────────────┘
```

## Performance Considerations

- **Embedding Model**: `all-MiniLM-L6-v2` is optimized for speed
    - 384 dimensions (smaller than alternatives)
    - ~14MB model size
    - Fast inference on CPU
    - Consider `all-mpnet-base-v2` (768d) for better quality if needed

- **Chunking Strategy**:
    - Default: 500 characters per chunk with 50 char overlap
    - Preserves paragraph boundaries
    - Adjust based on SOP structure

- **Database Indexing**:
    - pgvector uses IVFFlat or HNSW indexes
    - Add index for production: `CREATE INDEX ON sops USING ivfflat (embedding vector_cosine_ops);`

## Multi-Tenancy

All queries include `tenant_id` filtering to ensure:
- Data isolation between MSP clients
- Each tenant only sees their own SOPs
- Prevents data leakage across organizations

## Future Enhancements

1. **LLM Integration**: Use LLM to generate summaries of retrieved SOPs
2. **Hybrid Search**: Combine vector search with full-text search (BM25)
3. **Feedback Loop**: Track which SOPs resolve tickets successfully
4. **Auto-Ingestion**: Automatically ingest new SOPs from document repositories
5. **Version Control**: Track SOP versions and updates
6. **Multi-Language**: Support German and other European languages

## Troubleshooting

### Issue: "relation 'sops' does not exist"
**Solution**: Run the database schema creation script first:
```bash
psql -h localhost -U postgres -d alphora_agent -f ../db/schema.sql
```

### Issue: "ModuleNotFoundError: No module named 'sentence_transformers'"
**Solution**: Install dependencies:
```bash
pip install -r requirements.txt
```

### Issue: Slow first query
**Cause**: Embedding model loads on first use (~2-3 seconds)
**Solution**: This is normal; subsequent queries are fast

### Issue: Low similarity scores
**Solution**:
- Check if SOPs are properly ingested
- Verify query matches SOP content
- Lower similarity threshold (default: 0.5)
- Consider using hybrid search with category filter