"""
Ontology importer for Graphiti knowledge graph.

Imports classified ontology data into Graphiti with proper layer labels
and structured relationships.
"""

import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class OntologyImporter:
    """
    Imports classified ontology data into Graphiti knowledge graph.
    
    Creates nodes with proper layer labels for targeted search and
    maintains ontological relationships between entities.
    """
    
    def __init__(self, add_memory_func):
        """
        Initialize with Graphiti add_memory function.
        
        Args:
            add_memory_func: The add_memory function from MCP server
        """
        self.add_memory = add_memory_func
        
    async def import_with_layers(
        self, 
        classified_data: Dict[str, Any], 
        group_id: str,
        framework_name: str = "Generic"
    ) -> Dict[str, Any]:
        """
        Import classified ontology data into Graphiti with layer support.
        
        Args:
            classified_data: Output from LayerClassifier.classify()
            group_id: Target group ID for the ontology
            framework_name: Name of the framework (e.g., "COBIT5", "ISO17025")
            
        Returns:
            Import results with statistics and episode UUIDs
        """
        if "error" in classified_data:
            return {"success": False, "error": classified_data["error"]}
            
        try:
            import_results = {}
            
            # Import metadata
            if "metadata" in classified_data:
                metadata_result = await self._import_metadata(
                    classified_data["metadata"], group_id, framework_name
                )
                import_results["metadata"] = metadata_result
                
            # Import classes by layer
            if "classes" in classified_data:
                classes_result = await self._import_classes_by_layer(
                    classified_data["classes"], group_id, framework_name
                )
                import_results["classes"] = classes_result
                
            # Import properties by layer
            if "properties" in classified_data:
                properties_result = await self._import_properties_by_layer(
                    classified_data["properties"], group_id, framework_name
                )
                import_results["properties"] = properties_result
                
            # Import individuals by layer
            if "individuals" in classified_data:
                individuals_result = await self._import_individuals_by_layer(
                    classified_data["individuals"], group_id, framework_name
                )
                import_results["individuals"] = individuals_result
                
            # Import relationships
            if "relationships" in classified_data:
                relationships_result = await self._import_relationships(
                    classified_data["relationships"], group_id, framework_name
                )
                import_results["relationships"] = relationships_result
                
            # Generate summary
            summary = self._generate_import_summary(import_results, classified_data)
            
            logger.info(f"Ontology import completed for {framework_name}: {summary}")
            return {"success": True, "results": import_results, "summary": summary}
            
        except Exception as e:
            logger.error(f"Ontology import failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _import_metadata(
        self, 
        metadata: Dict[str, Any], 
        group_id: str, 
        framework_name: str
    ) -> Dict[str, Any]:
        """Import ontology metadata"""
        result = await self.add_memory(
            name=f"{framework_name} Ontology Metadata",
            episode_body=json.dumps(metadata),
            group_id=group_id,
            source="json",
            source_description=f"Ontology metadata for {framework_name} framework"
        )
        return result
    
    async def _import_classes_by_layer(
        self, 
        classes: List[Dict[str, Any]], 
        group_id: str, 
        framework_name: str
    ) -> Dict[str, Any]:
        """Import classes organized by layer"""
        # Organize classes by layer
        layers = {"business": [], "technical": [], "core": []}
        
        for cls in classes:
            primary_layer = cls.get("primary_layer", "technical")
            if primary_layer in layers:
                layers[primary_layer].append(cls)
                
        # Import each layer separately
        layer_results = {}
        
        for layer_name, layer_classes in layers.items():
            if layer_classes:
                result = await self.add_memory(
                    name=f"{framework_name} Classes - {layer_name.title()} Layer",
                    episode_body=json.dumps({
                        "layer": layer_name,
                        "framework": framework_name,
                        "classes": layer_classes,
                        "count": len(layer_classes)
                    }),
                    group_id=group_id,
                    source="json",
                    source_description=f"{framework_name} {layer_name} layer classes"
                )
                layer_results[layer_name] = result
                
        return layer_results
    
    async def _import_properties_by_layer(
        self, 
        properties: List[Dict[str, Any]], 
        group_id: str, 
        framework_name: str
    ) -> Dict[str, Any]:
        """Import properties organized by layer"""
        # Organize properties by layer
        layers = {"business": [], "technical": [], "core": []}
        
        for prop in properties:
            primary_layer = prop.get("primary_layer", "technical")
            if primary_layer in layers:
                layers[primary_layer].append(prop)
                
        # Import each layer separately
        layer_results = {}
        
        for layer_name, layer_properties in layers.items():
            if layer_properties:
                result = await self.add_memory(
                    name=f"{framework_name} Properties - {layer_name.title()} Layer",
                    episode_body=json.dumps({
                        "layer": layer_name,
                        "framework": framework_name,
                        "properties": layer_properties,
                        "count": len(layer_properties)
                    }),
                    group_id=group_id,
                    source="json",
                    source_description=f"{framework_name} {layer_name} layer properties"
                )
                layer_results[layer_name] = result
                
        return layer_results
    
    async def _import_individuals_by_layer(
        self, 
        individuals: List[Dict[str, Any]], 
        group_id: str, 
        framework_name: str
    ) -> Dict[str, Any]:
        """Import individuals organized by layer"""
        # Organize individuals by layer
        layers = {"business": [], "technical": [], "core": []}
        
        for individual in individuals:
            primary_layer = individual.get("primary_layer", "technical")
            if primary_layer in layers:
                layers[primary_layer].append(individual)
                
        # Import each layer separately
        layer_results = {}
        
        for layer_name, layer_individuals in layers.items():
            if layer_individuals:
                result = await self.add_memory(
                    name=f"{framework_name} Individuals - {layer_name.title()} Layer",
                    episode_body=json.dumps({
                        "layer": layer_name,
                        "framework": framework_name,
                        "individuals": layer_individuals,
                        "count": len(layer_individuals)
                    }),
                    group_id=group_id,
                    source="json",
                    source_description=f"{framework_name} {layer_name} layer individuals"
                )
                layer_results[layer_name] = result
                
        return layer_results
    
    async def _import_relationships(
        self, 
        relationships: List[Dict[str, Any]], 
        group_id: str, 
        framework_name: str
    ) -> Dict[str, Any]:
        """Import relationships between entities"""
        # Group relationships by type for better organization
        relationship_groups = {}
        
        for rel in relationships:
            predicate = rel.get("predicate_local_name", "unknown")
            if predicate not in relationship_groups:
                relationship_groups[predicate] = []
            relationship_groups[predicate].append(rel)
            
        # Import relationship groups
        group_results = {}
        
        for rel_type, rel_list in relationship_groups.items():
            if len(rel_list) > 0:
                result = await self.add_memory(
                    name=f"{framework_name} Relationships - {rel_type}",
                    episode_body=json.dumps({
                        "relationship_type": rel_type,
                        "framework": framework_name,
                        "relationships": rel_list,
                        "count": len(rel_list)
                    }),
                    group_id=group_id,
                    source="json",
                    source_description=f"{framework_name} {rel_type} relationships"
                )
                group_results[rel_type] = result
                
        return group_results
    
    def _generate_import_summary(
        self, 
        import_results: Dict[str, Any], 
        classified_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate comprehensive import summary"""
        
        # Count entities by layer
        layer_stats = classified_data.get("layer_statistics", {})
        
        # Count episodes created
        episodes_created = 0
        for category_results in import_results.values():
            if isinstance(category_results, dict):
                for layer_result in category_results.values():
                    if isinstance(layer_result, dict) and "message" in layer_result:
                        episodes_created += 1
                        
        # Statistics from original data
        stats = classified_data.get("statistics", {})
        
        summary = {
            "import_timestamp": datetime.now(timezone.utc).isoformat(),
            "episodes_created": episodes_created,
            "entities_processed": {
                "classes": stats.get("classes", 0),
                "properties": stats.get("object_properties", 0) + stats.get("datatype_properties", 0),
                "individuals": stats.get("individuals", 0),
                "relationships": stats.get("relationships", 0)
            },
            "layer_distribution": layer_stats,
            "original_triples": stats.get("total_triples", 0),
            "import_categories": list(import_results.keys())
        }
        
        return summary
