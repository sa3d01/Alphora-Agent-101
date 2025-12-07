# Alphora Agent 101 — AI-Native MSP Support Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Java 17](https://img.shields.io/badge/java-17-orange.svg)](https://openjdk.org/)

An AI-powered IT support automation engine that classifies tickets, retrieves relevant SOPs using semantic search, generates action plans, and safely executes low-risk tasks with human-in-the-loop oversight.

This repository contains the complete MVP implementation for the Alphora Agent 101 case study, demonstrating an intelligent agent system for automating L1/L2 MSP support operations.

---

## 🎯 Overview

Alphora Agent 101 transforms traditional MSP operations by:

- **Intelligent Ticket Classification**: Uses ML-based intent recognition with confidence scoring
- **Semantic SOP Retrieval**: RAG (Retrieval-Augmented Generation) system with pgvector for finding relevant procedures
- **Action Planning**: Generates step-by-step resolution plans with time estimates
- **Safety-First Execution**: Human approval gates for high-risk actions
- **Multi-Tenant Architecture**: Isolated data per MSP client

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Agent Orchestrator                        │
│              (Java Spring Boot - Port 8080)                  │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Ticket       │  │ Safety       │  │ Action       │      │
│  │ Ingestion    │──│ Gate         │──│ Executor     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      AI Service                              │
│              (Python FastAPI - Port 8000)                    │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Intent       │  │ RAG          │  │ Action       │      │
│  │ Classifier   │  │ Retrieval    │  │ Planner      │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  PostgreSQL + pgvector                       │
│                    (Port 5432)                               │
│                                                               │
│  ┌────────────────────────────────────────────────┐         │
│  │  SOP Knowledgebase (Vector Embeddings)         │         │
│  │  - Password Reset Procedures                   │         │
│  │  - System Restart Workflows                    │         │
│  │  - VPN Access Setup                            │         │
│  │  - Backup Verification                         │         │
│  └────────────────────────────────────────────────┘         │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
alphora-agent-101/
│
├── agent-orchestrator/           # Java Spring Boot Service
│   ├── src/main/java/com/alphora/agent101/
│   │   ├── controller/           # REST controllers
│   │   ├── service/              # Business logic
│   │   ├── model/                # Domain models
│   │   └── config/               # Configuration
│   ├── Dockerfile
│   ├── pom.xml
│   └── README.md
│
├── ai-service/                   # Python FastAPI Service
│   ├── rag/                      # RAG Implementation
│   │   ├── embeddings.py         # Vector embeddings (sentence-transformers)
│   │   ├── ingestion.py          # Document processing & storage
│   │   ├── retrieval.py          # Semantic search (pgvector)
│   │   ├── sample_sops.py        # Sample SOPs for testing
│   │   ├── init_database.py      # Database initialization
│   │   └── README.md
│   │
│   ├── classification/           # Intent Classification (TBD)
│   ├── actions/                  # Action Implementations (TBD)
│   ├── templates/                # Email Templates (TBD)
│   ├── safety/                   # Safety Gates (TBD)
│   │
│   ├── main.py                   # FastAPI application
│   ├── models.py                 # Pydantic models
│   ├── Dockerfile
│   └── requirements.txt
│
├── db/
│   └── schema.sql                # PostgreSQL schema with pgvector
│
├── scripts/
│   └── init-rag-data.sh          # RAG initialization script
│
├── docker-compose.yml            # Multi-service orchestration
├── Makefile                      # Development commands
├── .dockerignore
├── .gitignore
└── README.md                     # This file
```

---

## 🚀 Quick Start

### Prerequisites

- **Docker** and **Docker Compose** installed
- **Make** (optional, for convenience commands)
- **curl** and **jq** (for testing)

### Option 1: Using Make (Recommended)

```bash
# 1. Clone the repository
git clone https://github.com/sa3d01/Alphora-Agent-101.git
cd Alphora-Agent-101

# 2. Build and start all services
make build
make up

# 3. Initialize RAG database with sample SOPs
make init-rag

# 4. Test the system
make test-classify
make test-rag
make test-plan
```

### Option 2: Using Docker Compose

```bash
# 1. Clone the repository
git clone https://github.com/sa3d01/Alphora-Agent-101.git
cd Alphora-Agent-101

# 2. Start all services
docker-compose up -d

# 3. Wait for services to be healthy (30-60 seconds)
docker-compose ps

# 4. Initialize RAG database
bash scripts/init-rag-data.sh

