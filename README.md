# Alphora Agent 101 — Mock MSP Support Agent

This repository contains a **small, self-contained demo** of an AI-powered MSP support agent
for the *Alphora Agent 101* case study.

It is **not** a production system.  
It is designed to **show my thinking** around:

- Ticket classification
- RAG-based SOP retrieval
- Agent-style action planning
- Mock tool execution
- Human-in-the-loop email drafting

---

## 1. High-Level Architecture

```mermaid
flowchart LR
    PSA[PSA / Ticket System] -->|webhook / polling| Ingest[Ticket Ingestion]
    Ingest --> Classifier[Intent Classification]
    Ingest --> Context[Client Context]

    Classifier --> RAG[RAG KB -SOPs, configs]
    Context --> RAG

    RAG --> Planner[Action Planner]
    Classifier --> Planner

    Planner --> Tools[AI Tool Workbench]
    Planner --> Email[Email Draft Generator]

    Tools --> Scribe[Alphora Scribe / Logging]
    Email --> PSA
    Tools --> PSA
