"""
AI Agent Orchestrator using LangChain for workflow coordination
"""

from langchain.agents import initialize_agent, AgentType
from langchain.tools import Tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, SystemMessage
from typing import List, Dict, Optional, Any
from loguru import logger
import asyncio
import json
from datetime import datetime

from adapters.pubmed_adapter import PubMedAdapter
from adapters.uniprot_adapter import UniProtAdapter
from adapters.swissadme_adapter import SwissADMEAdapter
from config import Config

class AIOrchestrator:
    """AI Agent for orchestrating biomedical research workflows"""
    
    def __init__(self):
        self.llm = None
        self.agent = None
        self.tools = []
        self.pubmed_adapter = PubMedAdapter()
        self.uniprot_adapter = UniProtAdapter()
        self.swissadme_adapter = SwissADMEAdapter()
        
    async def initialize(self):
        """Initialize the AI agent and tools"""
        try:
            # Validate configuration
            Config.validate_config()
            
            # Initialize LLM (using Google Gemini)
            self.llm = ChatGoogleGenerativeAI(
                model=Config.AI_MODEL,
                temperature=Config.AI_TEMPERATURE,
                max_output_tokens=Config.AI_MAX_TOKENS,
                google_api_key=Config.GEMINI_API_KEY
            )
            
            # Define tools for the agent
            self.tools = [
                Tool(
                    name="search_pubmed",
                    description="Search PubMed for biomedical articles. Input should be a search query string.",
                    func=self._search_pubmed_tool
                ),
                Tool(
                    name="search_uniprot",
                    description="Search UniProt for protein information. Input should be a protein name, gene name, or organism.",
                    func=self._search_uniprot_tool
                ),
                Tool(
                    name="search_swissadme",
                    description="Search SwissADME for drug properties. Input should be a SMILES notation of a drug molecule.",
                    func=self._search_swissadme_tool
                ),
                Tool(
                    name="synthesize_results",
                    description="Synthesize and analyze results from multiple biomedical sources. Input should be a JSON string of results.",
                    func=self._synthesize_results_tool
                )
            ]
            
            # Initialize the agent
            self.agent = initialize_agent(
                tools=self.tools,
                llm=self.llm,
                agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
                verbose=True,
                handle_parsing_errors=True
            )
            
            logger.info("AI Orchestrator initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing AI Orchestrator: {e}")
            raise
    
    def _search_pubmed_tool(self, query: str) -> str:
        """Tool function for PubMed search"""
        try:
            # Run async function in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            results = loop.run_until_complete(self.pubmed_adapter.search_articles(query, 5))
            loop.close()
            
            if results:
                return json.dumps({
                    "source": "pubmed",
                    "count": len(results),
                    "results": results[:3]  # Limit to first 3 for tool response
                })
            else:
                return json.dumps({"source": "pubmed", "count": 0, "message": "No articles found"})
                
        except Exception as e:
            logger.error(f"PubMed tool error: {e}")
            return json.dumps({"source": "pubmed", "error": str(e)})
    
    def _search_uniprot_tool(self, query: str) -> str:
        """Tool function for UniProt search"""
        try:
            # Run async function in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            results = loop.run_until_complete(self.uniprot_adapter.search_proteins(query, 5))
            loop.close()
            
            if results:
                return json.dumps({
                    "source": "uniprot",
                    "count": len(results),
                    "results": results[:3]  # Limit to first 3 for tool response
                })
            else:
                return json.dumps({"source": "uniprot", "count": 0, "message": "No proteins found"})
                
        except Exception as e:
            logger.error(f"UniProt tool error: {e}")
            return json.dumps({"source": "uniprot", "error": str(e)})
    
    def _search_swissadme_tool(self, smiles: str) -> str:
        """Tool function for SwissADME search"""
        try:
            # Run async function in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            results = loop.run_until_complete(self.swissadme_adapter.search_drug_properties(smiles))
            loop.close()
            
            if results:
                return json.dumps({
                    "source": "swissadme",
                    "count": len(results),
                    "results": results
                })
            else:
                return json.dumps({"source": "swissadme", "count": 0, "message": "No drug properties found"})
                
        except Exception as e:
            logger.error(f"SwissADME tool error: {e}")
            return json.dumps({"source": "swissadme", "error": str(e)})
    
    def _synthesize_results_tool(self, results_json: str) -> str:
        """Tool function for synthesizing results"""
        try:
            results = json.loads(results_json)
            
            # Create a synthesis prompt
            synthesis_prompt = f"""
            Analyze and synthesize the following biomedical research results:
            
            {results_json}
            
            Provide:
            1. Key findings summary
            2. Connections between different data sources
            3. Potential research implications
            4. Recommendations for further investigation
            
            Keep the response concise and focused on actionable insights.
            """
            
            # Use LLM to synthesize results
            messages = [
                SystemMessage(content="You are a biomedical research assistant. Analyze and synthesize research data from multiple sources."),
                HumanMessage(content=synthesis_prompt)
            ]
            
            response = self.llm(messages)
            return response.content
            
        except Exception as e:
            logger.error(f"Synthesis tool error: {e}")
            return f"Error synthesizing results: {str(e)}"
    
    async def process_query(self, query: str, sources: List[str], max_results: int = 10) -> Dict:
        """
        Process a biomedical research query using AI orchestration
        
        Args:
            query: The research query
            sources: List of data sources to query
            max_results: Maximum results per source
            
        Returns:
            Dictionary containing orchestrated results
        """
        try:
            logger.info(f"Processing query with AI orchestration: {query}")
            
            # Create a comprehensive prompt for the agent
            agent_prompt = f"""
            You are a biomedical research assistant. The user has asked: "{query}"
            
            Available data sources: {', '.join(sources)}
            
            Please:
            1. Search relevant data sources based on the query
            2. Analyze the results
            3. Synthesize findings from multiple sources
            4. Provide actionable insights and recommendations
            
            Focus on finding connections between different types of biomedical data.
            """
            
            # Execute the agent
            if self.agent:
                result = self.agent.run(agent_prompt)
            else:
                # Fallback to direct tool usage
                result = await self._fallback_processing(query, sources, max_results)
            
            return {
                "query": query,
                "sources_queried": sources,
                "ai_analysis": result,
                "timestamp": datetime.utcnow().isoformat(),
                "orchestration_method": "AI Agent"
            }
            
        except Exception as e:
            logger.error(f"Error in AI orchestration: {e}")
            # Fallback to direct processing
            return await self._fallback_processing(query, sources, max_results)
    
    async def _fallback_processing(self, query: str, sources: List[str], max_results: int) -> Dict:
        """Fallback processing when AI agent is not available"""
        try:
            results = {}
            
            # Query each source directly
            if "pubmed" in sources:
                try:
                    pubmed_results = await self.pubmed_adapter.search_articles(query, max_results)
                    results["pubmed"] = pubmed_results
                except Exception as e:
                    results["pubmed"] = {"error": str(e)}
            
            if "uniprot" in sources:
                try:
                    uniprot_results = await self.uniprot_adapter.search_proteins(query, max_results)
                    results["uniprot"] = uniprot_results
                except Exception as e:
                    results["uniprot"] = {"error": str(e)}
            
            if "swissadme" in sources:
                try:
                    # For SwissADME, we need SMILES notation
                    # This is a simplified approach - in practice, you'd convert the query to SMILES
                    smiles_query = "CCO"  # Placeholder
                    swissadme_results = await self.swissadme_adapter.search_drug_properties(query)
                    results["swissadme"] = swissadme_results
                except Exception as e:
                    results["swissadme"] = {"error": str(e)}
            
            return {
                "query": query,
                "sources_queried": sources,
                "results": results,
                "timestamp": datetime.utcnow().isoformat(),
                "orchestration_method": "Direct"
            }
            
        except Exception as e:
            logger.error(f"Error in fallback processing: {e}")
            return {
                "query": query,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
                "orchestration_method": "error"
            }
    
    async def cleanup(self):
        """Cleanup resources"""
        try:
            if self.swissadme_adapter:
                self.swissadme_adapter.cleanup()
            logger.info("AI Orchestrator cleaned up")
        except Exception as e:
            logger.error(f"Error cleaning up AI Orchestrator: {e}")
