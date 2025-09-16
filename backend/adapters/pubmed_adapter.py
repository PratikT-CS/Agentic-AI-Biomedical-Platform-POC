"""
PubMed API adapter for retrieving biomedical articles
"""

import requests
import xml.etree.ElementTree as ET
from typing import List, Dict, Optional
from loguru import logger
import time
from datetime import datetime

class PubMedAdapter:
    """Adapter for PubMed API integration"""
    
    def __init__(self):
        self.base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
        self.search_url = f"{self.base_url}esearch.fcgi"
        self.fetch_url = f"{self.base_url}efetch.fcgi"
        self.summary_url = f"{self.base_url}esummary.fcgi"
        self.db = "pubmed"
        self.retmax = 100  # Maximum results per request
        
    async def search_articles(self, query: str, max_results: int = 10) -> List[Dict]:
        """
        Search for articles in PubMed
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            
        Returns:
            List of article dictionaries
        """
        try:
            logger.info(f"Searching PubMed for: {query}")
            
            # Step 1: Search for PMIDs
            search_params = {
                "db": self.db,
                "term": query,
                "retmax": min(max_results, self.retmax),
                "retmode": "json",
                "sort": "relevance"
            }
            
            response = requests.get(self.search_url, params=search_params, timeout=30)
            response.raise_for_status()
            
            search_data = response.json()
            pmids = search_data.get("esearchresult", {}).get("idlist", [])
            
            if not pmids:
                logger.info("No articles found in PubMed")
                return []
            
            # Step 2: Fetch article details
            articles = await self._fetch_article_details(pmids[:max_results])
            
            logger.info(f"Retrieved {len(articles)} articles from PubMed")
            return articles
            
        except requests.exceptions.RequestException as e:
            logger.error(f"PubMed API request failed: {e}")
            raise Exception(f"PubMed API error: {e}")
        except Exception as e:
            logger.error(f"Error searching PubMed: {e}")
            raise
    
    async def _fetch_article_details(self, pmids: List[str]) -> List[Dict]:
        """Fetch detailed information for given PMIDs"""
        try:
            # Use esummary for faster retrieval of basic details
            summary_params = {
                "db": self.db,
                "id": ",".join(pmids),
                "retmode": "json"
            }
            
            response = requests.get(self.summary_url, params=summary_params, timeout=30)
            response.raise_for_status()
            
            summary_data = response.json()
            articles = []
            
            for pmid in pmids:
                if pmid in summary_data.get("result", {}):
                    article_data = summary_data["result"][pmid]
                    article = self._parse_article_summary(pmid, article_data)
                    articles.append(article)
            
            return articles
            
        except Exception as e:
            logger.error(f"Error fetching article details: {e}")
            # Fallback to basic information
            return [{"pmid": pmid, "title": "Details unavailable", "error": str(e)} for pmid in pmids]
    
    def _parse_article_summary(self, pmid: str, data: Dict) -> Dict:
        """Parse article summary data into standardized format"""
        try:
            return {
                "pmid": pmid,
                "title": data.get("title", "No title available"),
                "authors": self._parse_authors(data.get("authors", [])),
                "journal": data.get("source", "Unknown journal"),
                "publication_date": data.get("pubdate", "Unknown date"),
                "abstract": data.get("abstract", "No abstract available"),
                "doi": data.get("elocationid", ""),
                "pmc": data.get("pmc", ""),
                "mesh_terms": data.get("mesh", []),
                "keywords": data.get("keywords", []),
                "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                "source": "pubmed",
                "retrieved_at": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Error parsing article data for PMID {pmid}: {e}")
            return {
                "pmid": pmid,
                "title": "Parsing error",
                "error": str(e),
                "source": "pubmed"
            }
    
    def _parse_authors(self, authors_data: List[Dict]) -> List[str]:
        """Parse authors data into list of author names"""
        try:
            if not authors_data:
                return ["Unknown authors"]
            
            authors = []
            for author in authors_data:
                name_parts = []
                if author.get("name"):
                    name_parts.append(author["name"])
                elif author.get("lastname") or author.get("forename"):
                    if author.get("lastname"):
                        name_parts.append(author["lastname"])
                    if author.get("forename"):
                        name_parts.append(author["forename"])
                
                if name_parts:
                    authors.append(" ".join(name_parts))
            
            return authors if authors else ["Unknown authors"]
        except Exception as e:
            logger.error(f"Error parsing authors: {e}")
            return ["Unknown authors"]
    
    async def get_article_by_pmid(self, pmid: str) -> Optional[Dict]:
        """Get a specific article by PMID"""
        try:
            articles = await self._fetch_article_details([pmid])
            return articles[0] if articles else None
        except Exception as e:
            logger.error(f"Error retrieving article {pmid}: {e}")
            return None
    
    def get_source_info(self) -> Dict:
        """Get information about the PubMed data source"""
        return {
            "name": "PubMed",
            "description": "PubMed is a free search engine accessing primarily the MEDLINE database of references and abstracts on life sciences and biomedical topics",
            "url": "https://pubmed.ncbi.nlm.nih.gov/",
            "api_documentation": "https://www.ncbi.nlm.nih.gov/books/NBK25501/",
            "data_types": ["articles", "abstracts", "metadata"],
            "access_method": "api",
            "rate_limits": "3 requests per second without API key, 10 requests per second with API key"
        }