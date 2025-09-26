"""
OntologieService - Libreria dedicata per gestione ontologie TTL/RDF

Questa libreria fornisce:
- Parsing generico di file TTL/RDF
- Classificazione automatica di nodi in layer (business/technical)
- Import strutturato in knowledge graph con labels
- Supporto specifico per ontologie COBIT5, ISO17025, BFO, etc.

Utilizzo:
    from ontologieService import TTLParser, LayerClassifier, OntologyImporter
"""

from .core.ttl_parser import TTLParser
from .core.layer_classifier import LayerClassifier
from .core.ontology_importer import OntologyImporter
from .frameworks.cobit5_analyzer import COBIT5Analyzer
from .frameworks.iso17025_analyzer import ISO17025Analyzer

__version__ = "1.0.0"
__author__ = "waDoker LIMS Team"

__all__ = [
    'TTLParser',
    'LayerClassifier', 
    'OntologyImporter',
    'COBIT5Analyzer',
    'ISO17025Analyzer'
]
