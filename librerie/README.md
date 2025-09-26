# Librerie waGraphiti

Questa cartella contiene tutte le librerie personalizzate sviluppate per il sistema waGraphiti e waDoker LIMS.

## Struttura

```
librerie/
├── ontologieService/          # Gestione ontologie TTL/RDF
│   ├── core/                 # Componenti core (parser, classifier, importer)
│   └── frameworks/           # Supporto framework specifici (COBIT5, ISO17025)
├── [future_library]/         # Altre librerie future
└── README.md                 # Questo file
```

## Librerie Disponibili

### 🔧 OntologieService v1.0.0
**Scopo**: Gestione completa di ontologie TTL/RDF per knowledge graph

**Funzionalità**:
- Parsing generico file Turtle/RDF
- Classificazione automatica nodi in layer (business/technical/core)
- Import strutturato in Graphiti con layer labels
- Supporto specifico per framework COBIT5, ISO17025, BFO

**Utilizzo**:
```python
from librerie.ontologieService import TTLParser, LayerClassifier, OntologyImporter
```

## Integrazione

Le librerie sono progettate per essere importate in:
- **graphiti_core**: Funzionalità core del knowledge graph
- **mcp_server**: Esposizione API MCP
- **server**: API REST
- Altri componenti del sistema

## Sviluppo

Ogni libreria mantiene:
- Struttura modulare indipendente
- Documentazione completa
- Test suite dedicata
- Configurazione pyproject.toml
- Versioning semantico