# 5. Test the classification endpoint
curl -X POST http://localhost:8000/classify \
  -H "Content-Type: application/json" \
  -d '{
    "ticketId": "T-1001",
    "tenantId": "tenant1",
    "subject": "Cannot login",
    "description": "User forgot password"
  }' | jq
```

---

## 🔧 Services

### AI Service (Port 8000)

**FastAPI-based AI orchestration service**

- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/

**Key Endpoints:**

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/classify` | Classify ticket intent with confidence scoring |
| POST | `/rag` | Retrieve relevant SOPs using semantic search |
| POST | `/plan` | Generate action plan for ticket resolution |
| GET | `/stats/{tenant_id}` | Get RAG database statistics |

### Agent Orchestrator (Port 8080)

**Spring Boot orchestration layer**

- **Base URL**: http://localhost:8080
- **Health Check**: http://localhost:8080/actuator/health

**Key Endpoints:**

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/tickets/simulate` | Simulate complete ticket processing |

### PostgreSQL (Port 5432)

**Vector database with pgvector extension**

- **Database**: `alphora_agent`
- **User**: `postgres`
- **Password**: `postgres`

```bash
# Connect to database
docker exec -it alphora-postgres psql -U postgres -d alphora_agent

# Check SOP count
SELECT tenant_id, COUNT(*) as sop_count FROM sops GROUP BY tenant_id;
```

---

## 📊 Usage Examples

### Example 1: Password Reset Ticket

```bash
curl -X POST http://localhost:8080/tickets/simulate \
  -H "Content-Type: application/json" \
  -d '{
    "ticketId": "T-1001",
    "tenantId": "tenant1",
    "subject": "Cannot login to email",
    "description": "User forgot their password and is locked out"
  }' | jq
```

**Response:**
```json
{
  "ticketId": "T-1001",
  "intent": "PASSWORD_RESET",
  "confidence": 0.95,
  "decision": "AUTO_RESOLVE",
  "steps": [
    "Verify user identity via email",
    "Check account status in directory",
    "Generate temporary password",
    "Reset password in identity provider",
    "Send temporary password to user securely",
    "Verify successful login and password change"
  ],
  "estimated_time_minutes": 8,
  "retrieved_sops": ["Password Reset Procedure"]
}
```

### Example 2: System Restart (Requires Approval)

```bash
curl -X POST http://localhost:8080/tickets/simulate \
  -H "Content-Type: application/json" \
  -d '{
    "ticketId": "T-1002",
    "tenantId": "tenant1",
    "subject": "Server running slow",
    "description": "Production server needs restart for performance issues"
  }' | jq
```

**Response:**
```json
{
  "ticketId": "T-1002",
  "intent": "SYSTEM_RESTART",
  "confidence": 0.88,
  "decision": "HUMAN_APPROVAL",
  "reasoning": "Server restart requires approval due to production impact"
}
```

### Example 3: RAG Semantic Search

```bash
curl -X POST http://localhost:8000/rag \
  -H "Content-Type: application/json" \
  -d '{
    "ticketId": "T-1003",
    "tenantId": "tenant1",
    "subject": "VPN setup",
    "description": "New employee needs remote access"
  }' | jq
```

**Response:**
```json
{
  "query": "VPN setup New employee needs remote access",
  "tenant_id": "tenant1",
  "results": [
    {
      "sop_id": 3,
      "title": "VPN Access Setup",
      "content": "VPN Access Setup Standard Operating Procedure...",
      "category": "vpn_access",
      "similarity": 0.89,
      "chunk_index": 0
    }
  ],
  "total_results": 1
}
```

---

## 🧪 Testing

### Run All Tests

```bash
make test-classify
make test-rag
make test-plan
```

### Manual Testing

```bash
# Test classification confidence scoring
curl -X POST http://localhost:8000/classify \
  -H "Content-Type: application/json" \
  -d '{
    "ticketId": "T-TEST",
    "tenantId": "tenant1",
    "subject": "Something is broken",
    "description": "Not sure what the issue is"
  }' | jq

# Expected: Low confidence, UNKNOWN intent
```

### Check RAG Statistics

```bash
curl http://localhost:8000/stats/tenant1 | jq
```

---

## 🛠️ Development

### Local Development (Without Docker)

**Prerequisites:**
- Python 3.11+
- Java 17+
- PostgreSQL 15+ with pgvector
- Maven

#### AI Service

```bash
cd ai-service

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=alphora_agent
export DB_USER=postgres
export DB_PASSWORD=postgres

# Run the service
uvicorn main:app --reload --port 8000
```

#### Agent Orchestrator

```bash
cd agent-orchestrator

