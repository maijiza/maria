#!/usr/bin/env python3
"""
COBIT5 Ontology Integration Module for waDoker LIMS
Integrates COBIT5 governance framework into Graphiti knowledge graph
"""

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
from urllib.parse import urlparse

from pydantic import BaseModel

try:
    # Attempt to import library for parsing RDF/Turtle files
    from rdflib import Graph as RDFGraph, Namespace
    from rdflib.namespace import RDF, RDFS, OWL, DCTERMS as NS_DCTERMS, XSD
    RDFLIB_AVAILABLE = True
except ImportError:
    RDFLIB_AVAILABLE = False
    RDFGraph = None
    RDF = None
    RDFS = None
    OWL = None
    NS_DCTERMS = None
    XSD = None

logger = logging.getLogger(__name__)

class COBIT5OntologyParser:
    """
    Parse COBIT5 ontology files (.ttl) and convert to Graphiti JSON format
    """
    
    def __init__(self, ontology_path: str = "docs/ontologie/"):
        self.ontology_path = Path(ontology_path)
        self.cobit5_namespace = "http://purl.org/atextor/ontology/cobit5#"
        self.rdf_graph = None
        
    def parse_cobit5_ontology(self) -> Dict[str, Any]:
        """
        Parse the main COBIT5 ontology file and extract structured data
        """
        if not RDFLIB_AVAILABLE:
            logger.error("rdflib not available - cannot parse RDF/Turtle files")
            return {"error": "RDF parsing library not available"}
        
        cobit_file = self.ontology_path / "1_cobit5.ttl"
        if not cobit_file.exists():
            logger.error(f"COBIT5 ontology file not found: {cobit_file}")
            return {"error": f"File not found: {cobit_file}"}
        
        try:
            # Initialize RDF graph
            self.rdf_graph = RDFGraph()
            logger.info(f"Loading COBIT5 ontology from {cobit_file}")
            self.rdf_graph.parse(str(cobit_file), format="turtle")
            
            # Extract structured COBIT5 data
            extracted_data = {
                "ontology_metadata": self._extract_metadata(),
                "processes": self._extract_processes(), 
                "domains": self._extract_domains(),
                "goals": self._extract_goals(),
                "controls": self._extract_controls(),
                "stakeholders": self._extract_stakeholders(),
                "enablers": self._extract_enablers()
            }
            
            logger.info(f"Successfully parsed COBIT5 ontology: {len(extracted_data)} categories")
            return extracted_data
            
        except Exception as e:
            logger.error(f"Failed to parse COBIT5 ontology: {e}")
            return {"error": f"Parsing failed: {str(e)}"}
    
    def _extract_metadata(self) -> Dict[str, str]:
        """Extract ontology metadata"""
        metadata = {}
        
        # Get ontology IRI
        for s, p, o in self.rdf_graph.triples((None, RDF.type, OWL.Ontology)):
            # Extract title, description, version, etc.
            title = self._get_literal_value(s, NS_DCTERMS.title, "")
            description = self._get_literal_value(s, NS_DCTERMS.description, "")
            version = self._get_literal_value(s, OWL.versionInfo, "")
            metadata.update({
                "title": title,
                "description": description, 
                "version": version,
                "namespace": str(s)
            })
            break
            
        return metadata
    
    def _extract_processes(self) -> List[Dict[str, Any]]:
        """Extract COBIT5 processes by domain (EDM, APO, BAI, DSS, MEA)"""
        processes = []
        cobit5 = Namespace(self.cobit5_namespace)
        
        # Query for processes and their attributes
        query_result = list(self.rdf_graph.query("""
            PREFIX cobit5: <http://purl.org/atextor/ontology/cobit5#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX owl: <http://www.w3.org/2002/07/owl#>
            
            SELECT ?process ?domain ?code ?name ?description ?purpose
            WHERE {
                ?process rdf:type owl:Class ;
                         rdfs:label ?name .
                OPTIONAL { ?process cobit5:purpose ?purpose }
                OPTIONAL { ?process cobit5:description ?description }
                # Add more process-specific queries as needed
            }
        """))
        
        for row in query_result:
            process_data = {
                "process_uri": str(row.process) if row.process else "",
                "domain": row.domain if hasattr(row, 'domain') else "",
                "code": row.code if hasattr(row, 'code') else "",
                "name": str(row.name) if row.name else "",
                "description": str(row.description) if hasattr(row, 'description') else "",
                "purpose": str(row.purpose) if hasattr(row, 'purpose') else ""
            }
            processes.append(process_data)
        
        logger.info(f"Extracted {len(processes)} COBIT5 processes")
        return processes
    
    def _extract_domains(self) -> List[Dict[str, Any]]:
        """Extract COBIT5 governance and management domains"""
        domains = []
        
        # Known COBIT5 domains
        cobit_domains = {
            "EDM": "Evaluate, Direct and Monitor", 
            "APO": "Align, Plan and Organize",
            "BAI": "Build, Acquire and Implement", 
            "DSS": "Deliver, Service and Support",
            "MEA": "Monitor, Evaluate and Assess"
        }
        
        for code, name in cobit_domains.items():
            domain_data = {
                "code": code,
                "name": name,
                "type": "Governance Domain" if code == "EDM" else "Management Domain",
                "level": 1 if code == "EDM" else 2
            }
            domains.append(domain_data)
        
        return domains
    
    def _extract_goals(self) -> List[Dict[str, Any]]:
        """Extract enterprise and IT goals"""
        goals = []
        
        # This would be expanded with actual SPARQL queries
        # For now, structure according to COBIT5 goals framework
        enterprise_goals = [
            {"type": "Enterprise Goal", "category": "Financial", "name": "ROI of IT"},
            {"type": "Enterprise Goal", "category": "Financial", "name": "Portfolio of competitive products"},
            {"type": "Enterprise Goal", "category": "Customer", "name": "Customer-oriented service culture"},
            {"type": "Enterprise Goal", "category": "Internal", "name": "Optimized process automation"},
            {"type": "Enterprise Goal", "category": "Learning and Growth", "name": "Competent and motivated business staff"}
        ]
        
        it_goals = [
            {"type": "IT Goal", "category": "Customer", "name": "Optimized IT expenses and assets"},
            {"type": "IT Goal", "category": "Internal", "name": "IT compliance and support for business requirements"},
            {"type": "IT Goal", "category": "Learning and Growth", "name": "IT knowledge, expertise and initiatives for innovation"}
        ]
        
        goals.extend(enterprise_goals + it_goals)
        return goals
    
    def _extract_controls(self) -> List[Dict[str, Any]]:
        """Extract control objectives from COBIT5"""
        return []  # To be implemented with specific control extraction
    
    def _extract_stakeholders(self) -> List[Dict[str, Any]]:
        """Extract stakeholder definitions"""
        return []  # To be implemented
    
    def _extract_enablers(self) -> List[Dict[str, Any]]:
        """Extract COBIT5 seven enablers"""
        enablers = [
            {"name": "Principles, Policies and Frameworks", "id": "01"},
            {"name": "Processes", "id": "02"},
            {"name": "Organisational Structures", "id": "03"},
            {"name": "Culture, Ethics and Behaviour", "id": "04"},
            {"name": "Information", "id": "05"},
            {"name": "Services, Infrastructure and Applications", "id": "06"},
            {"name": "People, Skills and Competencies", "id": "07"}
        ]
        return enablers
    
    def _get_literal_value(self, subject, predicate, default: str = "") -> str:
        """Helper to extract literal values from RDF graph"""
        if not self.rdf_graph:
            return default
        try:
            for s, p, o in self.rdf_graph.triples((subject, predicate, None)):
                return str(o)
        except:
            pass
        return default


