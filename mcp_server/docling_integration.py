"""
Docling Integration for waGraphiti MCP Server

Extends MCP tools with document processing capabilities via Docling microservice.
"""

import asyncio
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
import httpx
import tempfile
import time
from datetime import datetime, timezone

from graphiti_core import Graphiti
from graphiti_core.nodes import EpisodeType
from pydantic import BaseModel

logger = logging.getLogger(__name__)

# Configuration
DOCLING_SERVICE_URL = "http://docling-service:5001"  # Official docling-serve port
DOCLING_TIMEOUT = 300.0  # 5 minutes max processing time


class DoclingResponse(BaseModel):
    """Docling service response model"""
    success: bool
    document_id: str
    processing_time_seconds: float
    text_content: str
    tables: List[Dict] = []
    figures: List[Dict] = []
    metadata: Dict = {}
    pages_processed: int = 0
    confidence_score: float = 0.0
    warnings: List[str] = []
    error_details: Optional[str] = None


class DoclingIntegration:
    """Integration client for Docling microservice"""
    
    def __init__(self, graphiti_instance: Graphiti):
        self.graphiti = graphiti_instance
        self.client = httpx.AsyncClient(timeout=DOCLING_TIMEOUT)
        self.stats = {
            "documents_processed": 0,
            "successful_processes": 0,
            "failed_processes": 0,
            "total_processing_time": 0.0
        }
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    async def health_check(self) -> bool:
        """Check if Docling service is available"""
        try:
            # Try both health and root endpoints
            response = await self.client.get(f"{DOCLING_SERVICE_URL}/")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Docling health check failed: {e}")
            return False
    
    async def get_service_info(self) -> Optional[Dict]:
        """Get Docling service capabilities"""
        try:
            response = await self.client.get(f"{DOCLING_SERVICE_URL}/info")
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"Failed to get Docling service info: {e}")
            return None
    
    async def get_models_status(self) -> Optional[Dict]:
        """Get AI models download and cache status"""
        try:
            response = await self.client.get(f"{DOCLING_SERVICE_URL}/models")
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"Failed to get models status: {e}")
            return None
    
    async def process_document_file(
        self,
        file_path: str,
        extract_tables: bool = True,
        extract_figures: bool = True,
        ocr_enabled: bool = True
    ) -> DoclingResponse:
        """Process a document file via Docling service"""
        
        start_time = time.time()
        self.stats["documents_processed"] += 1
        
        try:
            # Validate file exists
            if not Path(file_path).exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            # Prepare file upload
            with open(file_path, 'rb') as f:
                files = {
                    'file': (Path(file_path).name, f, self._get_content_type(file_path))
                }
                data = {
                    'extract_tables': extract_tables,
                    'extract_figures': extract_figures,
                    'ocr_enabled': ocr_enabled
                }
                
                logger.info(f"Processing document via Docling: {file_path}")
                
                # Send to Docling service (official docling-serve API)
                response = await self.client.post(
                    f"{DOCLING_SERVICE_URL}/v1/convert/file",  # Official endpoint
                    files={'files': (Path(file_path).name, f, self._get_content_type(file_path))}
                )
            
            processing_time = time.time() - start_time
            self.stats["total_processing_time"] += processing_time
            
            if response.status_code == 200:
                result_data = response.json()
                
                # Adapt official docling-serve response to our format
                doc_response = result_data.get('document', {})
                
                result = DoclingResponse(
                    success=result_data.get('status') == 'success',
                    document_id=f"doc_{int(time.time())}",
                    processing_time_seconds=result_data.get('processing_time', processing_time),
                    text_content=doc_response.get('md_content', ''),
                    tables=self._extract_tables_from_json(result_data),
                    figures=self._extract_figures_from_json(result_data),
                    metadata={'filename': doc_response.get('filename', '')},
                    pages_processed=1,  # Default for HTML
                    confidence_score=0.95,  # High confidence for successful processing
                    warnings=[],
                    error_details=None if result_data.get('status') == 'success' else 'Processing failed'
                )
                
                if result.success:
                    self.stats["successful_processes"] += 1
                    logger.info(f"Document processed successfully in {processing_time:.2f}s")
                else:
                    self.stats["failed_processes"] += 1
                    logger.warning(f"Document processing failed: {result.error_details}")
                
                return result
            else:
                self.stats["failed_processes"] += 1
                error_msg = f"Docling service error: {response.status_code}"
                logger.error(error_msg)
                
                return DoclingResponse(
                    success=False,
                    document_id="",
                    processing_time_seconds=processing_time,
                    text_content="",
                    error_details=error_msg
                )
                
        except Exception as e:
            processing_time = time.time() - start_time
            self.stats["failed_processes"] += 1
            self.stats["total_processing_time"] += processing_time
            
            logger.error(f"Document processing failed: {e}")
            
            return DoclingResponse(
                success=False,
                document_id="",
                processing_time_seconds=processing_time,
                text_content="",
                error_details=str(e)
            )
    
    async def process_document_bytes(
        self,
        file_content: bytes,
        filename: str,
        extract_tables: bool = True,
        extract_figures: bool = True,
        ocr_enabled: bool = True
    ) -> DoclingResponse:
        """Process document from bytes via Docling service"""
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=Path(filename).suffix
        ) as temp_file:
            temp_file.write(file_content)
            temp_path = temp_file.name
        
        try:
            return await self.process_document_file(
                file_path=temp_path,
                extract_tables=extract_tables,
                extract_figures=extract_figures,
                ocr_enabled=ocr_enabled
            )
        finally:
            # Clean up temporary file
            Path(temp_path).unlink(missing_ok=True)
    
    async def document_to_knowledge_graph(
        self,
        file_path: str,
        episode_name: Optional[str] = None,
        source_description: Optional[str] = None,
        extract_tables: bool = True,
        extract_figures: bool = True,
        ocr_enabled: bool = True
    ) -> Dict[str, Any]:
        """Complete pipeline: Document → Docling → Knowledge Graph"""
        
        # Step 1: Process document via Docling
        docling_result = await self.process_document_file(
            file_path=file_path,
            extract_tables=extract_tables,
            extract_figures=extract_figures,
            ocr_enabled=ocr_enabled
        )
        
        if not docling_result.success:
            return {
                "success": False,
                "error": "Docling processing failed",
                "details": docling_result.error_details,
                "docling_result": docling_result.dict()
            }
        
        # Step 2: Format for knowledge graph
        episode_text = self._format_for_knowledge_graph(docling_result)
        
        # Step 3: Create episode name if not provided
        if not episode_name:
            filename = Path(file_path).stem
            episode_name = f"Document Analysis: {filename}"
        
        # Step 4: Add to knowledge graph
        try:
            episode = await self.graphiti.add_episode(
                name=episode_name,
                episode_body=episode_text,
                source=EpisodeType.text,
                source_description=source_description or f"Processed via Docling from {Path(file_path).name}",
                reference_time=datetime.now(timezone.utc)
            )
            
            return {
                "success": True,
                "episode_id": getattr(episode, 'episode_uuid', str(episode)),
                "docling_result": docling_result.dict(),
                "knowledge_graph_ingestion": {
                    "episode_name": episode_name,
                    "text_length": len(episode_text),
                    "tables_processed": len(docling_result.tables),
                    "figures_processed": len(docling_result.figures),
                    "processing_time": docling_result.processing_time_seconds
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to add episode to knowledge graph: {e}")
            return {
                "success": False,
                "error": "Knowledge graph ingestion failed",
                "details": str(e),
                "docling_result": docling_result.dict()
            }
    
    def _get_content_type(self, file_path: str) -> str:
        """Determine content type from file extension"""
        suffix = Path(file_path).suffix.lower()
        content_types = {
            '.pdf': 'application/pdf',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.doc': 'application/msword',
            '.html': 'text/html',
            '.htm': 'text/html',
        }
        return content_types.get(suffix, 'application/octet-stream')
    
    def _format_for_knowledge_graph(self, docling_result: DoclingResponse) -> str:
        """Format Docling result for knowledge graph ingestion"""
        
        formatted_parts = []
        
        # Main text content
        if docling_result.text_content:
            formatted_parts.append("=== DOCUMENT CONTENT ===")
            formatted_parts.append(docling_result.text_content)
        
        # Tables
        if docling_result.tables:
            formatted_parts.append("\n=== EXTRACTED TABLES ===")
            for i, table in enumerate(docling_result.tables, 1):
                formatted_parts.append(f"\nTable {i}:")
                if table.get('caption'):
                    formatted_parts.append(f"Caption: {table['caption']}")
                
                headers = table.get('headers', [])
                rows = table.get('rows', [])
                
                if headers:
                    formatted_parts.append("Headers: " + " | ".join(headers))
                
                for row in rows[:10]:  # Limit to first 10 rows
                    formatted_parts.append("Data: " + " | ".join(str(cell) for cell in row))
                
                if len(rows) > 10:
                    formatted_parts.append(f"... and {len(rows) - 10} more rows")
        
        # Figures
        if docling_result.figures:
            formatted_parts.append("\n=== EXTRACTED FIGURES ===")
            for i, figure in enumerate(docling_result.figures, 1):
                formatted_parts.append(f"\nFigure {i}:")
                if figure.get('caption'):
                    formatted_parts.append(f"Caption: {figure['caption']}")
                if figure.get('figure_type'):
                    formatted_parts.append(f"Type: {figure['figure_type']}")
        
        # Metadata
        if docling_result.metadata:
            formatted_parts.append("\n=== DOCUMENT METADATA ===")
            for key, value in docling_result.metadata.items():
                if value:
                    formatted_parts.append(f"{key.title()}: {value}")
        
        # Processing info
        formatted_parts.append("\n=== PROCESSING INFORMATION ===")
        formatted_parts.append(f"Pages Processed: {docling_result.pages_processed}")
        formatted_parts.append(f"Processing Time: {docling_result.processing_time_seconds:.2f} seconds")
        formatted_parts.append(f"Confidence Score: {docling_result.confidence_score:.2f}")
        
        if docling_result.warnings:
            formatted_parts.append("Warnings: " + "; ".join(docling_result.warnings))
        
        return "\n".join(formatted_parts)
    
    def _extract_tables_from_json(self, docling_result: Dict) -> List[Dict]:
        """Extract table data from docling-serve JSON response"""
        tables = []
        
        try:
            # docling-serve returns structured JSON with table information
            json_content = docling_result.get('document', {}).get('json_content')
            if json_content and 'tables' in json_content:
                for i, table in enumerate(json_content['tables']):
                    # Extract table structure from Docling JSON format
                    table_data = {
                        'table_id': f'table_{i+1}',
                        'headers': [],
                        'rows': [],
                        'coordinates': {},
                        'confidence': 0.9,
                        'caption': None
                    }
                    
                    # Parse table data if available
                    if 'data' in table and 'table_cells' in table['data']:
                        cells = table['data']['table_cells']
                        # Process table cells to extract headers and rows
                        # This is a simplified extraction
                        table_data['rows'] = self._process_table_cells(cells)
                    
                    tables.append(table_data)
            
            # Fallback: extract from markdown table format
            md_content = docling_result.get('document', {}).get('md_content', '')
            if '|' in md_content and not tables:
                tables = self._extract_tables_from_markdown(md_content)
                
        except Exception as e:
            logger.warning(f"Failed to extract tables: {e}")
        
        return tables
    
    def _extract_figures_from_json(self, docling_result: Dict) -> List[Dict]:
        """Extract figure data from docling-serve JSON response"""
        figures = []
        
        try:
            json_content = docling_result.get('document', {}).get('json_content')
            if json_content and 'pictures' in json_content:
                for i, picture in enumerate(json_content['pictures']):
                    figure_data = {
                        'figure_id': f'fig_{i+1}',
                        'caption': None,
                        'coordinates': {},
                        'figure_type': 'image',
                        'confidence': 0.85
                    }
                    
                    # Extract caption from captions array if available
                    if 'captions' in picture and picture['captions']:
                        # Get first caption reference
                        caption_ref = picture['captions'][0].get('$ref', '')
                        # This would need to be resolved against the document
                        figure_data['caption'] = f"Figure {i+1}"
                    
                    figures.append(figure_data)
                    
        except Exception as e:
            logger.warning(f"Failed to extract figures: {e}")
        
        return figures
    
    def _process_table_cells(self, table_cells: List[Dict]) -> List[List[str]]:
        """Process table cells into rows format"""
        rows = []
        try:
            # Group cells by row
            cell_rows = {}
            for cell in table_cells:
                row_idx = cell.get('start_row_offset_idx', 0)
                if row_idx not in cell_rows:
                    cell_rows[row_idx] = []
                cell_rows[row_idx].append({
                    'col': cell.get('start_col_offset_idx', 0),
                    'text': cell.get('text', '')
                })
            
            # Convert to list of lists
            for row_idx in sorted(cell_rows.keys()):
                row_cells = sorted(cell_rows[row_idx], key=lambda x: x['col'])
                row_data = [cell['text'] for cell in row_cells]
                rows.append(row_data)
                
        except Exception as e:
            logger.warning(f"Failed to process table cells: {e}")
        
        return rows
    
    def _extract_tables_from_markdown(self, md_content: str) -> List[Dict]:
        """Extract tables from markdown content"""
        tables = []
        lines = md_content.split('\n')
        
        table_lines = []
        in_table = False
        
        for line in lines:
            if '|' in line and line.strip():
                table_lines.append(line.strip())
                in_table = True
            elif in_table and not line.strip():
                # End of table
                if len(table_lines) >= 2:  # At least header + separator
                    table = self._parse_markdown_table(table_lines)
                    if table:
                        tables.append(table)
                table_lines = []
                in_table = False
        
        # Handle table at end of content
        if table_lines and len(table_lines) >= 2:
            table = self._parse_markdown_table(table_lines)
            if table:
                tables.append(table)
        
        return tables
    
    def _parse_markdown_table(self, table_lines: List[str]) -> Optional[Dict]:
        """Parse markdown table format into structured data"""
        try:
            if len(table_lines) < 2:
                return None
            
            # Parse header row
            header_line = table_lines[0]
            headers = [cell.strip() for cell in header_line.split('|')[1:-1]]
            
            # Skip separator line (index 1)
            # Parse data rows
            rows = []
            for line in table_lines[2:]:
                if '|' in line:
                    row_data = [cell.strip() for cell in line.split('|')[1:-1]]
                    if len(row_data) == len(headers):
                        rows.append(row_data)
            
            return {
                'table_id': f'table_{len(rows)}',
                'headers': headers,
                'rows': rows,
                'coordinates': {},
                'confidence': 0.9,
                'caption': None
            }
            
        except Exception as e:
            logger.warning(f"Failed to parse markdown table: {e}")
            return None

    def get_integration_stats(self) -> Dict[str, Any]:
        """Get integration statistics"""
        return {
            **self.stats,
            "success_rate": (
                self.stats["successful_processes"] / max(1, self.stats["documents_processed"])
            ),
            "average_processing_time": (
                self.stats["total_processing_time"] / max(1, self.stats["documents_processed"])
            )
        }


# Global integration instance
_docling_integration: Optional[DoclingIntegration] = None


async def get_docling_integration(graphiti_instance: Graphiti) -> DoclingIntegration:
    """Get or create Docling integration instance"""
    global _docling_integration
    
    if _docling_integration is None:
        _docling_integration = DoclingIntegration(graphiti_instance)
    
    return _docling_integration


async def cleanup_docling_integration():
    """Cleanup integration resources"""
    global _docling_integration
    
    if _docling_integration:
        await _docling_integration.client.aclose()
        _docling_integration = None
