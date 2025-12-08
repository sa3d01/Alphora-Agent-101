# 🧠 Alphora Agent 101 — Minimal AI Support Agent (MVP)

This repository implements a minimal, clear, end-to-end prototype of an AI-powered L1/L2 support agent.  
It demonstrates the core building blocks expected in the assignment:

✔ Ticket classification  
✔ Lightweight RAG system  
✔ Simple retrieval mechanism  
✔ Mock actions (tools)  
✔ Full ticket → agent reasoning → action → reply simulation  

The goal is clarity, modularity, and extensibility — not production complexity.

---

## 1. 🎯 Purpose of the MVP

This codebase shows how an autonomous support agent can:

1. Understand a ticket (classification)  
2. Retrieve relevant SOPs (mini-RAG)  
3. Plan the next steps  
4. Execute mock actions  
5. Respond back to the user  

Everything is implemented with clean, minimal code to highlight architecture and reasoning.

---

## 2. 🏛️ High-Level Architecture

            ┌──────────────────┐
            │   Ticket Input    │
            └─────────┬────────┘
                      │
            ┌─────────▼─────────┐
            │  Classification     │  (LLM + heuristics)
            └─────────┬─────────┘
                      │ category
            ┌─────────▼─────────┐
            │   RAG Retrieval    │ (vector search)
            └─────────┬─────────┘
                      │ SOP context
            ┌─────────▼─────────┐
            │  Agent Reasoning   │ (LLM + tool planner)
            └─────────┬─────────┘
                      │ actions
            ┌─────────▼─────────┐
            │   Mock Actions     │ (restart/reset/etc.)
            └─────────┬─────────┘
                      │ results
            ┌─────────▼─────────┐
            │ Final Agent Reply  │
            └────────────────────┘

This flow is reproduced in `src/simulator.py`.

---


## 3. ▶️ Running the Simulation

### Install dependencies
```bash
pip install -r requirements.txt
```
### Ingest SOP documents into the vector DB
```bash
python rag/ingest.py
```
### Run the end-to-end flow
```bash
python -m src.simulator
```
You will be prompted to enter a ticket description.