.PHONY: help build up down restart logs clean init-rag test-classify test-rag test-plan

# Default target
help:
	@echo "Alphora Agent 101 - Development Commands"
	@echo ""
	@echo "Available commands:"
	@echo "  make build       - Build all Docker images"
	@echo "  make up          - Start all services"
	@echo "  make down        - Stop all services"
	@echo "  make restart     - Restart all services"
	@echo "  make logs        - View logs from all services"
	@echo "  make clean       - Remove all containers, volumes, and images"
	@echo "  make init-rag    - Initialize RAG database with sample SOPs"
	@echo "  make test-classify - Test ticket classification"
	@echo "  make test-rag    - Test RAG retrieval"
	@echo "  make test-plan   - Test action planning"
	@echo ""

# Build Docker images
build:
	@echo "Building Docker images..."
	docker-compose build

# Start all services
up:
	@echo "Starting all services..."
	docker-compose up -d
	@echo ""
	@echo "Services started! Waiting for them to be healthy..."
	@sleep 15
	@echo ""
	@echo "✅ Services are ready:"
	@echo "  - AI Service API: http://localhost:8000"
	@echo "  - AI Service Docs: http://localhost:8000/docs"
	@echo "  - Orchestrator: http://localhost:8080"
	@echo "  - PostgreSQL: localhost:5432"
	@echo ""
	@echo "Next step: Run 'make init-rag' to load sample SOPs"

# Stop all services
down:
	@echo "Stopping all services..."
	docker-compose down

# Restart services
restart: down up

# View logs
logs:
	docker-compose logs -f

# Clean everything
clean:
	@echo "⚠️  This will remove all containers, volumes, and images!"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker-compose down -v; \
		docker system prune -f; \
		echo "✅ Cleanup complete"; \
	fi

# Initialize RAG database
init-rag:
	@echo "Initializing RAG database..."
	@bash scripts/init-rag-data.sh

# Test ticket classification
test-classify:
	@echo "Testing ticket classification..."
	@curl -X POST http://localhost:8000/classify \
		-H "Content-Type: application/json" \
		-d '{ \
			"ticketId": "T-1001", \
			"tenantId": "tenant1", \
			"subject": "Cannot login", \
			"description": "User forgot their password and needs help resetting it" \
		}' | jq

# Test RAG retrieval
test-rag:
	@echo "Testing RAG retrieval..."
	@curl -X POST http://localhost:8000/rag \
		-H "Content-Type: application/json" \
		-d '{ \
			"ticketId": "T-1002", \
			"tenantId": "tenant1", \
			"subject": "Need password reset", \
			"description": "Employee locked out of account" \
		}' | jq

# Test action planning
test-plan:
	@echo "Testing action planning..."
	@curl -X POST http://localhost:8000/plan \
		-H "Content-Type: application/json" \
		-d '{ \
			"ticketId": "T-1003", \
			"tenantId": "tenant1", \
			"subject": "Computer running slow", \
			"description": "System needs restart to improve performance" \
		}' | jq

# Check service health
health:
	@echo "Checking service health..."
	@echo ""
	@echo "AI Service:"
	@curl -s http://localhost:8000/ | jq || echo "❌ AI Service not responding"
	@echo ""
	@echo "Orchestrator:"
	@curl -s http://localhost:8080/actuator/health | jq || echo "❌ Orchestrator not responding"
	@echo ""
	@echo "PostgreSQL:"
	@docker exec alphora-postgres pg_isready -U postgres || echo "❌ PostgreSQL not ready"