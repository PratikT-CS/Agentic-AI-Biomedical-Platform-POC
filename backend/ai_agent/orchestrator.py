"""
AI Agent Orchestrator using LangGraph ReAct Agent with tools
"""

from typing import List, Dict, Optional, Any
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from loguru import logger
import asyncio
import json
from datetime import datetime
import requests

from adapters.pubmed_adapter import PubMedAdapter
from adapters.uniprot_adapter import UniProtAdapter
from adapters.swissadme_adapter import SwissADMEAdapter
from config import Config


class AIOrchestrator:
    """AI Agent for orchestrating biomedical research workflows using LangGraph ReAct Agent"""
    
    def __init__(self):
        self.llm = None
        self.agent = None
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
                # max_output_tokens=Config.AI_MAX_TOKENS,
                google_api_key=Config.GEMINI_API_KEY
            )
            
            # Create tools from adapters
            tools = self._create_tools()
            
            # Create ReAct agent
            self.agent = create_react_agent(
                model=self.llm,
                tools=tools
            )
            
            logger.info("AI Orchestrator with ReAct Agent initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing AI Orchestrator: {e}")
            raise
    
    def _create_tools(self) -> List:
        """Create tools from the adapters"""
        
        @tool
        def search_pubmed(query: str, max_results: int = 10) -> str:
            """
            Search PubMed for biomedical articles and research papers.
            
            Args:
                query: Search query string (e.g., "COVID-19 treatment", "protein structure")
                max_results: Maximum number of results to return (default: 10)
            
            Returns:
                JSON string containing article information including titles, authors, abstracts, and metadata
            """
            try:
                # Run async function in sync context
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                results = loop.run_until_complete(self.pubmed_adapter.search_articles(query, max_results))
                loop.close()
                
                if results:
                    return json.dumps({
                        "source": "pubmed",
                        "count": len(results),
                        "query": query,
                        "results": results,
                        "timestamp": datetime.utcnow().isoformat()
                    })
                else:
                    return json.dumps({
                        "source": "pubmed", 
                        "count": 0, 
                        "query": query,
                        "message": "No articles found",
                        "timestamp": datetime.utcnow().isoformat()
                    })
                    
            except Exception as e:
                logger.error(f"PubMed search error: {e}")
                return json.dumps({
                    "source": "pubmed",
                    "error": str(e),
                    "query": query,
                    "timestamp": datetime.utcnow().isoformat()
                })
        
        @tool
        def search_uniprot(query: str, max_results: int = 10) -> str:
            """
            Search UniProt for protein information, sequences, and functional annotations.
            
            Args:
                query: Search query string (e.g., "insulin", "BRCA1", "Homo sapiens")
                max_results: Maximum number of results to return (default: 10)
            
            Returns:
                JSON string containing protein information including sequences, functions, and annotations
            """
            try:
                # Run async function in sync context
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                results = loop.run_until_complete(self.uniprot_adapter.search_proteins(query, max_results))
                loop.close()
                
                if results:
                    return json.dumps({
                        "source": "uniprot",
                        "count": len(results),
                        "query": query,
                        "results": results,
                        "timestamp": datetime.utcnow().isoformat()
                    })
                else:
                    return json.dumps({
                        "source": "uniprot",
                        "count": 0,
                        "query": query,
                        "message": "No proteins found",
                        "timestamp": datetime.utcnow().isoformat()
                    })
                    
            except Exception as e:
                logger.error(f"UniProt search error: {e}")
                return json.dumps({
                    "source": "uniprot",
                    "error": str(e),
                    "query": query,
                    "timestamp": datetime.utcnow().isoformat()
                })
        
        @tool
        def search_swissadme(smiles: str) -> str:
            """
            Analyze drug properties and ADME characteristics using SwissADME.
            
            Args:
                smiles: SMILES notation of the drug molecule (e.g., "CCO" for ethanol)
            
            Returns:
                JSON string containing drug properties, ADME predictions, and drug-likeness analysis
            """
            try:
                # Run async function in sync context
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                results = loop.run_until_complete(self.swissadme_adapter.search_drug_properties(smiles))
                loop.close()
                
                if results:
                    return json.dumps({
                        "source": "swissadme",
                        "count": len(results) if isinstance(results, list) else 1,
                        "smiles": smiles,
                        "results": results,
                        "timestamp": datetime.utcnow().isoformat()
                    })
                else:
                    return json.dumps({
                        "source": "swissadme",
                        "count": 0,
                        "smiles": smiles,
                        "message": "No drug properties found",
                        "timestamp": datetime.utcnow().isoformat()
                    })
                    
            except Exception as e:
                logger.error(f"SwissADME search error: {e}")
                return json.dumps({
                    "source": "swissadme",
                    "error": str(e),
                    "smiles": smiles,
                    "timestamp": datetime.utcnow().isoformat()
                })
                
        @tool
        def search_smiles_string(molecule: str) -> str:
            """
            Get valid SMILES string for a given molecule name from the authenticated database.
            
            Args:
                molecule: valid molecule name for finding it's SMILES string from PubChem database (e.g., "aspirin", "olaparib").
                
            Returns:
                SMILES string fethed from the database. 
            """
            # Input validation
            if not molecule or not isinstance(molecule, str):
                logger.error("Invalid molecule name provided")
                return ""
            
            molecule = molecule.strip()
            if not molecule:
                logger.error("Empty molecule name after stripping")
                return ""
            
            try:
                result = requests.get(
                    f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{molecule}/property/CanonicalSMILES/TXT",
                    timeout=30
                )
                
                if result.status_code == 200:
                    smiles = result.text.strip()
                    if smiles:
                        logger.info(f"Successfully retrieved SMILES for {molecule}: {smiles}")
                        return smiles
                    else:
                        logger.warning(f"Empty SMILES response for molecule: {molecule}")
                        return ""
                elif result.status_code == 404:
                    logger.warning(f"Molecule not found in PubChem: {molecule}")
                    return ""
                else:
                    logger.error(f"PubChem API error for {molecule}: HTTP {result.status_code} - {result.text}")
                    return ""
                
            except requests.exceptions.Timeout:
                logger.error(f"Timeout while fetching SMILES for {molecule}")
                return ""
            except requests.exceptions.ConnectionError:
                logger.error(f"Connection error while fetching SMILES for {molecule}")
                return ""
            except requests.exceptions.RequestException as e:
                logger.error(f"Request error while fetching SMILES for {molecule}: {e}")
                return ""
            except Exception as e:
                logger.error(f"Unexpected error while fetching SMILES for {molecule}: {e}")
                return ""
        
        @tool
        def synthesize_biomedical_data(results_json: str) -> str:
            """
            Synthesize and analyze results from multiple biomedical data sources.
            
            Args:
                results_json: JSON string containing results from multiple sources
            
            Returns:
                Comprehensive analysis and synthesis of the biomedical data
            """
            try:
                results = json.loads(results_json)
                
                if results["results"]["swissadme"]:
                    del results["rsults"]["swissadme"]["images"]
                    del results["rsults"]["swissadme"]["boiled_egg_plot"]
                
                results = json.dumps(results)
                
                # Create a synthesis prompt
                synthesis_prompt = f"""
                Analyze and synthesize the following biomedical research results:
                
                {results}
                
                Provide a comprehensive analysis including:
                1. Key findings summary from each data source
                2. Connections and relationships between different types of data
                3. Potential research implications and insights
                4. Recommendations for further investigation
                5. Overall assessment of the research landscape
                
                Focus on actionable insights and make connections between different data sources.
                Keep the analysis structured and evidence-based.
                """
                
                # Use LLM to synthesize results
                messages = [
                    SystemMessage(content="You are a biomedical research assistant. Analyze and synthesize research data from multiple sources to provide comprehensive insights."),
                    HumanMessage(content=synthesis_prompt)
                ]
                
                response = self.llm.invoke(messages)
                return response.content
                
            except Exception as e:
                logger.error(f"Synthesis error: {e}")
                return f"Error synthesizing results: {str(e)}"
        
        return [search_pubmed, search_uniprot, search_swissadme, search_smiles_string, synthesize_biomedical_data]
    
    def _extract_tool_results(self, messages: List) -> Dict:
        """
        Extract individual results from tool calls in agent messages
        
        Args:
            messages: List of messages from the agent execution
            
        Returns:
            Dictionary containing results from each source
        """
        try:
            results = {}
            
            for message in messages:
                # Check if this is a tool message with results
                # LangGraph uses different message types, let's check for tool messages
                if hasattr(message, 'type'):
                    if message.type == 'tool' or message.type == 'ToolMessage':
                        try:
                            # Parse the tool result
                            tool_result = json.loads(message.content)
                            source = tool_result.get('source')
                            
                            if source and source in ['pubmed', 'uniprot', 'swissadme']:
                                # Extract the actual results from the tool response
                                if 'results' in tool_result:
                                    results[source] = tool_result['results']
                                elif 'error' in tool_result:
                                    results[source] = {"error": tool_result['error']}
                                else:
                                    results[source] = {"message": tool_result.get('message', 'No results found')}
                                    
                        except (json.JSONDecodeError, KeyError) as e:
                            logger.warning(f"Could not parse tool result: {e}")
                            continue
                
                # Also check for AIMessage with tool calls
                elif hasattr(message, 'tool_calls') and message.tool_calls:
                    # This is an AI message that made tool calls, skip for now
                    continue
                
                # Check if message content contains tool results (fallback)
                elif hasattr(message, 'content') and isinstance(message.content, str):
                    try:
                        # Try to parse as JSON to see if it's a tool result
                        tool_result = json.loads(message.content)
                        if isinstance(tool_result, dict) and 'source' in tool_result:
                            source = tool_result.get('source')
                            if source and source in ['pubmed', 'uniprot', 'swissadme']:
                                if 'results' in tool_result:
                                    results[source] = tool_result['results']
                                elif 'error' in tool_result:
                                    results[source] = {"error": tool_result['error']}
                                else:
                                    results[source] = {"message": tool_result.get('message', 'No results found')}
                    except (json.JSONDecodeError, KeyError):
                        # Not a tool result, continue
                        continue
            
            return results
            
        except Exception as e:
            logger.error(f"Error extracting tool results: {e}")
            return {}
    
    async def process_query(self, query: str, sources: List[str], max_results: int = 10) -> Dict:
        """
        Process a biomedical research query using ReAct agent
        
        Args:
            query: The research query
            sources: List of data sources to query (used for context, agent decides which to use)
            max_results: Maximum results per source
            
        Returns:
            Dictionary containing orchestrated results
        """
        try:
            logger.info(f"Processing query with ReAct agent: {query}")
            
            # Create a comprehensive prompt for the agent
            system_message = SystemMessage(content="""
You are a specialized biomedical research assistant with access to three powerful scientific databases. Your role is to conduct comprehensive research by integrating information from multiple sources to provide meaningful insights for biomedical questions.

## Available Tools

### 1. PubMed Search (`search_pubmed`)
- **Purpose**: Find recent research papers, clinical studies, and scientific articles
- **Best for**: Literature reviews, disease mechanisms, treatment outcomes, epidemiological data
- **Use when**: Need peer-reviewed evidence, recent discoveries, clinical trial results

### 2. UniProt Database (`search_uniprot`)
- **Purpose**: Retrieve detailed protein information including sequences, functions, and interactions
- **Best for**: Protein characterization, pathway analysis, structural information, gene ontology
- **Use when**: Need protein-specific data, functional annotations, molecular interactions

### 3. Valid SMILES string search (`search_smiles_string`)
- **Purpose**: Retrieve valid FDA approved SMILES string for molecule name (e.g., for 'aspirin', 'olaparib')
- **Use when**: Getting valid SMILES string for molecule to analyze using SwissADME tool

### 4. SwissADME Analysis (`search_swissadme`)
- **Purpose**: Predict ADME properties and drug-likeness of chemical compounds
- **Best for**: Drug development, pharmacokinetic predictions, toxicity screening
- **Use when**: Evaluating therapeutic potential, optimizing drug candidates, assessing bioavailability
- **Note**: You can call this tool for multiple SMILES strings at once by providing a comma-separated list (e.g., `CCO, CC`).

## Research Methodology

### For Each Query:
1. **Analyze the question** to determine which databases are most relevant.
2. **Query databases strategically** – start broad, then narrow down using filters (e.g., MeSH terms, clinical trial phase).
3. **Cross-reference information** between sources to identify mechanistic links (e.g., how drug ADME properties relate to protein targets and clinical outcomes).
4. **Differentiate evidence types** – separate preclinical, clinical trial, and review/meta-analysis findings.
5. **Integrate computational predictions with real-world data** – compare SwissADME predictions with reported pharmacokinetic or clinical observations.
6. **Synthesize findings** into coherent, actionable insights.

### Query Optimization:
- **PubMed**: Use MeSH terms, combine disease + protein/pathway names, and include filters for clinical trial phases or systematic reviews when relevant.
- **UniProt**: Search by protein names, gene symbols, UniProt IDs, and extract functional domains, binding motifs, post-translational modifications, and disease associations.
- **SwissADME**: Input SMILES strings from validated drug databases; report Lipinski’s Rule of Five, PAINS alerts, solubility, GI absorption, BBB penetration, CYP inhibition, and bioavailability scores.

## Output Structure

Always provide:

1. **Executive Summary** (2–3 sentences highlighting the most important insights)

2. **Detailed Analysis** organized by:
   - **Literature Evidence (PubMed findings)**: Include recent and high-quality evidence, clinical trial phases, and systematic reviews.
   - **Molecular Details (UniProt data)**: Report UniProt IDs, functions, pathways, structural domains, and known drug-binding sites.
   - **Drug/Compound Assessment (SwissADME results)**: Include all key ADME metrics, drug-likeness filters (e.g., Lipinski, PAINS), and note computational vs. clinical pharmacokinetics.

3. **Cross-Database Insights** showing mechanistic connections between:
   - Literature findings and protein targets
   - Protein functional domains and drug-binding sites
   - ADME predictions and observed clinical outcomes

4. **Research Gaps & Future Directions**: Highlight limitations in current knowledge, resistance mechanisms, translational challenges, or next-generation therapeutic strategies.

5. **Methodology Notes**: Explain your search strategy, filtering criteria, and limitations (e.g., predictive vs experimental data).

## Response Guidelines

- **Be scientifically rigorous** – cite specific PMIDs, UniProt IDs, compound names, and SMILES strings.
- **Quantify when possible** – include IC50/EC50 values, hazard ratios, survival outcomes, and clinical trial identifiers.
- **Flag uncertainties** – note conflicting evidence, predictive vs experimental discrepancies, or incomplete datasets.
- **Suggest follow-up research** – propose experiments, trials, or additional database queries.
- **Use precise scientific terminology** while remaining accessible to biomedical researchers.

## Quality Standards

- Prioritize **recent publications (last 5 years)** unless historical context is necessary.
- Report **systematic reviews/meta-analyses** where available.
- Verify protein information across multiple UniProt entries, including domains and disease associations.
- Cross-check **SwissADME predictions** with published pharmacokinetic or clinical trial data when available.
- Always provide specific identifiers (PMIDs, UniProt IDs, trial numbers) for reproducibility.
- Acknowledge limitations in predictions, literature coverage, or available evidence.

Remember: Your goal is to provide **comprehensive, evidence-based, and mechanistically connected insights** that advance biomedical understanding and support decision-making.
""")
            
            user_prompt = f"""
            The user has asked: "{query}"
            
            Available data sources: {', '.join(sources)}
            Maximum results per source: {max_results}
            
            Please:
            1. Analyze the query to determine which data sources are most relevant
            2. Use the appropriate tools to search for information
            3. Synthesize the results from multiple sources if relevant
            4. Provide comprehensive insights and recommendations
            
            Focus on finding connections between different types of biomedical data and provide actionable insights.
            """
            
            # Execute the agent
            if self.agent:
                # Create the input for the agent
                agent_input = {
                    "messages": [system_message, HumanMessage(content=user_prompt)]
                }
                
                # Run the agent
                result = await self.agent.ainvoke(agent_input)
                
                # Extract the final message from the agent
                final_message = result["messages"][-1].content if result["messages"] else "No response generated"
                
                # Extract individual results from tool calls
                individual_results = self._extract_tool_results(result["messages"])
                
                # Debug: Log message structure for troubleshooting
                logger.info(f"Agent execution completed with {len(result['messages'])} messages")
                for i, msg in enumerate(result["messages"]):
                    logger.debug(f"Message {i}: type={getattr(msg, 'type', 'unknown')}, content_length={len(str(getattr(msg, 'content', '')))}")
                
                return {
                    "query": query,
                    "sources_queried": sources,
                    "results": individual_results,
                    "ai_analysis": final_message,
                    "timestamp": datetime.utcnow().isoformat(),
                    "orchestration_method": "Agent",
                    "workflow_status": "completed"
                }
            else:
                raise Exception("ReAct agent not initialized")
            
        except Exception as e:
            logger.error(f"Error in ReAct agent processing: {e}")
            return {
                "query": query,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
                "orchestration_method": "LangGraph ReAct Agent",
                "workflow_status": "error"
            }
    
    async def cleanup(self):
        """Cleanup resources"""
        try:
            if self.swissadme_adapter:
                self.swissadme_adapter.cleanup()
            logger.info("AI Orchestrator cleaned up")
        except Exception as e:
            logger.error(f"Error cleaning up AI Orchestrator: {e}")