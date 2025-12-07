# Alphora Agent 101 — AI-Native MSP Support Platform

An AI-powered IT support automation engine for the Alphora Holdings case study.

## 🎯 Features

- **Ticket Classification** with confidence scoring (8+ intent types)
- **RAG (Retrieval-Augmented Generation)** semantic search with pgvector
- **Action Planning** with step-by-step procedures
- **Multi-tenant** data isolation

## 🏗️ Architecture
```
┌─────────────────┐
│  Orchestrator   │  (Java Spring Boot - Port 8080)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   AI Service    │  (Python FastAPI - Port 8000)
│  • Classification
│  • RAG Retrieval
│  • Action Plans
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  PostgreSQL     │  (pgvector - Port 5432)
│  • 4 Sample SOPs
│  • 37 chunks
└─────────────────┘
```

## 🚀 Quick Start (3 Steps)

### Prerequisites
- Docker & Docker Compose
- 4GB RAM available

### Setup
```bash
# 1. Clone repository
git clone https://github.com/sa3d01/Alphora-Agent-101.git
cd Alphora-Agent-101

# 2. Start all services
docker-compose up -d

# 3. Wait 30 seconds, then initialize RAG database
sleep 30
docker-compose exec ai-service python rag/init_database.py
```

### Verify Installation
```bash
# Check services are running
docker-compose ps

# Test classification
curl -X POST http://localhost:8000/classify \
  -H "Content-Type: application/json" \
  -d '{
    "ticketId": "T-1001",
    "tenantId": "tenant1",
    "subject": "Password reset needed",
    "description": "User forgot their password"
  }'

# Expected response:
# {
#   "intent": "PASSWORD_RESET",
#   "confidence": 0.93,
#   "is_automatable": true,
#   ...
# }
```

## 📡 API Endpoints

### AI Service (http://localhost:8000)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/docs` | GET | Interactive API documentation |
| `/classify` | POST | Classify ticket intent with confidence |
| `/rag` | POST | Retrieve relevant SOPs |
| `/plan` | POST | Generate action plan |
| `/stats/{tenant_id}` | GET | RAG database statistics |

### Orchestrator (http://localhost:8080)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/tickets/simulate` | POST | Complete ticket processing flow |

## 📊 Usage Examples

### 1. Test Classification with Confidence Scoring
```bash
# High confidence - specific keywords
curl -X POST http://localhost:8000/classify \
  -H "Content-Type: application/json" \
  -d '{
    "ticketId": "T-1",
    "tenantId": "tenant1",
    "subject": "Password reset",
    "description": "User locked out of account"
  }'

# Response: PASSWORD_RESET with ~0.93 confidence

# Low confidence - vague request
curl -X POST http://localhost:8000/classify \
  -H "Content-Type: application/json" \
  -d '{
    "ticketId": "T-2",
    "tenantId": "tenant1",
    "subject": "Cannot login",
    "description": "User forgot something"
  }'

# Response: UNKNOWN or low confidence
```

### 2. Test RAG Semantic Search
```bash
curl -X POST http://localhost:8000/rag \
  -H "Content-Type: application/json" \
  -d '{
    "ticketId": "T-3",
    "tenantId": "tenant1",
    "subject": "VPN access needed",
    "description": "New employee needs remote access setup"
  }'

# Returns relevant SOP chunks with similarity scores
```

### 3. Get Action Plan
```bash
curl -X POST http://localhost:8000/plan \
  -H "Content-Type: application/json" \
  -d '{
    "ticketId": "T-4",
    "tenantId": "tenant1",
    "subject": "System restart required",
    "description": "Server running slow"
  }'

# Returns step-by-step action plan with time estimates
```

### 4. Check RAG Statistics
```bash
curl http://localhost:8000/stats/tenant1

# Response:
# {
#   "total_sops": 4,
#   "total_chunks": 37,
#   "categories": ["password_reset", "system_restart", "vpn_access", "backup_verification"]
# }
```

## 📁 Project Structure
```
alphora-agent-101/
├── docker-compose.yml          # Multi-service orchestration
├── ai-service/
│   ├── Dockerfile
│   ├── main.py                 # FastAPI app with RAG integration
│   ├── requirements.txt
│   └── rag/                    # RAG implementation
│       ├── embeddings.py       # sentence-transformers (384d)
│       ├── ingestion.py        # Document chunking & storage
│       ├── retrieval.py        # pgvector semantic search
│       ├── sample_sops.py      # 4 sample SOPs
│       └── init_database.py    # Database initialization
├── agent-orchestrator/
│   ├── Dockerfile
│   └── src/                    # Spring Boot application
└── db/
    └── schema.sql              # PostgreSQL + pgvector schema
```

## 🗄️ Sample Data

### 4 Sample SOPs (37 total chunks)

1. **Password Reset Procedure** (8 chunks)
    - Identity verification steps
    - Account status checks
    - Secure password generation
    - User communication protocols

2. **System Restart Procedure** (11 chunks)
    - Pre-restart assessments
    - User notification protocols
    - Windows/Linux restart commands
    - Post-restart verification

