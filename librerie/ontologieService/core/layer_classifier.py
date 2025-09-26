"""
Layer classifier for ontology nodes.

Classifies ontology entities into different layers (business, technical, core)
based on their characteristics, names, and relationships.
"""

from typing import Dict, List, Any, Set
import re
import logging

logger = logging.getLogger(__name__)


class LayerClassifier:
    """
    Classifies ontology nodes into different layers for targeted search.
    
    Layers:
    - business: User-facing, domain-specific concepts
    - technical: Implementation details, OWL constructs
    - core: Essential concepts needed by both layers
    """
    
    def __init__(self):
        # Business layer keywords
        self.business_keywords = {
            'domain', 'process', 'goal', 'objective', 'enabler', 'control',
            'governance', 'management', 'audit', 'compliance', 'risk',
            'stakeholder', 'framework', 'practice', 'activity', 'outcome',
            'metric', 'kpi', 'performance', 'maturity', 'capability',
            'service', 'resource', 'asset', 'value', 'benefit',
            'requirement', 'standard', 'policy', 'procedure', 'guideline',
            'laboratory', 'test', 'sample', 'analysis', 'result',
            'calibration', 'measurement', 'uncertainty', 'traceability',
            'quality', 'assurance', 'accreditation', 'certification'
        }
        
        # Technical layer keywords
        self.technical_keywords = {
            'property', 'class', 'individual', 'restriction', 'constraint',
            'axiom', 'assertion', 'inference', 'reasoning', 'ontology',
            'namespace', 'prefix', 'uri', 'iri', 'rdf', 'owl', 'rdfs',
            'domain', 'range', 'inverse', 'functional', 'transitive',
            'symmetric', 'reflexive', 'irreflexive', 'asymmetric',
            'equivalent', 'disjoint', 'complement', 'union', 'intersection',
            'cardinality', 'some', 'only', 'exactly', 'min', 'max',
            'annotation', 'comment', 'label', 'seealso', 'isdefinedby'
        }
        
        # Core concepts that both layers need
        self.core_keywords = {
            'organization', 'role', 'responsibility', 'person', 'user',
            'system', 'application', 'data', 'information', 'document',
            'time', 'date', 'period', 'duration', 'event', 'action',
            'status', 'state', 'type', 'category', 'classification'
        }
        
        # Patterns for technical constructs
        self.technical_patterns = [
            r'^has[A-Z]',  # hasProperty, hasDomain, etc.
            r'^is[A-Z]',   # isDefinedBy, isPartOf, etc.
            r'Property$',  # ObjectProperty, DatatypeProperty
            r'Class$',     # Various classes
            r'^owl:',      # OWL namespace
            r'^rdfs:',     # RDFS namespace
            r'^rdf:',      # RDF namespace
            r'Restriction$',
            r'Constraint$',
            r'Axiom$'
        ]
        
        # Patterns for business constructs
        self.business_patterns = [
            r'Goal$',
            r'Process$',
            r'Domain$',
            r'Enabler$',
            r'Control$',
            r'Framework$',
            r'Standard$',
            r'Requirement$',
            r'Practice$',
            r'Activity$',
            r'Outcome$',
            r'Metric$'
        ]
    
    def classify(self, ontology_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Classify all entities in ontology data into layers.
        
        Args:
            ontology_data: Parsed ontology data from TTLParser
            
        Returns:
            Ontology data with layer classifications added
        """
        if "error" in ontology_data:
            return ontology_data
            
        logger.info("Starting layer classification")
        
        # Classify each category
        classified_data = ontology_data.copy()
        
        if "classes" in ontology_data:
            classified_data["classes"] = self._classify_entities(
                ontology_data["classes"], "class"
            )
            
        if "properties" in ontology_data:
            classified_data["properties"] = self._classify_entities(
                ontology_data["properties"], "property"
            )
            
        if "individuals" in ontology_data:
            classified_data["individuals"] = self._classify_entities(
                ontology_data["individuals"], "individual"
            )
            
        # Add classification statistics
        classified_data["layer_statistics"] = self._get_layer_statistics(classified_data)
        
        logger.info(f"Classification completed: {classified_data['layer_statistics']}")
        return classified_data
    
    def _classify_entities(self, entities: List[Dict[str, Any]], entity_type: str) -> List[Dict[str, Any]]:
        """Classify a list of entities"""
        classified_entities = []
        
        for entity in entities:
            # Determine layer for this entity
            layers = self._determine_layers(entity, entity_type)
            
            # Add layer information to entity
            entity_with_layers = entity.copy()
            entity_with_layers["layers"] = layers
            entity_with_layers["primary_layer"] = self._get_primary_layer(layers)
            
            classified_entities.append(entity_with_layers)
            
        return classified_entities
    
    def _determine_layers(self, entity: Dict[str, Any], entity_type: str) -> List[str]:
        """Determine which layers an entity belongs to"""
        layers = set()
        
        # Get entity identifiers
        local_name = entity.get("local_name", "").lower()
        prefixed_name = entity.get("prefixed_name", "").lower()
        label = entity.get("label", "").lower()
        comment = entity.get("comment", "").lower()
        description = entity.get("description", "").lower()
        
        # All text to analyze
        text_content = f"{local_name} {prefixed_name} {label} {comment} {description}"
        
        # Check for technical indicators
        if self._is_technical_entity(entity, text_content):
            layers.add("technical")
            
        # Check for business indicators
        if self._is_business_entity(entity, text_content):
            layers.add("business")
            
        # Check for core indicators
        if self._is_core_entity(entity, text_content):
            layers.add("core")
            
        # Special handling by entity type
        if entity_type == "property":
            layers.update(self._classify_property(entity))
        elif entity_type == "class":
            layers.update(self._classify_class(entity))
        elif entity_type == "individual":
            layers.update(self._classify_individual(entity))
            
        # Default to technical if no classification found
        if not layers:
            layers.add("technical")
            
        return sorted(list(layers))
    
    def _is_technical_entity(self, entity: Dict[str, Any], text_content: str) -> bool:
        """Check if entity has technical characteristics"""
        
        # Check technical keywords
        for keyword in self.technical_keywords:
            if keyword in text_content:
                return True
                
        # Check technical patterns
        local_name = entity.get("local_name", "")
        for pattern in self.technical_patterns:
            if re.search(pattern, local_name):
                return True
                
        # Check if it's an OWL construct
        entity_type = entity.get("type", "")
        if "Property" in entity_type or entity_type in ["Class", "Restriction"]:
            return True
            
        # Check namespace
        prefixed_name = entity.get("prefixed_name", "")
        if any(prefixed_name.startswith(ns) for ns in ["owl:", "rdfs:", "rdf:", "xsd:"]):
            return True
            
        return False
    
    def _is_business_entity(self, entity: Dict[str, Any], text_content: str) -> bool:
        """Check if entity has business characteristics"""
        
        # Check business keywords
        for keyword in self.business_keywords:
            if keyword in text_content:
                return True
                
        # Check business patterns
        local_name = entity.get("local_name", "")
        for pattern in self.business_patterns:
            if re.search(pattern, local_name):
                return True
                
        # Check for domain-specific namespaces
        prefixed_name = entity.get("prefixed_name", "")
        business_namespaces = ["cobit5:", "iso17025:", "bfo:", "sosa:"]
        if any(prefixed_name.startswith(ns) for ns in business_namespaces):
            return True
            
        return False
    
    def _is_core_entity(self, entity: Dict[str, Any], text_content: str) -> bool:
        """Check if entity is a core concept"""
        
        # Check core keywords
        for keyword in self.core_keywords:
            if keyword in text_content:
                return True
                
        # Entities with many relationships are often core
        relationships_count = 0
        if "subclass_of" in entity:
            relationships_count += len(entity["subclass_of"])
        if "superclass_of" in entity:
            relationships_count += len(entity["superclass_of"])
        if "domain" in entity:
            relationships_count += len(entity["domain"])
        if "range" in entity:
            relationships_count += len(entity["range"])
            
        if relationships_count >= 3:
            return True
            
        return False
    
    def _classify_property(self, property_entity: Dict[str, Any]) -> Set[str]:
        """Special classification logic for properties"""
        layers = set()
        
        prop_type = property_entity.get("type", "")
        
        # Object properties connecting business entities are business
        if prop_type == "ObjectProperty":
            domain = property_entity.get("domain", [])
            range_vals = property_entity.get("range", [])
            
            # Check if domain/range contains business entities
            business_domains = ["Goal", "Process", "Domain", "Control", "Framework"]
            if any(any(bd in dr for bd in business_domains) for dr in domain + range_vals):
                layers.add("business")
                
        # Annotation properties are often technical
        elif prop_type == "AnnotationProperty":
            layers.add("technical")
            
        # Functional properties with specific characteristics
        if property_entity.get("functional") or property_entity.get("inverse_functional"):
            layers.add("technical")
            
        return layers
    
    def _classify_class(self, class_entity: Dict[str, Any]) -> Set[str]:
        """Special classification logic for classes"""
        layers = set()
        
        # Classes with many subclasses are often core
        superclass_count = len(class_entity.get("superclass_of", []))
        if superclass_count >= 3:
            layers.add("core")
            
        # Top-level classes in business ontologies
        subclass_of = class_entity.get("subclass_of", [])
        if not subclass_of:  # Root classes
            layers.add("core")
            
        return layers
    
    def _classify_individual(self, individual_entity: Dict[str, Any]) -> Set[str]:
        """Special classification logic for individuals"""
        layers = set()
        
        # Individuals of business classes are business
        individual_type = individual_entity.get("type_local_name", "").lower()
        business_types = ["goal", "process", "domain", "control", "enabler", "framework"]
        
        if any(bt in individual_type for bt in business_types):
            layers.add("business")
            
        return layers
    
    def _get_primary_layer(self, layers: List[str]) -> str:
        """Determine primary layer from list of layers"""
        if not layers:
            return "technical"
            
        # Priority order: business > core > technical
        if "business" in layers:
            return "business"
        elif "core" in layers:
            return "core"
        else:
            return "technical"
    
    def _get_layer_statistics(self, classified_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate statistics about layer classification"""
        stats = {
            "business": {"classes": 0, "properties": 0, "individuals": 0},
            "technical": {"classes": 0, "properties": 0, "individuals": 0},
            "core": {"classes": 0, "properties": 0, "individuals": 0},
            "multi_layer": {"classes": 0, "properties": 0, "individuals": 0}
        }
        
        for category in ["classes", "properties", "individuals"]:
            if category in classified_data:
                for entity in classified_data[category]:
                    layers = entity.get("layers", [])
                    primary = entity.get("primary_layer", "technical")
                    
                    # Count by primary layer
                    if primary in stats:
                        stats[primary][category] += 1
                        
                    # Count multi-layer entities
                    if len(layers) > 1:
                        stats["multi_layer"][category] += 1
        
        # Calculate totals
        for layer in stats:
            stats[layer]["total"] = sum(stats[layer].values())
            
        return stats
