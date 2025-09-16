"""
UniProt API adapter for retrieving protein data
"""

import requests
import json
from typing import List, Dict, Any, Optional
from loguru import logger
import time
from datetime import datetime

class UniProtAdapter:
    """Adapter for UniProt API integration"""
    
    def __init__(self):
        self.base_url = "https://rest.uniprot.org"
        self.search_url = f"{self.base_url}/uniprotkb/search"
        self.retrieve_url = f"{self.base_url}/uniprotkb"
        self.max_results = 100
        
    async def search_proteins(self, query: str, max_results: int = 10) -> List[Dict]:
        """
        Search for proteins in UniProt
        
        Args:
            query: Search query string (can be protein name, gene name, organism, etc.)
            max_results: Maximum number of results to return
            
        Returns:
            List of protein dictionaries
        """
        try:
            logger.info(f"Searching UniProt for: {query}")
            
            # Construct search parameters
            search_params = {
                "query": query,
                "size": min(max_results, self.max_results),
                "format": "json",
                # "fields": "accession,id,protein_name,organism_name,gene_names,sequence,length,mass,ec,go,feature_count,reviewed"
            }
            
            response = requests.get(self.search_url, params=search_params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            proteins = []
            
            for result in data.get("results", []):
                protein = self._parse_protein_data(result)
                proteins.append(protein)
            
            logger.info(f"Retrieved {len(proteins)} proteins from UniProt")
            return proteins
            
        except requests.exceptions.RequestException as e:
            logger.error(f"UniProt API request failed: {e}")
            raise Exception(f"UniProt API error: {e}")
        except Exception as e:
            logger.error(f"Error searching UniProt: {e}")
            raise
    
    @staticmethod
    def _safe_get(obj: Any, path: list, default: Any = None) -> Any:
        """Safely traverse nested dicts/lists with type checking"""
        for key in path:
            if isinstance(obj, dict):
                obj = obj.get(key, default)
            elif isinstance(obj, list) and isinstance(key, int) and key < len(obj):
                obj = obj[key]
            else:
                return default
        return obj

    def _parse_protein_data(self, data: Dict) -> Dict:
        """Parse UniProt protein JSON into standardized format"""
        try:
            protein = {
                "accession": data.get("primaryAccession", ""),
                "id": data.get("uniProtkbId", ""),
                "protein_name": UniProtAdapter._safe_get(
                    data, ["proteinDescription", "recommendedName", "fullName", "value"], "Unknown protein"
                ),
                "organism": UniProtAdapter._safe_get(data, ["organism", "scientificName"], "Unknown organism"),
                "organism_id": UniProtAdapter._safe_get(data, ["organism", "taxonId"], ""),
                "gene_names": self._extract_gene_names(data.get("genes", [])),
                "sequence": UniProtAdapter._safe_get(data, ["sequence", "value"], ""),
                "sequence_length": UniProtAdapter._safe_get(data, ["sequence", "length"], 0),
                "molecular_weight": UniProtAdapter._safe_get(data, ["sequence", "molWeight"], 0),
                "ec_numbers": self._extract_ec_numbers(
                    UniProtAdapter._safe_get(data, ["proteinDescription", "recommendedName", "ecNumbers"], [])
                ),
                "go_terms": self._extract_go_terms(data.get("uniProtKBCrossReferences", [])),
                "keywords": [kw.get("name", "") for kw in data.get("keywords", []) if isinstance(kw, dict)],
                "feature_count": len(data.get("features", [])) if isinstance(data.get("features", []), list) else 0,
                "reviewed": data.get("entryType") == "UniProtKB reviewed (Swiss-Prot)",
                "url": f"https://www.uniprot.org/uniprotkb/{data.get('primaryAccession', '')}",
                "source": "uniprot",
                "retrieved_at": datetime.utcnow().isoformat()
            }
            return protein

        except Exception as e:
            logger.error(f"Error parsing protein data: {e}")
            return {
                "accession": data.get("primaryAccession", "Unknown"),
                "protein_name": "Parsing error",
                "error": str(e),
                "source": "uniprot"
            }

    def _extract_gene_names(self, genes_data: List[Dict]) -> List[str]:
        """Extract gene names"""
        gene_names = []
        for gene in genes_data:
            if isinstance(gene.get("geneName"), dict):
                val = gene["geneName"].get("value")
                if val:
                    gene_names.append(val)
        return gene_names

    def _extract_ec_numbers(self, ec_numbers_data: List[Dict]) -> List[str]:
        """Extract EC numbers"""
        ec_numbers = []
        for ec in ec_numbers_data:
            if isinstance(ec, dict) and ec.get("value"):
                ec_numbers.append(ec["value"])
        return ec_numbers

    def _extract_go_terms(self, cross_refs: List[Dict]) -> List[Dict]:
        """Extract GO terms"""
        go_terms = []
        for ref in cross_refs:
            if ref.get("database") == "GO":
                go_term = {
                    "id": ref.get("id", ""),
                    "properties": ref.get("properties", [])
                }
                go_terms.append(go_term)
        return go_terms
    def get_source_info(self) -> Dict:
        """Get information about the UniProt data source"""
        return {
            "name": "UniProt",
            "description": "UniProt is a comprehensive, high-quality and freely accessible resource of protein sequence and functional information",
            "url": "https://www.uniprot.org/",
            "api_documentation": "https://www.uniprot.org/help/api",
            "data_types": ["proteins", "sequences", "functional_annotations", "cross_references"],
            "access_method": "api",
            "rate_limits": "No official rate limits, but reasonable usage is expected"
        }