3. **VPN Access Setup** (14 chunks)
    - Request validation
    - Security compliance checks
    - MFA configuration
    - Client deployment steps

4. **Backup Verification** (4 chunks)
    - Job status checks
    - Integrity verification
    - Test restore procedures

## 🛠️ Common Commands
```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f ai-service

# Restart a service
docker-compose restart ai-service

# Initialize/reinitialize RAG database
docker-compose exec ai-service python rag/init_database.py

# Check database
docker-compose exec postgres psql -U postgres -d alphora_agent -c "SELECT COUNT(*) FROM sops;"

# Access interactive API docs
open http://localhost:8000/docs
```

## 🧪 Testing Different Ticket Types
```bash
# Password Reset (High Confidence)
curl -X POST http://localhost:8000/classify \
  -H "Content-Type: application/json" \
  -d '{"ticketId":"T-1","tenantId":"tenant1","subject":"Password reset","description":"User locked out"}'

# System Restart (Medium Confidence)
curl -X POST http://localhost:8000/classify \
  -H "Content-Type: application/json" \
  -d '{"ticketId":"T-2","tenantId":"tenant1","subject":"Computer slow","description":"Need to restart"}'

# VPN Access (High Confidence)
curl -X POST http://localhost:8000/classify \
  -H "Content-Type: application/json" \
  -d '{"ticketId":"T-3","tenantId":"tenant1","subject":"Remote access","description":"Need VPN setup"}'

# Unknown Intent (Low Confidence)
curl -X POST http://localhost:8000/classify \
  -H "Content-Type: application/json" \
  -d '{"ticketId":"T-4","tenantId":"tenant1","subject":"Something broken","description":"Not working"}'
```

## 🐛 Troubleshooting

### Services won't start
```bash
# Check logs
docker-compose logs

# Restart everything
docker-compose down
docker-compose up -d
```

### RAG initialization fails
```bash
# Check if database is ready
docker-compose exec postgres pg_isready -U postgres

# Drop and recreate table
docker-compose exec postgres psql -U postgres -d alphora_agent -c "DROP TABLE IF EXISTS sops CASCADE;"
docker-compose exec postgres psql -U postgres -d alphora_agent -f /tmp/schema.sql

# Reinitialize
docker-compose exec ai-service python rag/init_database.py
```

### No RAG results returned
```bash
# Check if SOPs are ingested
docker-compose exec postgres psql -U postgres -d alphora_agent -c "SELECT COUNT(*) FROM sops;"

# Should return: 37
# If 0, reinitialize database
```

### Port conflicts
```bash
# Check what's using ports
lsof -ti:8000
lsof -ti:8080
lsof -ti:5432

# Kill processes if needed
lsof -ti:8000 | xargs kill -9
```

### Container name issues
```bash
# Find actual container names
docker ps

# Use docker-compose exec (works with service names)
docker-compose exec ai-service python rag/init_database.py
```

## 📋 Case Study Requirements Status

### ✅ Completed (Phase 1)
- [x] **6.2** Ticket Classification
    - Intent recognition (8+ types)
    - Confidence scoring (0.0-1.0)
    - Automatable flag
    - Required keyword matching

- [x] **6.3** RAG Database & Retrieval
    - Embedding generation (sentence-transformers)
    - Document chunking (paragraph-based)
    - Vector storage (pgvector, 384 dimensions)
    - Semantic search (cosine similarity)
    - Multi-tenant isolation
    - 4 sample SOPs with 37 chunks

### 🚧 Next Steps (Phase 2)
- [ ] **6.1** Email response generation (human-in-the-loop)
- [ ] **6.4** Action implementations (2-3 concrete examples)
- [ ] Safety gate implementation
- [ ] LLM integration for better classification

## 🔧 Technology Stack

- **Backend**: Python 3.11 (FastAPI), Java 17 (Spring Boot)
- **Database**: PostgreSQL 15 + pgvector
- **Embeddings**: sentence-transformers (all-MiniLM-L6-v2, 384 dimensions)
- **Deployment**: Docker Compose
- **Vector Search**: Cosine similarity via pgvector

## 📚 Documentation

- **Interactive API Docs**: http://localhost:8000/docs (when running)
- **RAG Module Details**: See `ai-service/rag/README.md`
- **Case Study**: See `Senior Engineer_Case.pdf`

## 👤 Author

**Saad Salem**  
Senior Backend Engineer

- GitHub: [@sa3d01](https://github.com/sa3d01)
- Email: sa3dsalem01@gmail.com

---

## 💡 Key Features Demonstrated

1. **Semantic Search**: RAG system finds relevant procedures without exact keyword matching
2. **Confidence Scoring**: Classification includes confidence levels for safety decisions
3. **Multi-tenancy**: Data isolation per MSP client via `tenant_id`
4. **Docker Deployment**: One-command setup with docker-compose
5. **Production-Ready Schema**: pgvector for scalable similarity search

---

**Built for Alphora Holdings Case Study — Demonstrating AI-powered MSP automation**