class COBIT5GraphitiIntegrator:
    """
    Integrate COBIT5 ontology data into Graphiti knowledge graph through MCP server
    """
    
    def __init__(self, mcp_add_memory_func):
        self.add_memory = mcp_add_memory_func
        self.group_id = "cobit5_governance"
        
    async def integrate_cobit5_ontologies(self, ontology_path: str = "docs/ontologie/"):
        """
        Main integration method to load all COBIT5 ontologies into Graphiti
        """
        try:
            # Parse COBIT5 ontologies
            parser = COBIT5OntologyParser(ontology_path)
            ontologies_data = parser.parse_cobit5_ontology()
            
            if "error" in ontologies_data:
                logger.error(f"Failed to parse COBIT5: {ontologies_data['error']}")
                return {"success": False, "error": ontologies_data["error"]}
            
            # Process each category and add to knowledge graph
            integration_results = {}
            
            # Add ontology metadata
            metadata_result = await self._add_metadata_to_graph(
                ontologies_data.get("ontology_metadata", {})
            )
            integration_results["metadata"] = metadata_result
            
            # Add process networks
            processes_result = await self._add_processes_to_graph(
                ontologies_data.get("processes", [])
            )
            integration_results["processes"] = processes_result
            
            # Add governance domains
            domains_result = await self._add_domains_to_graph(
                ontologies_data.get("domains", [])
            )
            integration_results["domains"] = domains_result
            
            # Add goals framework 
            goals_result = await self._add_goals_to_graph(
                ontologies_data.get("goals", [])
            )
            integration_results["goals"] = goals_result
            
            # Add enablers
            enablers_result = await self._add_enablers_to_graph(
                ontologies_data.get("enablers", [])
            )
            integration_results["enablers"] = enablers_result
            
            logger.info(f"COBIT5 integration completed: {integration_results}")
            return {"success": True, "results": integration_results}
            
        except Exception as e:
            logger.error(f"COBIT5 integration failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _add_metadata_to_graph(self, metadata: Dict) -> Dict:
        """Add ontology metadata to Graphiti"""
        result = await self.add_memory(
            name="COBIT5 Ontology Metadata",
            episode_body=json.dumps(metadata),
            group_id=self.group_id,
            source="json",
            source_description="COBIT5 ontology header metadata"
        )
        return result
    
    async def _add_processes_to_graph(self, processes: List[Dict]) -> Dict:
        """Add COBIT5 processes network to Graphiti"""
        result = await self.add_memory(
            name="COBIT5 Management and Governance Processes",
            episode_body=json.dumps({"processes": processes}),
            group_id=self.group_id,
            source="json", 
            source_description="Process definitions and governance frameworks"
        )
        return result
        
    async def _add_domains_to_graph(self, domains: List[Dict]) -> Dict:
        """Add governance domains to Graphiti"""
        result = await self.add_memory(
            name="COBIT5 Governance and Management Domains",
            episode_body=json.dumps({"domains": domains}),
            group_id=self.group_id,
            source="json",
            source_description="Governance structure framework"
        )
        return result
        
    async def _add_goals_to_graph(self, goals: List[Dict]) -> Dict:
        """Add COBIT5 goals cascade to Graphiti"""
        result = await self.add_memory(
            name="COBIT5 Enterprise and IT Goals Cascade",
            episode_body=json.dumps({"goals": goals}),
            group_id=self.group_id,
            source="json",
            source_description="Goals cascade for governance alignment"
        )
        return result
        
    async def _add_enablers_to_graph(self, enablers: List[Dict]) -> Dict:
        """Add COBIT5 seven enablers to Graphiti"""
        result = await self.add_memory(
            name="COBIT5 Seven Enablers Framework",
            episode_body=json.dumps({"enablers": enablers}),
            group_id=self.group_id,
            source="json",
            source_description="Complete enabler framework"
        )
        return result


# MCP integration helper
def create_cobit5_integrator(add_memory_func):
    """Factory for COBIT5 Graphiti integrator"""
    return COBIT5GraphitiIntegrator(add_memory_func)
