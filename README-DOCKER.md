# Graphiti Docker Installation

Installazione dockerizzata completa di Graphiti con Neo4j per la costruzione di Knowledge Graphs in tempo reale per AI Agents.

## 🚀 Quick Start

### Prerequisiti

- Docker e Docker Compose installati
- Chiave API OpenAI (opzionale: Anthropic)

### Installazione Automatica

```bash
# Clona il repository (già fatto)
git clone https://github.com/getzep/graphiti.git

# Setup automatico
./scripts/setup.sh
```

### Installazione Manuale

1. **Configura le variabili d'ambiente:**
```bash
cp .env.example.local .env
# Modifica .env con le tue API keys
```

2. **Avvia i servizi:**
```bash
make up
# oppure
docker-compose up -d
```

3. **Verifica l'installazione:**
```bash
make health
# oppure
./scripts/health-check.sh
```

## 🌐 Accesso ai Servizi

- **Graphiti API**: http://localhost:8000
- **Neo4j Browser**: http://localhost:7474
- **Neo4j Credentials**: `neo4j` / `<NEO4J_PASSWORD dal file .env>`

## 📋 Comandi Utili

### Makefile Commands

```bash
make help          # Mostra tutti i comandi disponibili
make build         # Build delle immagini Docker
make up            # Avvia servizi (development)
make up-prod       # Avvia servizi (production)
make down          # Ferma tutti i servizi
make logs          # Mostra logs di tutti i servizi
make logs-graph    # Mostra logs di Graphiti
make logs-neo4j    # Mostra logs di Neo4j
make shell         # Apre shell nel container Graphiti
make neo4j-shell   # Apre Neo4j cypher shell
make restart       # Riavvia tutti i servizi
make status        # Mostra status dei servizi
make health        # Controlla salute dei servizi
make clean         # Rimuove tutti i container e volumi
```

### Docker Compose Commands

```bash
# Development
docker-compose up -d

# Production
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Logs
docker-compose logs -f

# Stop
docker-compose down

# Rebuild
docker-compose build --no-cache
```

## 🔧 Configurazione

### Environment Variables (.env)

```bash
# OpenAI Configuration (Required)
OPENAI_API_KEY=sk-your-openai-api-key-here

# Neo4j Database Configuration
NEO4J_URI=bolt://neo4j:7687
NEO4J_PORT=7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=secure_password_here

# Optional: Anthropic Configuration
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Performance Configuration
USE_PARALLEL_RUNTIME=true
SEMAPHORE_LIMIT=10
MAX_REFLEXION_ITERATIONS=3
```

### Configurazioni Disponibili

- **Development**: `docker-compose.yml` + `docker-compose.override.yml`
- **Production**: `docker-compose.yml` + `docker-compose.prod.yml`

## 🏗️ Architettura

```
┌─────────────────┐    ┌─────────────────┐
│   Graphiti      │    │     Neo4j       │
│   Container     │◄──►│   Container     │
│   Port: 8000    │    │   Port: 7474    │
└─────────────────┘    └─────────────────┘
         │                       │
         ▼                       ▼
┌─────────────────┐    ┌─────────────────┐
│   Graphiti      │    │   Neo4j Data    │
│   API Service   │    │   Volume        │
└─────────────────┘    └─────────────────┘
```

## 🔍 Health Checks

### Automatic Health Checks

- **Graphiti**: `/healthcheck` endpoint
- **Neo4j**: HTTP check su porta 7474
- **Dependencies**: Service dependencies con health conditions

### Manual Health Check

```bash
# Controllo completo
./scripts/health-check.sh

# Controllo singoli servizi
curl http://localhost:8000/healthcheck
curl http://localhost:7474
```

## 🛠️ Troubleshooting

### Problemi Comuni

1. **Port già in uso:**
```bash
# Cambia le porte nel docker-compose.yml
ports:
  - "8001:8000"  # Graphiti
  - "7475:7474"  # Neo4j
```

2. **API Key non configurata:**
```bash
# Modifica il file .env
OPENAI_API_KEY=your_actual_api_key_here
```

3. **Neo4j non si avvia:**
```bash
# Controlla i logs
make logs-neo4j

# Ricrea i volumi
make clean
make up
```

4. **Memoria insufficiente:**
```bash
# Aumenta la memoria Docker (Docker Desktop Settings)
# oppure usa la configurazione production
make up-prod
```

### Logs e Debug

```bash
# Logs di tutti i servizi
make logs

# Logs specifici
docker-compose logs -f graph
docker-compose logs -f neo4j

# Debug mode
export LOG_LEVEL=DEBUG
docker-compose up
```

## 📊 Monitoring

### Metriche Disponibili

- **Graphiti API**: Health endpoint, response times
- **Neo4j**: Browser interface, cypher queries
- **Docker**: Container stats, resource usage

### Monitoring Commands

```bash
# Status containers
docker-compose ps

# Resource usage
docker stats

# Neo4j database info
make neo4j-shell
# Poi esegui: CALL dbms.components() YIELD name, versions, edition
```

## 🔒 Security

### Configurazioni di Sicurezza

- **Non-root user**: I container girano come utente non-root
- **Secrets management**: API keys tramite environment variables
- **Network isolation**: Container comunicano solo tramite rete Docker
- **Volume persistence**: Dati Neo4j persistenti ma isolati

### Best Practices

1. **Non committare** il file `.env` con API keys reali
2. **Usa password forti** per Neo4j
3. **Aggiorna regolarmente** le immagini Docker
4. **Monitora** i logs per attività sospette

## 📚 Esempi di Utilizzo

### Test dell'Installazione

```bash
# Test API Graphiti
curl -X POST http://localhost:8000/api/v1/graph/add_episode \
  -H "Content-Type: application/json" \
  -d '{"episode": "Test episode for Graphiti"}'

# Test Neo4j
make neo4j-shell
# Esegui: MATCH (n) RETURN count(n) as node_count;
```

### Esempi Python

```python
from graphiti_core import Graphiti

# Connessione al Neo4j dockerizzato
graphiti = Graphiti(
    "bolt://localhost:7687",
    "neo4j",
    "your_neo4j_password",
    # ... altre configurazioni
)

# Aggiungi un episodio
result = graphiti.add_episode("Esempio di episodio per test")
print(result)
```

## 🤝 Supporto

- **Documentazione**: https://help.getzep.com/graphiti
- **GitHub Issues**: https://github.com/getzep/graphiti/issues
- **Discord**: Zep Discord server - #Graphiti channel

## 📄 Licenza

Apache-2.0 License - vedi [LICENSE](LICENSE) per dettagli.

---

**Nota**: Questa installazione dockerizzata è ottimizzata per sviluppo e testing. Per produzione, considera configurazioni aggiuntive di sicurezza e monitoring.

