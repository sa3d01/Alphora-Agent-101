# Alphora Agent 101 — MVP Implementation

An AI-assisted IT support automation engine that classifies tickets, retrieves SOPs, generates action plans, and safely auto-executes low-risk tasks.

This repository contains the complete MVP implementation delivered as part of the Alphora Agent 101 case study.

---

## Project Structure

```
alphora-agent-101/
│
├── agent-orchestrator/        # Spring Boot (Ticket Orchestrator)
│   ├── src/main/java/com/alphora/agent101
│   ├── pom.xml
│   └── README.md
│
├── ai-service/                # Python FastAPI (AI Layer)
│   ├── main.py
│   ├── models.py
│   ├── requirements.txt
│   └── README.md
│
└── db/
    └── schema.sql             # pgvector-ready structure (future RAG)
```

---

## Components Overview

### 1. Orchestrator (Java / Spring Boot)

Responsible for:
- Receiving incoming tickets
- Calling AI endpoints (`/classify`, `/rag`, `/plan`)
- Applying the Safety Gate
- Generating the final decision
- Triggering mock execution (`/execute-mock`)

### 2. AI Service (Python / FastAPI)

Handles:
- Ticket classification
- Mock RAG SOP retrieval
- Plan generation (deterministic)
- Mock execution engine

### 3. Database Schema (Optional for MVP)

`db/schema.sql` includes:
- `pgvector` extension
- SOP embedding table
- Ready for future semantic search

---

# Tech Stack

### Backend
- Java 17
- Spring Boot 3
- Maven
- WebClient

### AI Layer
- Python 3.11
- FastAPI
- Pydantic v2
- Uvicorn

---

# Running the System

## 1. Start the AI Service

```
cd ai-service
pyenv local 3.11.6
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

uvicorn main:app --reload --port 8000
```

API Docs: http://localhost:8000/docs

---

## 2. Start the Orchestrator

```
cd agent-orchestrator
./mvnw spring-boot:run
```

Service available at:  
http://localhost:8080

---

# API Usage

## Simulate Ticket Processing

```
curl -X POST http://localhost:8080/tickets/simulate \
  -H "Content-Type: application/json" \
  -d '{
    "ticketId": "T-1001",
    "tenantId": "tenant1",
    "subject": "Cannot login",
    "description": "User needs a VPN password reset"
  }'
```

### Sample Response

```json
{
  "ticketId": "T-1001",
  "intent": "PASSWORD_RESET",
  "decision": "AUTO_RESOLVE",
  "steps": [
    "Verify requester identity via email",
    "Reset password in IdP",
    "Force password change on next login",
    "Notify user with temporary password"
  ]
}
```

---

# AI Service Endpoints

| Method | Endpoint        | Description             |
|--------|------------------|-------------------------|
| POST   | /classify        | Predict ticket intent   |
| POST   | /rag             | Return mock SOPs        |
| POST   | /plan            | Generate action plan    |
| POST   | /execute-mock    | Simulate SOP execution  |

---

# Sample MVP Tickets

### Password Reset → AUTO_RESOLVE
### Printer Issue → AUTO_RESOLVE
### VPN Access Setup → AUTO_RESOLVE

Full examples documented in the case study.

---

# Roadmap

- Integrate pgvector RAG
- Add LLM-based planning
- Connect to real PSA (ConnectWise / Autotask)
- RBAC and permissions engine
- Agentic execution plugins
- Observability, audit logs, metrics

---

# Author

Built by **Saad Salem**  
Senior Backend Engineer — Java, Spring Boot, Python, Automation
