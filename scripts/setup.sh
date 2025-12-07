#!/bin/bash

# Alphora Agent 101 - Setup Script
# This script sets up the entire system from scratch

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored message
print_message() {
    echo -e "${2}${1}${NC}"
}

print_header() {
    echo ""
    echo "=========================================="
    print_message "$1" "$BLUE"
    echo "=========================================="
}

print_success() {
    print_message "✅ $1" "$GREEN"
}

print_error() {
    print_message "❌ $1" "$RED"
}

print_warning() {
    print_message "⚠️  $1" "$YELLOW"
}

# Check prerequisites
check_prerequisites() {
    print_header "Checking Prerequisites"

    # Check Docker
    if command -v docker &> /dev/null; then
        DOCKER_VERSION=$(docker --version)
        print_success "Docker installed: $DOCKER_VERSION"
    else
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi

    # Check Docker Compose
    if command -v docker-compose &> /dev/null; then
        COMPOSE_VERSION=$(docker-compose --version)
        print_success "Docker Compose installed: $COMPOSE_VERSION"
    else
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi

    # Check if Docker daemon is running
    if docker info &> /dev/null; then
        print_success "Docker daemon is running"
    else
        print_error "Docker daemon is not running. Please start Docker."
        exit 1
    fi

    # Check optional tools
    if command -v curl &> /dev/null; then
        print_success "curl installed"
    else
        print_warning "curl not found (optional for testing)"
    fi

    if command -v jq &> /dev/null; then
        print_success "jq installed"
    else
        print_warning "jq not found (optional for pretty JSON)"
    fi
}

# Clean existing setup
clean_existing() {
    print_header "Cleaning Existing Setup"

    if [ "$(docker ps -q -f name=alphora)" ]; then
        print_message "Stopping existing containers..." "$YELLOW"
        docker-compose down -v
        print_success "Existing containers stopped and removed"
    else
        print_success "No existing containers found"
    fi
}

# Build images
build_images() {
    print_header "Building Docker Images"

    print_message "Building AI Service (Python FastAPI)..." "$YELLOW"
    print_message "Building Agent Orchestrator (Java Spring Boot)..." "$YELLOW"
    print_message "This may take 3-5 minutes..." "$YELLOW"

    if docker-compose build; then
        print_success "All images built successfully"
    else
        print_error "Failed to build images"
        exit 1
    fi
}

# Start services
start_services() {
    print_header "Starting Services"

    print_message "Starting PostgreSQL, AI Service, and Orchestrator..." "$YELLOW"

    if docker-compose up -d; then
        print_success "All services started"
    else
        print_error "Failed to start services"
        exit 1
    fi
}

# Wait for services
wait_for_services() {
    print_header "Waiting for Services to be Healthy"

    print_message "This may take 30-60 seconds..." "$YELLOW"

    # Wait for PostgreSQL
    print_message "Waiting for PostgreSQL..." "$YELLOW"
    for i in {1..30}; do
        if docker exec alphora-postgres pg_isready -U postgres &> /dev/null; then
            print_success "PostgreSQL is ready"
            break
        fi
        sleep 2
        if [ $i -eq 30 ]; then
            print_error "PostgreSQL failed to start"
            exit 1
        fi
    done

    # Wait for AI Service
    print_message "Waiting for AI Service..." "$YELLOW"
    print_message "(First start downloads embedding model ~80MB)" "$YELLOW"
    for i in {1..60}; do
        if curl -s http://localhost:8000/ &> /dev/null; then
            print_success "AI Service is ready"
            break
        fi
        sleep 2
        if [ $i -eq 60 ]; then
            print_error "AI Service failed to start"
            print_message "Check logs: docker-compose logs ai-service" "$RED"
            exit 1
        fi
    done

    # Wait for Orchestrator
    print_message "Waiting for Orchestrator..." "$YELLOW"
    for i in {1..30}; do
        if curl -s http://localhost:8080/actuator/health &> /dev/null; then
            print_success "Orchestrator is ready"
            break
        fi
        sleep 2
        if [ $i -eq 30 ]; then
            print_error "Orchestrator failed to start"
            print_message "Check logs: docker-compose logs agent-orchestrator" "$RED"
            exit 1
        fi
    done
}

