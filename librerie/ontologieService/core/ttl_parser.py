"""
Generic TTL/RDF parser for ontology files.
"""

from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

try:
    from rdflib import Graph as RDFGraph, Namespace, URIRef, Literal
    from rdflib.namespace import RDF, RDFS, OWL, DCTERMS, XSD
    RDFLIB_AVAILABLE = True
except ImportError:
    RDFLIB_AVAILABLE = False
    RDFGraph = None
    RDF = None
    RDFS = None
    OWL = None
    DCTERMS = None
    XSD = None

logger = logging.getLogger(__name__)


class TTLParser:
    """
    Generic parser for TTL/RDF ontology files.
    
    Extracts structured data from RDF/Turtle files for import into knowledge graphs.
    Supports full ontology parsing with classes, properties, individuals, and relationships.
    """
    
    def __init__(self, ttl_file_path: str):
        self.ttl_file_path = Path(ttl_file_path)
        self.rdf_graph: Optional[RDFGraph] = None
        self.namespace_map: Dict[str, str] = {}
        
    def parse(self) -> Dict[str, Any]:
        """
        Parse TTL file and extract all ontology components.
        
        Returns:
            Dictionary with extracted ontology data:
            - metadata: Ontology metadata (title, description, version, etc.)
            - classes: OWL classes with hierarchy
            - properties: Object and datatype properties
            - individuals: Instances/individuals
            - relationships: All relationships between entities
            - statistics: Parsing statistics
        """
        if not RDFLIB_AVAILABLE:
            return {"error": "rdflib not available for RDF parsing"}
            
        if not self.ttl_file_path.exists():
            return {"error": f"TTL file not found: {self.ttl_file_path}"}
            
        try:
            self.rdf_graph = RDFGraph()
            logger.info(f"Parsing TTL file: {self.ttl_file_path}")
            self.rdf_graph.parse(str(self.ttl_file_path), format="turtle")
            
            # Build namespace mapping
            self._build_namespace_map()
            
            # Extract all components
            parsed_data = {
                "metadata": self._extract_metadata(),
                "classes": self._extract_classes(),
                "properties": self._extract_properties(),
                "individuals": self._extract_individuals(),
                "relationships": self._extract_relationships(),
                "statistics": self._get_statistics(),
                "namespaces": self.namespace_map
            }
            
            logger.info(f"Successfully parsed {len(self.rdf_graph)} triples")
            return parsed_data
            
        except Exception as e:
            logger.error(f"Failed to parse TTL file: {e}")
            return {"error": f"Parsing failed: {str(e)}"}
    
    def _build_namespace_map(self) -> None:
        """Build mapping of namespace prefixes to URIs"""
        if not self.rdf_graph:
            return
            
        for prefix, namespace in self.rdf_graph.namespaces():
            self.namespace_map[str(prefix)] = str(namespace)
    
    def _extract_metadata(self) -> Dict[str, Any]:
        """Extract ontology metadata from owl:Ontology declarations"""
        metadata = {}
        
        for s, p, o in self.rdf_graph.triples((None, RDF.type, OWL.Ontology)):
            metadata.update({
                "uri": str(s),
                "title": self._get_literal_value(s, DCTERMS.title),
                "description": self._get_literal_value(s, DCTERMS.description),
                "version": self._get_literal_value(s, OWL.versionInfo),
                "creator": self._get_literal_value(s, DCTERMS.creator),
                "created": self._get_literal_value(s, DCTERMS.created),
                "modified": self._get_literal_value(s, DCTERMS.modified),
                "imports": [str(obj) for subj, pred, obj in 
                           self.rdf_graph.triples((s, OWL.imports, None))]
            })
            break
            
        return metadata
    
    def _extract_classes(self) -> List[Dict[str, Any]]:
        """Extract all OWL classes with their properties and hierarchy"""
        classes = []
        
        for s, p, o in self.rdf_graph.triples((None, RDF.type, OWL.Class)):
            class_data = {
                "uri": str(s),
                "local_name": self._get_local_name(s),
                "prefixed_name": self._get_prefixed_name(s),
                "label": self._get_literal_value(s, RDFS.label),
                "comment": self._get_literal_value(s, RDFS.comment),
                "description": self._get_literal_value(s, DCTERMS.description),
                "subclass_of": [str(obj) for subj, pred, obj in 
                               self.rdf_graph.triples((s, RDFS.subClassOf, None))],
                "superclass_of": [str(subj) for subj, pred, obj in 
                                 self.rdf_graph.triples((None, RDFS.subClassOf, s))],
                "equivalent_class": [str(obj) for subj, pred, obj in 
                                   self.rdf_graph.triples((s, OWL.equivalentClass, None))],
                "disjoint_with": [str(obj) for subj, pred, obj in 
                                self.rdf_graph.triples((s, OWL.disjointWith, None))]
            }
            classes.append(class_data)
            
        return classes
    
    def _extract_properties(self) -> List[Dict[str, Any]]:
        """Extract all OWL properties (Object and Datatype)"""
        properties = []
        
        # Object Properties
        for s, p, o in self.rdf_graph.triples((None, RDF.type, OWL.ObjectProperty)):
            prop_data = self._build_property_data(s, "ObjectProperty")
            properties.append(prop_data)
            
        # Datatype Properties
        for s, p, o in self.rdf_graph.triples((None, RDF.type, OWL.DatatypeProperty)):
            prop_data = self._build_property_data(s, "DatatypeProperty")
            properties.append(prop_data)
            
        # Annotation Properties
        for s, p, o in self.rdf_graph.triples((None, RDF.type, OWL.AnnotationProperty)):
            prop_data = self._build_property_data(s, "AnnotationProperty")
            properties.append(prop_data)
            
        return properties
    
    def _build_property_data(self, prop_uri: URIRef, prop_type: str) -> Dict[str, Any]:
        """Build property data structure"""
        return {
            "uri": str(prop_uri),
            "local_name": self._get_local_name(prop_uri),
            "prefixed_name": self._get_prefixed_name(prop_uri),
            "type": prop_type,
            "label": self._get_literal_value(prop_uri, RDFS.label),
            "comment": self._get_literal_value(prop_uri, RDFS.comment),
            "description": self._get_literal_value(prop_uri, DCTERMS.description),
            "domain": [str(obj) for subj, pred, obj in 
                      self.rdf_graph.triples((prop_uri, RDFS.domain, None))],
            "range": [str(obj) for subj, pred, obj in 
                     self.rdf_graph.triples((prop_uri, RDFS.range, None))],
            "subproperty_of": [str(obj) for subj, pred, obj in 
                             self.rdf_graph.triples((prop_uri, RDFS.subPropertyOf, None))],
            "inverse_of": [str(obj) for subj, pred, obj in 
                          self.rdf_graph.triples((prop_uri, OWL.inverseOf, None))],
            "functional": bool(list(self.rdf_graph.triples((prop_uri, RDF.type, OWL.FunctionalProperty)))),
            "inverse_functional": bool(list(self.rdf_graph.triples((prop_uri, RDF.type, OWL.InverseFunctionalProperty)))),
            "transitive": bool(list(self.rdf_graph.triples((prop_uri, RDF.type, OWL.TransitiveProperty)))),
            "symmetric": bool(list(self.rdf_graph.triples((prop_uri, RDF.type, OWL.SymmetricProperty)))),
            "asymmetric": bool(list(self.rdf_graph.triples((prop_uri, RDF.type, OWL.AsymmetricProperty)))),
            "reflexive": bool(list(self.rdf_graph.triples((prop_uri, RDF.type, OWL.ReflexiveProperty)))),
            "irreflexive": bool(list(self.rdf_graph.triples((prop_uri, RDF.type, OWL.IrreflexiveProperty))))
        }
    
    def _extract_individuals(self) -> List[Dict[str, Any]]:
        """Extract all individuals/instances"""
        individuals = []
        
        # Get all classes to find their instances
        classes = set()
        for s, p, o in self.rdf_graph.triples((None, RDF.type, OWL.Class)):
            classes.add(s)
            
        # Find instances of each class
        for class_uri in classes:
            for s, p, o in self.rdf_graph.triples((None, RDF.type, class_uri)):
                individual_data = {
                    "uri": str(s),
                    "local_name": self._get_local_name(s),
                    "prefixed_name": self._get_prefixed_name(s),
                    "type": str(class_uri),
                    "type_local_name": self._get_local_name(class_uri),
                    "label": self._get_literal_value(s, RDFS.label),
                    "comment": self._get_literal_value(s, RDFS.comment),
                    "properties": self._get_individual_properties(s),
                    "same_as": [str(obj) for subj, pred, obj in 
                              self.rdf_graph.triples((s, OWL.sameAs, None))],
                    "different_from": [str(obj) for subj, pred, obj in 
                                     self.rdf_graph.triples((s, OWL.differentFrom, None))]
                }
                individuals.append(individual_data)
                
        return individuals
    
    def _extract_relationships(self) -> List[Dict[str, Any]]:
        """Extract all relationships/triples between entities"""
        relationships = []
        
        # Get all object properties
        object_props = set()
        for s, p, o in self.rdf_graph.triples((None, RDF.type, OWL.ObjectProperty)):
            object_props.add(s)
            
        # Extract relationships using object properties
        for prop_uri in object_props:
            for s, p, o in self.rdf_graph.triples((None, prop_uri, None)):
                rel_data = {
                    "subject": str(s),
                    "predicate": str(p),
                    "object": str(o),
                    "subject_local_name": self._get_local_name(s),
                    "predicate_local_name": self._get_local_name(p),
                    "object_local_name": self._get_local_name(o),
                    "subject_prefixed": self._get_prefixed_name(s),
                    "predicate_prefixed": self._get_prefixed_name(p),
                    "object_prefixed": self._get_prefixed_name(o)
                }
                relationships.append(rel_data)
                
        return relationships
    
    def _get_individual_properties(self, individual_uri: URIRef) -> Dict[str, Any]:
        """Get all properties and their values for an individual"""
        properties = {}
        
        for s, p, o in self.rdf_graph.triples((individual_uri, None, None)):
            prop_name = self._get_local_name(p)
            
            # Skip RDF system properties
            if prop_name in ['type']:
                continue
                
            value = str(o)
            if isinstance(o, Literal):
                value = str(o)
            elif isinstance(o, URIRef):
                value = {
                    "uri": str(o),
                    "local_name": self._get_local_name(o),
                    "prefixed_name": self._get_prefixed_name(o)
                }
                
            if prop_name in properties:
                # Multiple values - convert to list
                if not isinstance(properties[prop_name], list):
                    properties[prop_name] = [properties[prop_name]]
                properties[prop_name].append(value)
            else:
                properties[prop_name] = value
                
        return properties
    
    def _get_statistics(self) -> Dict[str, int]:
        """Get comprehensive parsing statistics"""
        if not self.rdf_graph:
            return {}
            
        return {
            "total_triples": len(self.rdf_graph),
            "classes": len(list(self.rdf_graph.triples((None, RDF.type, OWL.Class)))),
            "object_properties": len(list(self.rdf_graph.triples((None, RDF.type, OWL.ObjectProperty)))),
            "datatype_properties": len(list(self.rdf_graph.triples((None, RDF.type, OWL.DatatypeProperty)))),
            "annotation_properties": len(list(self.rdf_graph.triples((None, RDF.type, OWL.AnnotationProperty)))),
            "individuals": len(set(str(s) for s, p, o in self.rdf_graph.triples((None, RDF.type, None)) 
                                 if not self._is_system_type(o))),
            "namespaces": len(self.namespace_map),
            "relationships": len(set((str(s), str(p), str(o)) 
                                   for s, p, o in self.rdf_graph.triples((None, None, None))
                                   if self._is_object_property(p)))
        }
    
    def _is_system_type(self, type_uri: URIRef) -> bool:
        """Check if a type is a system/OWL type"""
        system_types = {OWL.Class, OWL.ObjectProperty, OWL.DatatypeProperty, 
                       OWL.AnnotationProperty, OWL.Ontology}
        return type_uri in system_types
    
    def _is_object_property(self, prop_uri: URIRef) -> bool:
        """Check if a property is an object property"""
        return bool(list(self.rdf_graph.triples((prop_uri, RDF.type, OWL.ObjectProperty))))
    
    def _get_literal_value(self, subject: URIRef, predicate: URIRef, default: str = "") -> str:
        """Extract literal value from RDF graph"""
        try:
            for s, p, o in self.rdf_graph.triples((subject, predicate, None)):
                return str(o)
        except Exception:
            pass
        return default
    
    def _get_local_name(self, uri: URIRef) -> str:
        """Extract local name from URI"""
        uri_str = str(uri)
        if '#' in uri_str:
            return uri_str.split('#')[-1]
        elif '/' in uri_str:
            return uri_str.split('/')[-1]
        return uri_str
    
    def _get_prefixed_name(self, uri: URIRef) -> str:
        """Get prefixed name using namespace mapping"""
        uri_str = str(uri)
        
        # Find matching namespace
        for prefix, namespace_uri in self.namespace_map.items():
            if uri_str.startswith(namespace_uri):
                local_part = uri_str[len(namespace_uri):]
                return f"{prefix}:{local_part}" if prefix else local_part
                
        # Fallback to local name
        return self._get_local_name(uri)
