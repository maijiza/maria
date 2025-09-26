"""
Framework-specific analyzers for ontologies.
"""

from .cobit5_analyzer import COBIT5Analyzer
from .iso17025_analyzer import ISO17025Analyzer

__all__ = [
    'COBIT5Analyzer',
    'ISO17025Analyzer'
]