# Initialize RAG
initialize_rag() {
    print_header "Initializing RAG Database"

    print_message "Ingesting sample SOPs..." "$YELLOW"

    if docker exec alphora-ai-service python rag/init_database.py; then
        print_success "RAG database initialized successfully"
    else
        print_error "Failed to initialize RAG database"
        exit 1
    fi
}

# Run tests
run_tests() {
    print_header "Running System Tests"

    # Test classification
    print_message "Testing classification endpoint..." "$YELLOW"
    CLASSIFY_RESPONSE=$(curl -s -X POST http://localhost:8000/classify \
        -H "Content-Type: application/json" \
        -d '{
            "ticketId": "TEST-001",
            "tenantId": "tenant1",
            "subject": "Cannot login",
            "description": "User forgot password"
        }')

    if echo "$CLASSIFY_RESPONSE" | grep -q "PASSWORD_RESET"; then
        print_success "Classification test passed"
    else
        print_warning "Classification test returned unexpected result"
    fi

    # Test RAG
    print_message "Testing RAG retrieval..." "$YELLOW"
    RAG_RESPONSE=$(curl -s -X POST http://localhost:8000/rag \
        -H "Content-Type: application/json" \
        -d '{
            "ticketId": "TEST-002",
            "tenantId": "tenant1",
            "subject": "Password reset",
            "description": "User locked out"
        }')

    if echo "$RAG_RESPONSE" | grep -q "Password Reset Procedure"; then
        print_success "RAG retrieval test passed"
    else
        print_warning "RAG test returned unexpected result"
    fi

    # Check database
    print_message "Checking database..." "$YELLOW"
    SOP_COUNT=$(docker exec alphora-postgres psql -U postgres -d alphora_agent -t -c "SELECT COUNT(*) FROM sops;")
    SOP_COUNT=$(echo $SOP_COUNT | tr -d ' ')

    if [ "$SOP_COUNT" -ge 20 ]; then
        print_success "Database contains $SOP_COUNT SOP chunks"
    else
        print_warning "Database contains only $SOP_COUNT chunks (expected 20+)"
    fi
}

# Print summary
print_summary() {
    print_header "Setup Complete! 🎉"

    echo ""
    print_message "Services are running:" "$GREEN"
    echo "  • AI Service:        http://localhost:8000"
    echo "  • API Docs:          http://localhost:8000/docs"
    echo "  • Orchestrator:      http://localhost:8080"
    echo "  • PostgreSQL:        localhost:5432"
    echo ""
    print_message "Quick Commands:" "$BLUE"
    echo "  • View logs:         docker-compose logs -f"
    echo "  • Stop services:     docker-compose down"
    echo "  • Restart:           docker-compose restart"
    echo "  • Run tests:         make test-classify && make test-rag"
    echo ""
    print_message "Next Steps:" "$YELLOW"
    echo "  1. Visit http://localhost:8000/docs to explore the API"
    echo "  2. Try the example requests in README.md"
    echo "  3. Check GETTING_STARTED.md for detailed usage"
    echo ""
    print_success "Happy coding!"
}

# Main execution
main() {
    clear
    print_header "Alphora Agent 101 - Setup Script"

    check_prerequisites

    # Ask user if they want to clean
    if [ "$(docker ps -q -f name=alphora)" ]; then
        echo ""
        read -p "Existing containers found. Clean and rebuild? [y/N] " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            clean_existing
        fi
    fi

    build_images
    start_services
    wait_for_services
    initialize_rag
    run_tests
    print_summary
}

# Run main
main