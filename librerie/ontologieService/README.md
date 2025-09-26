# OntologieService

Libreria dedicata per la gestione di ontologie TTL/RDF nel sistema waDoker LIMS.

## Funzionalità

- **TTL Parser**: Parsing generico di file Turtle/RDF
- **Layer Classifier**: Classificazione automatica nodi in layer business/technical
- **Ontology Importer**: Import strutturato in knowledge graph con labels
- **Framework Support**: Supporto specifico per COBIT5, ISO17025, BFO, etc.

## Architettura

```
ontologieService/
├── core/                    # Componenti core
│   ├── ttl_parser.py       # Parser TTL generico
│   ├── layer_classifier.py # Classificazione layer
│   └── ontology_importer.py # Import con layer labels
├── frameworks/              # Supporto framework specifici
│   ├── cobit5_analyzer.py  # Analisi COBIT5
│   └── iso17025_analyzer.py # Analisi ISO17025
└── utils/                   # Utilities
    └── rdf_helpers.py      # Helper RDF
```

## Utilizzo

```python
from librerie.ontologieService import TTLParser, LayerClassifier, OntologyImporter

# Parse TTL file
parser = TTLParser("path/to/ontology.ttl")
ontology_data = parser.parse()

# Classify nodes into layers
classifier = LayerClassifier()
classified_data = classifier.classify(ontology_data)

# Import into knowledge graph
importer = OntologyImporter(graphiti_client)
result = await importer.import_with_layers(classified_data, group_id="my_ontology")
```

## Integrazione

La libreria è progettata per essere importata in:
- **graphiti_core**: Per funzionalità core
- **mcp_server**: Per esposizione API MCP
- Altri progetti che necessitano gestione ontologie
