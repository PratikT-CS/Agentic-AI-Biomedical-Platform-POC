"""
Workflow service for coordinating data sources and AI orchestration
"""

from typing import List, Dict, Optional, Any
from loguru import logger
import asyncio
from datetime import datetime
import json

from ai_agent.orchestrator import AIOrchestrator
from database.models import SessionLocal, QueryLog, DataProvenance, WorkflowExecution
from adapters.pubmed_adapter import PubMedAdapter
from adapters.uniprot_adapter import UniProtAdapter
from adapters.swissadme_adapter import SwissADMEAdapter

class WorkflowService:
    """Service for managing biomedical research workflows"""
    
    def __init__(self):
        self.ai_orchestrator = AIOrchestrator()
        self.pubmed_adapter = PubMedAdapter()
        self.uniprot_adapter = UniProtAdapter()
        self.swissadme_adapter = SwissADMEAdapter()
        self.initialized = False
        
    async def initialize(self):
        """Initialize the workflow service"""
        try:
            await self.ai_orchestrator.initialize()
            self.initialized = True
            logger.info("Workflow service initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing workflow service: {e}")
            self.initialized = False
    
    async def process_query(self, query: str, sources: List[str], max_results: int = 10) -> Dict:
        """
        Process a biomedical research query
        
        Args:
            query: The research query
            sources: List of data sources to query
            max_results: Maximum results per source
            
        Returns:
            Dictionary containing processed results
        """
        start_time = datetime.utcnow()
        query_log_id = None
        
        try:
            logger.info(f"Processing query: {query}")
            
            # Log the query
            query_log_id = await self._log_query(query, sources, start_time)
            
            # Process using AI orchestration if available
            if self.initialized:
                result = await self.ai_orchestrator.process_query(query, sources, max_results)
                orchestration_method = "ai_orchestration"
            else:
                # Fallback to direct processing
                result = await self._direct_processing(query, sources, max_results)
                orchestration_method = "direct_processing"
            
            # Log data provenance
            await self._log_data_provenance(query_log_id, result, sources)
            
            # Log workflow execution
            await self._log_workflow_execution(query_log_id, orchestration_method, result)
            
            # Update query log with results
            processing_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            await self._update_query_log(query_log_id, result, processing_time, "completed")
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            
            # Update query log with error
            if query_log_id:
                processing_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
                await self._update_query_log(query_log_id, None, processing_time, "failed", str(e))
            
            return {
                "query": query,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
                "status": "error"
            }
    
    async def _direct_processing(self, query: str, sources: List[str], max_results: int) -> Dict:
        """Direct processing without AI orchestration"""
        try:
            results = {}
            
            # Process each source
            for source in sources:
                try:
                    if source == "pubmed":
                        source_results = await self.pubmed_adapter.search_articles(query, max_results)
                    elif source == "uniprot":
                        source_results = await self.uniprot_adapter.search_proteins(query, max_results)
                    elif source == "swissadme":
                        # For SwissADME, we need SMILES notation
                        # This is a simplified approach
                        # smiles_query = "c1ccccc1Oc1ccccc1"  # Placeholder - in practice, convert query to SMILES
                        source_results = await self.swissadme_adapter.search_drug_properties(query)
                    else:
                        source_results = {"error": f"Unknown source: {source}"}
                    
                    results[source] = source_results
                    
                except Exception as e:
                    logger.error(f"Error processing source {source}: {e}")
                    results[source] = {"error": str(e)}
            
            return {
                "query": query,
                "sources_queried": sources,
                "results": results,
                "timestamp": datetime.utcnow().isoformat(),
                # "orchestration_method": "direct_processing"
                "orchestration_method": "Direct"
            }
            
        except Exception as e:
            logger.error(f"Error in direct processing: {e}")
            raise
    
    async def _log_query(self, query: str, sources: List[str], start_time: datetime) -> int:
        """Log the query to database"""
        try:
            db = SessionLocal()
            query_log = QueryLog(
                query=query,
                sources=sources,
                timestamp=start_time,
                status="processing"
            )
            db.add(query_log)
            db.commit()
            db.refresh(query_log)
            query_log_id = query_log.id
            db.close()
            
            logger.info(f"Logged query with ID: {query_log_id}")
            return query_log_id
            
        except Exception as e:
            logger.error(f"Error logging query: {e}")
            return None
    
    async def _log_data_provenance(self, query_log_id: int, result: Dict, sources: List[str]):
        """Log data provenance information"""
        try:
            if not query_log_id:
                return
            
            db = SessionLocal()
            
            # Log provenance for each source
            for source in sources:
                provenance = DataProvenance(
                    query_log_id=query_log_id,
                    source=source,
                    data_type=self._get_data_type(source),
                    extraction_method=self._get_extraction_method(source),
                    timestamp=datetime.utcnow()
                )
                db.add(provenance)
            
            db.commit()
            db.close()
            
        except Exception as e:
            logger.error(f"Error logging data provenance: {e}")
    
    async def _log_workflow_execution(self, query_log_id: int, orchestration_method: str, result: Dict):
        """Log workflow execution details"""
        try:
            if not query_log_id:
                return
            
            db = SessionLocal()
            
            workflow_execution = WorkflowExecution(
                query_log_id=query_log_id,
                workflow_type=orchestration_method,
                steps=self._extract_workflow_steps(result),
                ai_model="gemini-pro" if orchestration_method == "ai_orchestration" else None,
                status="completed",
                timestamp=datetime.utcnow()
            )
            db.add(workflow_execution)
            db.commit()
            db.close()
            
        except Exception as e:
            logger.error(f"Error logging workflow execution: {e}")
    
    async def _update_query_log(self, query_log_id: int, result: Dict, processing_time: int, status: str, error_message: str = None):
        """Update query log with results"""
        try:
            if not query_log_id:
                return
            
            db = SessionLocal()
            query_log = db.query(QueryLog).filter(QueryLog.id == query_log_id).first()
            
            if query_log:
                query_log.results = result
                query_log.processing_time = processing_time
                query_log.status = status
                query_log.error_message = error_message
                
                db.commit()
            
            db.close()
            
        except Exception as e:
            logger.error(f"Error updating query log: {e}")
    
    def _get_data_type(self, source: str) -> str:
        """Get data type for a source"""
        data_types = {
            "pubmed": "article",
            "uniprot": "protein",
            "swissadme": "drug_property"
        }
        return data_types.get(source, "unknown")
    
    def _get_extraction_method(self, source: str) -> str:
        """Get extraction method for a source"""
        methods = {
            "pubmed": "api",
            "uniprot": "api",
            "swissadme": "web_scraping"
        }
        return methods.get(source, "unknown")
    
    def _extract_workflow_steps(self, result: Dict) -> List[str]:
        """Extract workflow steps from result"""
        steps = []
        
        if "sources_queried" in result:
            for source in result["sources_queried"]:
                steps.append(f"query_{source}")
        
        if "ai_analysis" in result:
            steps.append("ai_synthesis")
        
        return steps
    
    async def get_recent_logs(self, limit: int = 100) -> List[Dict]:
        """Get recent query logs"""
        try:
            db = SessionLocal()
            logs = db.query(QueryLog).order_by(QueryLog.timestamp.desc()).limit(limit).all()
            
            log_data = []
            for log in logs:
                log_data.append({
                    "id": log.id,
                    "query": log.query,
                    "sources": log.sources,
                    "timestamp": log.timestamp.isoformat(),
                    "processing_time": log.processing_time,
                    "status": log.status,
                    "error_message": log.error_message
                })
            
            db.close()
            return log_data
            
        except Exception as e:
            logger.error(f"Error retrieving logs: {e}")
            return []
    
    async def cleanup(self):
        """Cleanup resources"""
        try:
            if self.ai_orchestrator:
                await self.ai_orchestrator.cleanup()
            if self.swissadme_adapter:
                self.swissadme_adapter.cleanup()
            logger.info("Workflow service cleaned up")
        except Exception as e:
            logger.error(f"Error cleaning up workflow service: {e}")