# Build and run
./mvnw spring-boot:run
```

### Adding New SOPs

```python
# Edit ai-service/rag/sample_sops.py

SAMPLE_SOPS.append({
    "tenant_id": "tenant1",
    "title": "New Procedure",
    "category": "new_category",
    "tags": ["tag1", "tag2"],
    "content": "Detailed step-by-step procedure...",
    "metadata": {
        "version": "1.0",
        "approval_required": False
    }
})

# Re-run initialization
python rag/init_database.py
```

---

## 📝 Make Commands Reference

```bash
make help          # Show all available commands
make build         # Build Docker images
make up            # Start all services
make down          # Stop all services
make restart       # Restart all services
make logs          # View logs from all services
make clean         # Remove containers, volumes, images
make init-rag      # Initialize RAG database
make test-classify # Test classification endpoint
make test-rag      # Test RAG retrieval
make test-plan     # Test action planning
make health        # Check service health
```

---

## 🗄️ Database Schema

The system uses PostgreSQL with the pgvector extension for semantic search.

### SOPs Table

```sql
CREATE TABLE sops (
    id SERIAL PRIMARY KEY,
    tenant_id VARCHAR(255) NOT NULL,
    title VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    category VARCHAR(255),
    chunk_index INTEGER,
    tags TEXT[],
    metadata JSONB,
    embedding vector(384),  -- sentence-transformers embeddings
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for vector similarity search
CREATE INDEX ON sops USING ivfflat (embedding vector_cosine_ops);

-- Index for tenant isolation
CREATE INDEX idx_sops_tenant_category ON sops(tenant_id, category);
```

---

## 🔒 Security Considerations

### Current Implementation (MVP)

- ✅ Multi-tenant data isolation via `tenant_id`
- ✅ Human approval gates for high-risk actions
- ✅ Confidence-based safety scoring
- ✅ Audit logging of all actions

### Production Requirements

- 🔲 API authentication (JWT/OAuth)
- 🔲 Role-based access control (RBAC)
- 🔲 Encrypted credentials storage
- 🔲 SOC 2 compliance logging
- 🔲 Rate limiting
- 🔲 Input validation and sanitization

---

## 🎯 Roadmap

### ✅ Phase 1: MVP (Current)
- [x] Ticket classification with confidence scoring
- [x] RAG implementation with pgvector
- [x] Sample SOP database
- [x] Action planning
- [x] Docker deployment
- [x] Basic orchestration

### 🚧 Phase 2: Core Features (Next)
- [ ] Email response generation (Requirement 6.1)
- [ ] Concrete action implementations (2-3 examples)
- [ ] Safety gate implementation
- [ ] Human-in-the-loop workflow
- [ ] LLM integration for better classification

### 📋 Phase 3: Production Features
- [ ] PSA integration (ConnectWise, Autotask)
- [ ] RMM tool integration
- [ ] Real-time action execution
- [ ] Advanced monitoring and alerts
- [ ] Multi-language support (German)
- [ ] Feedback loop for continuous improvement

### 🚀 Phase 4: Advanced Capabilities
- [ ] Fine-tuned classification models
- [ ] Agentic execution with tool chaining
- [ ] Automatic SOP generation from resolved tickets
- [ ] Predictive ticket categorization
- [ ] Integration marketplace

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Workflow

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Test locally with `make up && make init-rag`
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 👤 Author

**Saad Salem**  
Senior Backend Engineer — Java, Spring Boot, Python, AI/ML

- GitHub: [@sa3d01](https://github.com/sa3d01)
- Email: sa3dsalem01@gmail.com

---

## 🙏 Acknowledgments

- Built for Alphora Holdings case study
- Powered by [FastAPI](https://fastapi.tiangolo.com/)
- RAG implementation using [sentence-transformers](https://www.sbert.net/)
- Vector search with [pgvector](https://github.com/pgvector/pgvector)
- Orchestration with [Spring Boot](https://spring.io/projects/spring-boot)

---

## 📞 Support

For questions or issues:

1. Check the [AI Service RAG README](ai-service/rag/README.md)
2. Review the API documentation at http://localhost:8000/docs
3. Open an issue on GitHub
4. Contact the development team

---

## 🔗 Quick Links

- [AI Service Documentation](ai-service/README.md)
- [RAG Module Documentation](ai-service/rag/README.md)
- [Agent Orchestrator Documentation](agent-orchestrator/README.md)
- [API Documentation](http://localhost:8000/docs) (when running)
- [Case Study PDF](docs/Senior%20Engineer_Case.pdf)

---

**Built with ❤️ for transforming MSP operations through AI automation**