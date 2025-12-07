#!/bin/bash

# Initialize RAG database with sample SOPs
# This script should be run after containers are up and healthy

set -e

echo "=========================================="
echo "Initializing RAG Database"
echo "=========================================="

# Wait for services to be healthy
echo "Waiting for services to be ready..."
sleep 10

# Check if AI service is running
echo "Checking AI service health..."
until curl -s http://localhost:8000/ > /dev/null; do
echo "Waiting for AI service..."
sleep 5
done

echo "✅ AI service is healthy"

# Run initialization script
echo ""
echo "Ingesting sample SOPs..."
docker exec alphora-agent-101-ai-service-1 python rag/init_database.py

echo ""
echo "=========================================="
echo "✅ RAG Database Initialized Successfully"
echo "=========================================="
echo ""
echo "You can now test the system:"
echo "  - API Docs: http://localhost:8000/docs"
echo "  - Orchestrator: http://localhost:8080"
echo ""