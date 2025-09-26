"""
ISO17025-specific analyzer for laboratory ontology processing.
"""

from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)


class ISO17025Analyzer:
    """
    Specialized analyzer for ISO17025 laboratory ontology.
    
    Provides enhanced classification and processing for ISO17025 entities
    based on laboratory testing and calibration requirements.
    """
    
    def __init__(self):
        # ISO17025 clause mapping
        self.iso17025_clauses = {
            "4": {"name": "General requirements", "type": "Management System"},
            "5": {"name": "Structural requirements", "type": "Organization"},
            "6": {"name": "Resource requirements", "type": "Resources"},
            "7": {"name": "Process requirements", "type": "Processes"},
            "8": {"name": "Management system requirements", "type": "System"}
        }
        
        # Laboratory-specific business entities
        self.laboratory_business_entities = {
            'Laboratory', 'TestMethod', 'CalibrationMethod', 'Sample', 'Specimen',
            'TestResult', 'CalibrationResult', 'Certificate', 'Report',
            'Equipment', 'Instrument', 'Standard', 'ReferenceStandard',
            'Uncertainty', 'Traceability', 'Accreditation', 'Competence',
            'QualityControl', 'QualityAssurance', 'Validation', 'Verification',
            'NonConformity', 'CorrectiveAction', 'PreventiveAction',
            'CustomerComplaint', 'InternalAudit', 'ManagementReview'
        }
        
        # Technical laboratory entities
        self.laboratory_technical_entities = {
            'MeasurementProcedure', 'TestProcedure', 'CalibrationProcedure',
            'SamplingProcedure', 'DataProcessing', 'StatisticalAnalysis',
            'UncertaintyCalculation', 'TraceabilityChain', 'MeasurementModel',
            'EnvironmentalCondition', 'SafetyRequirement', 'TechnicalRecord'
        }
        
        # Core laboratory concepts
        self.laboratory_core_entities = {
            'Person', 'Staff', 'TechnicalPersonnel', 'Customer', 'Client',
            'Supplier', 'AccreditationBody', 'RegulatoryAuthority',
            'Document', 'Record', 'Procedure', 'Policy', 'Manual',
            'Location', 'Facility', 'Environment', 'Time', 'Date'
        }
    
    def enhance_classification(self, classified_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhance layer classification with ISO17025-specific logic.
        
        Args:
            classified_data: Data from LayerClassifier
            
        Returns:
            Enhanced classification with ISO17025 laboratory knowledge
        """
        enhanced_data = classified_data.copy()
        
        # Enhance classes
        if "classes" in enhanced_data:
            enhanced_data["classes"] = self._enhance_class_classification(
                enhanced_data["classes"]
            )
            
        # Enhance properties
        if "properties" in enhanced_data:
            enhanced_data["properties"] = self._enhance_property_classification(
                enhanced_data["properties"]
            )
            
        # Enhance individuals
        if "individuals" in enhanced_data:
            enhanced_data["individuals"] = self._enhance_individual_classification(
                enhanced_data["individuals"]
            )
            
        # Add ISO17025-specific analysis
        enhanced_data["iso17025_analysis"] = self._generate_iso17025_analysis(enhanced_data)
        
        return enhanced_data
    
    def _enhance_class_classification(self, classes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Enhance classification for ISO17025 classes"""
        enhanced_classes = []
        
        for cls in classes:
            enhanced_cls = cls.copy()
            local_name = cls.get("local_name", "")
            
            # ISO17025-specific layer logic
            iso_layers = self._classify_iso17025_entity(local_name, "class")
            
            # Merge with existing layers
            existing_layers = set(cls.get("layers", []))
            enhanced_layers = existing_layers.union(iso_layers)
            
            enhanced_cls["layers"] = sorted(list(enhanced_layers))
            enhanced_cls["primary_layer"] = self._get_iso17025_primary_layer(enhanced_layers)
            enhanced_cls["iso17025_clause"] = self._get_iso17025_clause(local_name)
            enhanced_cls["laboratory_relevance"] = self._get_laboratory_relevance(local_name)
            
            enhanced_classes.append(enhanced_cls)
            
        return enhanced_classes
    
    def _enhance_property_classification(self, properties: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Enhance classification for ISO17025 properties"""
        enhanced_properties = []
        
        for prop in properties:
            enhanced_prop = prop.copy()
            local_name = prop.get("local_name", "")
            
            # ISO17025-specific property analysis
            iso_layers = self._classify_iso17025_entity(local_name, "property")
            
            # Check for measurement/calibration properties
            if self._is_measurement_property(prop):
                iso_layers.add("business")
                
            # Merge layers
            existing_layers = set(prop.get("layers", []))
            enhanced_layers = existing_layers.union(iso_layers)
            
            enhanced_prop["layers"] = sorted(list(enhanced_layers))
            enhanced_prop["primary_layer"] = self._get_iso17025_primary_layer(enhanced_layers)
            enhanced_prop["measurement_relevance"] = self._assess_measurement_relevance(prop)
            
            enhanced_properties.append(enhanced_prop)
            
        return enhanced_properties
    
    def _enhance_individual_classification(self, individuals: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Enhance classification for ISO17025 individuals"""
        enhanced_individuals = []
        
        for individual in individuals:
            enhanced_individual = individual.copy()
            local_name = individual.get("local_name", "")
            type_name = individual.get("type_local_name", "")
            
            # ISO17025-specific individual analysis
            iso_layers = self._classify_iso17025_entity(local_name, "individual")
            
            # Check type for laboratory relevance
            if type_name in self.laboratory_business_entities:
                iso_layers.add("business")
            elif type_name in self.laboratory_core_entities:
                iso_layers.add("core")
                
            # Merge layers
            existing_layers = set(individual.get("layers", []))
            enhanced_layers = existing_layers.union(iso_layers)
            
            enhanced_individual["layers"] = sorted(list(enhanced_layers))
            enhanced_individual["primary_layer"] = self._get_iso17025_primary_layer(enhanced_layers)
            enhanced_individual["laboratory_function"] = self._get_laboratory_function(individual)
            
            enhanced_individuals.append(enhanced_individual)
            
        return enhanced_individuals
    
    def _classify_iso17025_entity(self, entity_name: str, entity_type: str) -> set:
        """Classify entity using ISO17025-specific rules"""
        layers = set()
        entity_lower = entity_name.lower()
        
        # Check for laboratory business entities
        if any(lbe.lower() in entity_lower for lbe in self.laboratory_business_entities):
            layers.add("business")
            
        # Check for laboratory technical entities
        if any(lte.lower() in entity_lower for lte in self.laboratory_technical_entities):
            layers.add("technical")
            
        # Check for laboratory core entities
        if any(lce.lower() in entity_lower for lce in self.laboratory_core_entities):
            layers.add("core")
            
        return layers
    
    def _is_measurement_property(self, property_data: Dict[str, Any]) -> bool:
        """Check if property is related to measurement/calibration"""
        prop_name = property_data.get("local_name", "").lower()
        measurement_terms = ['measure', 'calibrat', 'uncertain', 'trace', 'accura', 'precis']
        
        return any(term in prop_name for term in measurement_terms)
    
    def _get_iso17025_primary_layer(self, layers: set) -> str:
        """Determine primary layer with ISO17025-specific priority"""
        if "business" in layers:
            return "business"
        elif "core" in layers:
            return "core"
        else:
            return "technical"
    
    def _get_iso17025_clause(self, entity_name: str) -> Optional[str]:
        """Map entity to ISO17025 clause"""
        entity_lower = entity_name.lower()
        
        # Mapping based on entity characteristics
        clause_mapping = {
            "4": ["management", "system", "policy", "organization"],
            "5": ["structure", "personnel", "responsibility", "authority"],
            "6": ["resource", "equipment", "facility", "environment", "competence"],
            "7": ["process", "method", "procedure", "sample", "test", "calibration"],
            "8": ["record", "document", "review", "audit", "improvement"]
        }
        
        for clause, keywords in clause_mapping.items():
            if any(keyword in entity_lower for keyword in keywords):
                return clause
                
        return None
    
    def _get_laboratory_relevance(self, entity_name: str) -> str:
        """Assess laboratory relevance level"""
        entity_lower = entity_name.lower()
        
        high_relevance = ['test', 'calibration', 'measurement', 'sample', 'result', 'uncertainty']
        medium_relevance = ['equipment', 'method', 'procedure', 'standard', 'quality']
        
        if any(hr in entity_lower for hr in high_relevance):
            return "high"
        elif any(mr in entity_lower for mr in medium_relevance):
            return "medium"
        else:
            return "low"
    
    def _assess_measurement_relevance(self, property_data: Dict[str, Any]) -> str:
        """Assess measurement relevance of a property"""
        prop_name = property_data.get("local_name", "").lower()
        
        measurement_terms = ['measure', 'calibrat', 'uncertain', 'trace', 'accura']
        
        if any(term in prop_name for term in measurement_terms):
            return "high"
        elif "has" in prop_name and any(term in prop_name for term in ['value', 'result', 'data']):
            return "medium"
        else:
            return "low"
    
    def _get_laboratory_function(self, individual_data: Dict[str, Any]) -> str:
        """Determine laboratory function of an individual"""
        name = individual_data.get("local_name", "").lower()
        type_name = individual_data.get("type_local_name", "").lower()
        
        functions = {
            "testing": ["test", "analysis", "examination"],
            "calibration": ["calibrat", "standard", "reference"],
            "sampling": ["sample", "specimen", "collection"],
            "quality": ["quality", "control", "assurance"],
            "management": ["management", "administration", "governance"],
            "technical": ["technical", "method", "procedure"]
        }
        
        for function, keywords in functions.items():
            if any(keyword in name or keyword in type_name for keyword in keywords):
                return function
                
        return "general"
    
    def _generate_iso17025_analysis(self, enhanced_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate ISO17025-specific analysis"""
        analysis = {
            "clauses_covered": [],
            "laboratory_coverage": {},
            "measurement_capabilities": {},
            "compliance_readiness": "unknown"
        }
        
        # Analyze clauses covered
        clause_coverage = set()
        for category in ["classes", "properties", "individuals"]:
            if category in enhanced_data:
                for entity in enhanced_data[category]:
                    clause = entity.get("iso17025_clause")
                    if clause:
                        clause_coverage.add(clause)
                        
        analysis["clauses_covered"] = sorted(list(clause_coverage))
        
        # Calculate laboratory coverage
        total_clauses = len(self.iso17025_clauses)
        covered_clauses = len(clause_coverage)
        analysis["laboratory_coverage"] = {
            "clauses_covered": covered_clauses,
            "total_clauses": total_clauses,
            "coverage_percentage": (covered_clauses / total_clauses * 100) if total_clauses > 0 else 0
        }
        
        # Assess compliance readiness
        if covered_clauses >= 4:
            analysis["compliance_readiness"] = "high"
        elif covered_clauses >= 2:
            analysis["compliance_readiness"] = "medium"
        else:
            analysis["compliance_readiness"] = "low"
            
        return analysis
