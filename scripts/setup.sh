#!/bin/bash

# Graphiti Docker Setup Script
# This script sets up the complete Graphiti environment

set -e

echo "🚀 Setting up Graphiti Docker Environment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

print_status "Docker and Docker Compose are available"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    print_status "Creating .env file from template..."
    cp .env.example .env
    print_warning "Please edit .env file and add your API keys before starting the services"
    print_warning "Required: OPENAI_API_KEY"
    print_warning "Optional: ANTHROPIC_API_KEY"
else
    print_success ".env file already exists"
fi

# Check if OpenAI API key is set
if grep -q "your_openai_api_key_here\|your-openai-api-key-here" .env; then
    print_warning "OpenAI API key not set in .env file"
    print_warning "Please edit .env and add your OPENAI_API_KEY before starting services"
fi

# Build Docker images
print_status "Building Docker images..."
docker-compose build

# Start services
print_status "Starting services..."
docker-compose up -d

# Wait for services to be ready
print_status "Waiting for services to be ready..."
sleep 10

# Check service health
print_status "Checking service health..."

# Check Graphiti
if curl -f http://localhost:8000/healthcheck &> /dev/null; then
    print_success "Graphiti service is healthy"
else
    print_warning "Graphiti service is not yet ready"
fi

# Check Neo4j
if curl -f http://localhost:7474 &> /dev/null; then
    print_success "Neo4j service is healthy"
else
    print_warning "Neo4j service is not yet ready"
fi

print_success "Setup completed!"
echo ""
echo "🌐 Access your services:"
echo "  - Graphiti API: http://localhost:8000"
echo "  - Neo4j Browser: http://localhost:7474"
echo "  - Neo4j Credentials: neo4j/\$(grep NEO4J_PASSWORD .env | cut -d '=' -f2)"
echo ""
echo "📋 Useful commands:"
echo "  - View logs: make logs"
echo "  - Check status: make status"
echo "  - Stop services: make down"
echo "  - Open shell: make shell"
echo ""
