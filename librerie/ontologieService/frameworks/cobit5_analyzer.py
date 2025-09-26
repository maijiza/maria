"""
COBIT5-specific analyzer for enhanced ontology processing.
"""

from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)


class COBIT5Analyzer:
    """
    Specialized analyzer for COBIT5 ontology with domain-specific logic.
    
    Provides enhanced classification and processing for COBIT5 entities
    based on the framework's structure and governance model.
    """
    
    def __init__(self):
        # COBIT5 domain mapping
        self.cobit5_domains = {
            "EDM": {"name": "Evaluate, Direct and Monitor", "type": "Governance", "level": 1},
            "APO": {"name": "Align, Plan and Organize", "type": "Management", "level": 2},
            "BAI": {"name": "Build, Acquire and Implement", "type": "Management", "level": 2},
            "DSS": {"name": "Deliver, Service and Support", "type": "Management", "level": 2},
            "MEA": {"name": "Monitor, Evaluate and Assess", "type": "Management", "level": 2}
        }
        
        # Business-critical COBIT5 entities
        self.business_entities = {
            'EnterpriseGoal', 'ITGoal', 'Goal', 'Process', 'Domain',
            'Enabler', 'Control', 'Framework', 'Practice', 'Activity',
            'Outcome', 'Metric', 'Stakeholder', 'Role', 'Responsibility',
            'RiskAssessment', 'ComplianceRequirement', 'AuditFinding'
        }
        
        # Technical-only COBIT5 entities
        self.technical_entities = {
            'ObjectProperty', 'DatatypeProperty', 'AnnotationProperty',
            'Restriction', 'Constraint', 'ValidationRule', 'InferenceRule'
        }
        
        # Core entities needed by both layers
        self.core_entities = {
            'Organization', 'Person', 'System', 'Application', 'Information',
            'Service', 'Resource', 'Asset', 'Time', 'Date', 'Status', 'Type'
        }
    
    def enhance_classification(self, classified_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhance layer classification with COBIT5-specific logic.
        
        Args:
            classified_data: Data from LayerClassifier
            
        Returns:
            Enhanced classification with COBIT5 domain knowledge
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
            
        # Add COBIT5-specific metadata
        enhanced_data["cobit5_analysis"] = self._generate_cobit5_analysis(enhanced_data)
        
        return enhanced_data
    
    def _enhance_class_classification(self, classes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Enhance classification for COBIT5 classes"""
        enhanced_classes = []
        
        for cls in classes:
            enhanced_cls = cls.copy()
            local_name = cls.get("local_name", "")
            
            # COBIT5-specific layer logic
            cobit5_layers = self._classify_cobit5_entity(local_name, "class")
            
            # Merge with existing layers
            existing_layers = set(cls.get("layers", []))
            enhanced_layers = existing_layers.union(cobit5_layers)
            
            enhanced_cls["layers"] = sorted(list(enhanced_layers))
            enhanced_cls["primary_layer"] = self._get_cobit5_primary_layer(enhanced_layers)
            enhanced_cls["cobit5_domain"] = self._get_cobit5_domain(local_name)
            enhanced_cls["business_relevance"] = self._get_business_relevance(local_name)
            
            enhanced_classes.append(enhanced_cls)
            
        return enhanced_classes
    
    def _enhance_property_classification(self, properties: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Enhance classification for COBIT5 properties"""
        enhanced_properties = []
        
        for prop in properties:
            enhanced_prop = prop.copy()
            local_name = prop.get("local_name", "")
            
            # COBIT5-specific property analysis
            cobit5_layers = self._classify_cobit5_entity(local_name, "property")
            
            # Check domain and range for business relevance
            domain = prop.get("domain", [])
            range_vals = prop.get("range", [])
            
            if self._has_business_domain_range(domain, range_vals):
                cobit5_layers.add("business")
                
            # Merge layers
            existing_layers = set(prop.get("layers", []))
            enhanced_layers = existing_layers.union(cobit5_layers)
            
            enhanced_prop["layers"] = sorted(list(enhanced_layers))
            enhanced_prop["primary_layer"] = self._get_cobit5_primary_layer(enhanced_layers)
            enhanced_prop["governance_relevance"] = self._assess_governance_relevance(prop)
            
            enhanced_properties.append(enhanced_prop)
            
        return enhanced_properties
    
    def _enhance_individual_classification(self, individuals: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Enhance classification for COBIT5 individuals"""
        enhanced_individuals = []
        
        for individual in individuals:
            enhanced_individual = individual.copy()
            local_name = individual.get("local_name", "")
            type_name = individual.get("type_local_name", "")
            
            # COBIT5-specific individual analysis
            cobit5_layers = self._classify_cobit5_entity(local_name, "individual")
            
            # Check type for business relevance
            if type_name in self.business_entities:
                cobit5_layers.add("business")
            elif type_name in self.core_entities:
                cobit5_layers.add("core")
                
            # Merge layers
            existing_layers = set(individual.get("layers", []))
            enhanced_layers = existing_layers.union(cobit5_layers)
            
            enhanced_individual["layers"] = sorted(list(enhanced_layers))
            enhanced_individual["primary_layer"] = self._get_cobit5_primary_layer(enhanced_layers)
            enhanced_individual["cobit5_process_code"] = self._extract_process_code(local_name)
            
            enhanced_individuals.append(enhanced_individual)
            
        return enhanced_individuals
    
    def _classify_cobit5_entity(self, entity_name: str, entity_type: str) -> set:
        """Classify entity using COBIT5-specific rules"""
        layers = set()
        entity_lower = entity_name.lower()
        
        # Check for COBIT5 domain codes
        for domain_code in self.cobit5_domains:
            if domain_code.lower() in entity_lower:
                layers.add("business")
                break
                
        # Check for business entity types
        if any(be.lower() in entity_lower for be in self.business_entities):
            layers.add("business")
            
        # Check for technical entity types
        if any(te.lower() in entity_lower for te in self.technical_entities):
            layers.add("technical")
            
        # Check for core entity types
        if any(ce.lower() in entity_lower for ce in self.core_entities):
            layers.add("core")
            
        return layers
    
    def _has_business_domain_range(self, domain: List[str], range_vals: List[str]) -> bool:
        """Check if property domain/range involves business entities"""
        all_refs = domain + range_vals
        
        for ref in all_refs:
            ref_lower = ref.lower()
            if any(be.lower() in ref_lower for be in self.business_entities):
                return True
                
        return False
    
    def _get_cobit5_primary_layer(self, layers: set) -> str:
        """Determine primary layer with COBIT5-specific priority"""
        if "business" in layers:
            return "business"
        elif "core" in layers:
            return "core"
        else:
            return "technical"
    
    def _get_cobit5_domain(self, entity_name: str) -> Optional[str]:
        """Extract COBIT5 domain from entity name"""
        entity_upper = entity_name.upper()
        
        for domain_code in self.cobit5_domains:
            if domain_code in entity_upper:
                return domain_code
                
        return None
    
    def _get_business_relevance(self, entity_name: str) -> str:
        """Assess business relevance level"""
        entity_lower = entity_name.lower()
        
        high_relevance = ['goal', 'process', 'domain', 'control', 'audit', 'compliance']
        medium_relevance = ['enabler', 'framework', 'practice', 'activity', 'metric']
        
        if any(hr in entity_lower for hr in high_relevance):
            return "high"
        elif any(mr in entity_lower for mr in medium_relevance):
            return "medium"
        else:
            return "low"
    
    def _assess_governance_relevance(self, property_data: Dict[str, Any]) -> str:
        """Assess governance relevance of a property"""
        prop_name = property_data.get("local_name", "").lower()
        
        governance_terms = ['governance', 'control', 'audit', 'compliance', 'risk', 'monitor']
        
        if any(gt in prop_name for gt in governance_terms):
            return "high"
        elif "has" in prop_name or "is" in prop_name:
            return "medium"
        else:
            return "low"
    
    def _extract_process_code(self, entity_name: str) -> Optional[str]:
        """Extract COBIT5 process code (e.g., EDM01, APO02) from entity name"""
        import re
        
        # Pattern for COBIT5 process codes
        pattern = r'(EDM|APO|BAI|DSS|MEA)\d{2}'
        match = re.search(pattern, entity_name.upper())
        
        return match.group(0) if match else None
    
    def _generate_cobit5_analysis(self, enhanced_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate COBIT5-specific analysis"""
        analysis = {
            "domains_found": [],
            "governance_coverage": {},
            "process_distribution": {},
            "business_readiness": "unknown"
        }
        
        # Analyze domains found
        for category in ["classes", "properties", "individuals"]:
            if category in enhanced_data:
                for entity in enhanced_data[category]:
                    domain = entity.get("cobit5_domain")
                    if domain and domain not in analysis["domains_found"]:
                        analysis["domains_found"].append(domain)
                        
        # Calculate governance coverage
        total_domains = len(self.cobit5_domains)
        found_domains = len(analysis["domains_found"])
        analysis["governance_coverage"] = {
            "domains_found": found_domains,
            "total_domains": total_domains,
            "coverage_percentage": (found_domains / total_domains * 100) if total_domains > 0 else 0
        }
        
        # Assess business readiness
        layer_stats = enhanced_data.get("layer_statistics", {})
        business_entities = layer_stats.get("business", {}).get("total", 0)
        
        if business_entities >= 20:
            analysis["business_readiness"] = "high"
        elif business_entities >= 10:
            analysis["business_readiness"] = "medium"
        else:
            analysis["business_readiness"] = "low"
            
        return analysis
