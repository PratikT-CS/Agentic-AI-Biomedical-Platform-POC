"""
Main FastAPI application for the Agentic AI-Enabled Biomedical Research Platform
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from loguru import logger
import os
from dotenv import load_dotenv

from services.workflow_service import WorkflowService
from database.models import init_database
from config import Config

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Agentic AI Biomedical Research Platform",
    description="A POC platform for integrating biomedical data sources with AI orchestration",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
init_database()

# Initialize workflow service
workflow_service = WorkflowService()

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Starting Agentic AI Biomedical Research Platform")
    await workflow_service.initialize()

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Agentic AI Biomedical Research Platform")
    await workflow_service.cleanup()

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Agentic AI Biomedical Research Platform API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "biomedical-platform"}

@app.post("/api/query")
async def process_query(query_data: dict):
    """
    Process a biomedical research query using AI orchestration
    
    Expected query_data format:
    {
        "query": "string",
        "sources": ["pubmed", "uniprot", "swissadme"],
        "max_results": 10,
        "processingMode": "ai" or "direct"
    }
    """
    try:
        logger.info(f"Processing query: {query_data.get('query', '')}")
        
        # Validate input
        if not query_data.get("query"):
            raise HTTPException(status_code=400, detail="Query is required")
        
        # Set defaults
        sources = query_data.get("sources", ["pubmed", "uniprot", "swissadme"])
        max_results = query_data.get("max_results", 10)
        processing_mode = query_data.get("processingMode", "ai")
        
        # Process query through workflow service
        result = await workflow_service.process_query(
            query=query_data["query"],
            sources=sources,
            max_results=max_results,
            processing_mode=processing_mode
        )
        
        return JSONResponse(content=result)
        
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/sources")
async def get_available_sources():
    """Get list of available data sources"""
    return {
        "sources": [
            {
                "name": "pubmed",
                "description": "PubMed article database",
                "type": "api",
                "status": "available"
            },
            {
                "name": "uniprot",
                "description": "UniProt protein database",
                "type": "api", 
                "status": "available"
            },
            {
                "name": "swissadme",
                "description": "SwissADME drug properties",
                "type": "web_scraping",
                "status": "available"
            }
        ]
    }

@app.get("/api/logs")
async def get_logs(limit: int = 100):
    """Get recent query logs for data provenance"""
    try:
        logs = await workflow_service.get_recent_logs(limit)
        return {"logs": logs}
    except Exception as e:
        logger.error(f"Error retrieving logs: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving logs")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=Config.HOST,
        port=Config.PORT,
        reload=Config.DEBUG,
        log_level=Config.LOG_LEVEL.lower()
    )