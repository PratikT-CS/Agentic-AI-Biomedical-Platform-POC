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
            print(search_data)
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
        """Fetch detailed information for given PMIDs including abstracts"""
        try:
            articles = []
            
            # Process PMIDs in batches to avoid API limits
            batch_size = 10
            for i in range(0, len(pmids), batch_size):
                batch_pmids = pmids[i:i + batch_size]
                
                # First get basic summary data
                summary_params = {
                    "db": self.db,
                    "id": ",".join(batch_pmids),
                    "retmode": "json"
                }
                
                summary_response = requests.get(self.summary_url, params=summary_params, timeout=30)
                summary_response.raise_for_status()
                summary_data = summary_response.json()
                
                # Then fetch detailed XML data including abstracts
                fetch_params = {
                    "db": self.db,
                    "id": ",".join(batch_pmids),
                    "retmode": "xml",
                    "rettype": "abstract"
                }
                
                fetch_response = requests.get(self.fetch_url, params=fetch_params, timeout=30)
                fetch_response.raise_for_status()
                
                # Parse XML data
                xml_data = fetch_response.text
                xml_articles = self._parse_xml_articles(xml_data)
                
                # Combine summary and XML data
                for pmid in batch_pmids:
                    if pmid in summary_data.get("result", {}):
                        summary_data_article = summary_data["result"][pmid]
                        xml_article = xml_articles.get(pmid, {})
                        article = self._parse_article_complete(pmid, summary_data_article, xml_article)
                        articles.append(article)
                
                # Add delay between batches to respect rate limits
                if i + batch_size < len(pmids):
                    time.sleep(0.5)
            
            return articles
            
        except Exception as e:
            logger.error(f"Error fetching article details: {e}")
            # Fallback to basic information
            return [{"pmid": pmid, "title": "Details unavailable", "error": str(e)} for pmid in pmids]
    
    def _parse_xml_articles(self, xml_data: str) -> Dict[str, Dict]:
        """Parse XML data from efetch to extract abstracts and other details"""
        try:
            root = ET.fromstring(xml_data)
            articles = {}
            
            for article in root.findall(".//PubmedArticle"):
                pmid_elem = article.find(".//PMID")
                if pmid_elem is not None:
                    pmid = pmid_elem.text
                    
                    # Extract abstract - handle both simple and structured abstracts
                    abstract_elems = article.findall(".//AbstractText")
                    abstract = ""
                    
                    if abstract_elems:
                        abstract_parts = []
                        
                        for abstract_elem in abstract_elems:
                            # First try structured abstract extraction for labeled sections
                            structured_text = self._extract_structured_abstract(abstract_elem)
                            
                            if structured_text:
                                abstract_parts.append(structured_text)
                            else:
                                # Use ET.tostring with method='text' to get all text content including nested elements
                                elem_text = ET.tostring(abstract_elem, method='text', encoding='unicode').strip()
                                
                                if elem_text:
                                    abstract_parts.append(elem_text)
                                else:
                                    # Fallback: manually extract text from element and children
                                    elem_parts = []
                                    
                                    # Check for direct text content
                                    if abstract_elem.text:
                                        elem_parts.append(abstract_elem.text.strip())
                                    
                                    # Check for text in child elements
                                    for child in abstract_elem.getchildren():
                                        if child.text:
                                            elem_parts.append(child.text.strip())
                                        # Also get tail text (text after the element)
                                        if child.tail:
                                            elem_parts.append(child.tail.strip())
                                    
                                    if elem_parts:
                                        abstract_parts.append(" ".join(elem_parts))
                        
                        # Join all abstract parts with double newline for better readability
                        abstract = "\n\n".join(abstract_parts)
                        
                        # Clean up any excessive whitespace
                        abstract = " ".join(abstract.split())
                    
                    # Extract keywords
                    keywords = []
                    for keyword in article.findall(".//Keyword"):
                        if keyword.text:
                            keywords.append(keyword.text.strip())
                    
                    # Extract MeSH terms
                    mesh_terms = []
                    for mesh in article.findall(".//MeshHeading/DescriptorName"):
                        if mesh.text:
                            mesh_terms.append(mesh.text.strip())
                    
                    articles[pmid] = {
                        "abstract": abstract,
                        "keywords": keywords,
                        "mesh_terms": mesh_terms
                    }
            return articles
            
        except Exception as e:
            logger.error(f"Error parsing XML data: {e}")
            return {}
    
    def _extract_structured_abstract(self, abstract_elem) -> str:
        """Extract text from structured abstracts with labeled sections"""
        try:
            abstract_parts = []
            
            # Handle labeled sections (Background, Methods, Results, etc.)
            for section in abstract_elem.findall(".//*"):
                section_text = ""
                
                # Get the label (if any)
                label = section.get("Label", "")
                if label:
                    section_text += f"{label}: "
                
                # Get the text content
                if section.text:
                    section_text += section.text.strip()
                
                # Get text from child elements
                for child in section.getchildren():
                    if child.text:
                        section_text += " " + child.text.strip()
                    if child.tail:
                        section_text += " " + child.tail.strip()
                
                if section_text.strip():
                    abstract_parts.append(section_text.strip())
            
            return " ".join(abstract_parts) if abstract_parts else ""
            
        except Exception as e:
            logger.error(f"Error extracting structured abstract: {e}")
            return ""
    
    def _parse_article_complete(self, pmid: str, summary_data: Dict, xml_data: Dict) -> Dict:
        """Parse complete article data combining summary and XML data"""
        try:
            return {
                "pmid": pmid,
                "title": summary_data.get("title", "No title available"),
                "authors": self._parse_authors(summary_data.get("authors", [])),
                "journal": summary_data.get("source", "Unknown journal"),
                "publication_date": summary_data.get("pubdate", "Unknown date"),
                "abstract": xml_data.get("abstract", "No abstract available"),
                "doi": summary_data.get("elocationid", ""),
                "pmc": summary_data.get("pmc", ""),
                "mesh_terms": xml_data.get("mesh_terms", []),
                "keywords": xml_data.get("keywords", []),
                "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                "source": "pubmed",
                "retrieved_at": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Error parsing complete article data for PMID {pmid}: {e}")
            return {
                "pmid": pmid,
                "title": "Parsing error",
                "error": str(e),
                "source": "pubmed"
            }
    
    def _parse_article_summary(self, pmid: str, data: Dict) -> Dict:
        """Parse article summary data into standardized format (legacy method)"""
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
        """Get a specific article by PMID with complete details including abstract"""
        try:
            articles = await self._fetch_article_details([pmid])
            return articles[0] if articles else None
        except Exception as e:
            logger.error(f"Error retrieving article {pmid}: {e}")
            return None
    
    async def get_abstract_by_pmid(self, pmid: str) -> Optional[str]:
        """Get only the abstract for a specific PMID (more efficient for just abstracts)"""
        try:
            fetch_params = {
                "db": self.db,
                "id": pmid,
                "retmode": "xml",
                "rettype": "abstract"
            }
            
            response = requests.get(self.fetch_url, params=fetch_params, timeout=30)
            response.raise_for_status()
            
            xml_data = response.text
            xml_articles = self._parse_xml_articles(xml_data)
            
            if pmid in xml_articles:
                return xml_articles[pmid].get("abstract", "No abstract available")
            
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving abstract for PMID {pmid}: {e}")
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