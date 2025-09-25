#!/bin/bash

# Graphiti Health Check Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

echo "🔍 Graphiti Health Check"

# Check if services are running
print_status "Checking Docker containers..."
if docker-compose ps | grep -q "Up"; then
    print_success "Docker containers are running"
else
    print_error "Docker containers are not running"
    exit 1
fi

# Check Graphiti API
print_status "Checking Graphiti API..."
if curl -f http://localhost:8000/healthcheck &> /dev/null; then
    print_success "Graphiti API is responding"
    
    # Get API version info
    API_INFO=$(curl -s http://localhost:8000/healthcheck 2>/dev/null || echo "{}")
    if [ "$API_INFO" != "{}" ]; then
        echo "  API Response: $API_INFO"
    fi
else
    print_error "Graphiti API is not responding"
fi

# Check Neo4j
print_status "Checking Neo4j..."
if curl -f http://localhost:7474 &> /dev/null; then
    print_success "Neo4j is responding"
    
    # Try to connect to Neo4j
    if docker-compose exec neo4j cypher-shell -u neo4j -p "$(grep NEO4J_PASSWORD .env | cut -d '=' -f2)" "RETURN 1 as test" &> /dev/null; then
        print_success "Neo4j database connection successful"
    else
        print_warning "Neo4j database connection failed"
    fi
else
    print_error "Neo4j is not responding"
fi

# Check environment variables
print_status "Checking environment configuration..."
if [ -f .env ]; then
    print_success ".env file exists"
    
    if grep -q "OPENAI_API_KEY=" .env && ! grep -q "your_openai_api_key_here" .env; then
        print_success "OpenAI API key is configured"
    else
        print_warning "OpenAI API key is not configured"
    fi
    
    if grep -q "NEO4J_PASSWORD=" .env && ! grep -q "secure_password_here" .env; then
        print_success "Neo4j password is configured"
    else
        print_warning "Neo4j password is not configured"
    fi
else
    print_error ".env file is missing"
fi

echo ""
echo "📊 Health Check Summary:"
echo "  - Graphiti API: $(curl -f http://localhost:8000/healthcheck &> /dev/null && echo "✅ Healthy" || echo "❌ Unhealthy")"
echo "  - Neo4j Browser: $(curl -f http://localhost:7474 &> /dev/null && echo "✅ Healthy" || echo "❌ Unhealthy")"
echo "  - Environment: $([ -f .env ] && echo "✅ Configured" || echo "❌ Missing")"

