# Graphiti Docker Management Makefile

.PHONY: help build up down logs shell neo4j-shell clean restart status health

# Default target
help:
	@echo "Graphiti Docker Management Commands:"
	@echo ""
	@echo "  make build     - Build all Docker images"
	@echo "  make up        - Start all services (development)"
	@echo "  make up-prod   - Start all services (production)"
	@echo "  make down      - Stop all services"
	@echo "  make logs      - Show logs for all services"
	@echo "  make logs-graph - Show logs for Graphiti service"
	@echo "  make logs-neo4j - Show logs for Neo4j service"
	@echo "  make shell     - Open shell in Graphiti container"
	@echo "  make neo4j-shell - Open Neo4j cypher shell"
	@echo "  make restart   - Restart all services"
	@echo "  make status    - Show status of all services"
	@echo "  make health    - Check health of all services"
	@echo "  make clean     - Remove all containers and volumes"
	@echo ""

# Build images
build:
	docker-compose build --no-cache

# Start services (development)
up:
	@echo "Starting Graphiti with Neo4j in development mode..."
	docker-compose up -d
	@echo "Services started! Access:"
	@echo "  - Graphiti API: http://localhost:8000"
	@echo "  - Neo4j Browser: http://localhost:7474"
	@echo "  - Neo4j Credentials: neo4j/\$$NEO4J_PASSWORD"

# Start services (production)
up-prod:
	@echo "Starting Graphiti with Neo4j in production mode..."
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
	@echo "Production services started!"

# Stop services
down:
	docker-compose down

# Show logs
logs:
	docker-compose logs -f

logs-graph:
	docker-compose logs -f graph

logs-neo4j:
	docker-compose logs -f neo4j

# Open shell in Graphiti container
shell:
	docker-compose exec graph bash

# Open Neo4j cypher shell
neo4j-shell:
	docker-compose exec neo4j cypher-shell -u neo4j -p $(shell grep NEO4J_PASSWORD .env | cut -d '=' -f2)

# Restart services
restart:
	docker-compose restart

# Show status
status:
	docker-compose ps

# Check health
health:
	@echo "Checking Graphiti health..."
	@curl -f http://localhost:8000/healthcheck && echo "✅ Graphiti is healthy" || echo "❌ Graphiti is not responding"
	@echo "Checking Neo4j health..."
	@curl -f http://localhost:7474 && echo "✅ Neo4j is healthy" || echo "❌ Neo4j is not responding"

# Clean up everything
clean:
	@echo "⚠️  This will remove all containers, volumes, and data!"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker-compose down -v --remove-orphans; \
		docker system prune -f; \
		echo "✅ Cleanup completed"; \
	else \
		echo "❌ Cleanup cancelled"; \
	fi