# """
# SwissADME web scraping adapter for drug property predictions
# """

# import requests
# from bs4 import BeautifulSoup
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.chrome.options import Options
# from selenium.common.exceptions import TimeoutException, WebDriverException
# from typing import List, Dict, Optional
# from loguru import logger
# import time
# import re
# from datetime import datetime

# class SwissADMEAdapter:
#     """Adapter for SwissADME web scraping"""
    
#     def __init__(self):
#         self.base_url = "http://www.swissadme.ch/"
#         self.search_url = f"{self.base_url}index.php"
#         self.driver = None
#         self.setup_driver()
        
#     def setup_driver(self):
#         """Setup Chrome driver with headless options"""
#         try:
#             chrome_options = Options()
#             chrome_options.add_argument("--headless")
#             chrome_options.add_argument("--no-sandbox")
#             chrome_options.add_argument("--disable-dev-shm-usage")
#             chrome_options.add_argument("--disable-gpu")
#             chrome_options.add_argument("--window-size=1920,1080")
#             chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
            
#             self.driver = webdriver.Chrome(options=chrome_options)
#             self.driver.set_page_load_timeout(30)
#             logger.info("Chrome driver initialized successfully")
            
#         except Exception as e:
#             logger.error(f"Failed to initialize Chrome driver: {e}")
#             self.driver = None
    
#     async def search_drug_properties(self, smiles: str, max_results: int = 10) -> List[Dict]:
#         """
#         Search for drug properties using SMILES notation
        
#         Args:
#             smiles: SMILES notation of the drug molecule
#             max_results: Maximum number of results to return (not applicable for single molecule)
            
#         Returns:
#             List containing drug property dictionary
#         """
#         try:
#             if not self.driver:
#                 raise Exception("Web driver not initialized")
            
#             logger.info(f"Searching SwissADME for SMILES: {smiles[:50]}...")
            
#             # Navigate to SwissADME
#             self.driver.get(self.search_url)
            
#             # Wait for page to load
#             wait = WebDriverWait(self.driver, 10)
            
#             # Find and fill the SMILES input field
#             smiles_input = wait.until(
#                 EC.presence_of_element_located((By.NAME, "smiles"))
#             )
#             smiles_input.clear()
#             # smiles_input.send_keys(smiles)
#             smiles_input.send_keys("c1ccccc1Oc1ccccc1")
            
#             # Submit the form using the correct button selector
#             submit_button = wait.until(
#                 EC.element_to_be_clickable((By.ID, "submitButton"))
#             )
#             submit_button.click()
            
#             # Wait for results to load
#             time.sleep(60)
            
#             # Parse the results
#             drug_properties = self._parse_results_page()
            
#             logger.info(f"Retrieved drug properties from SwissADME")
#             return [drug_properties] if drug_properties else []
            
#         except TimeoutException:
#             logger.error("Timeout while waiting for SwissADME page to load")
#             raise Exception("SwissADME request timeout")
#         except WebDriverException as e:
#             logger.error(f"WebDriver error: {e}")
#             raise Exception(f"SwissADME web scraping error: {e}")
#         except Exception as e:
#             logger.error(f"Error searching SwissADME: {e}")
#             raise
    
#     def _parse_results_page(self) -> Optional[Dict]:
#         """Parse the SwissADME results page"""
#         try:
#             # Get page source
#             page_source = self.driver.page_source
#             soup = BeautifulSoup(page_source, 'html.parser')
            
#             # Initialize result dictionary
#             drug_properties = {
#                 "smiles": "",
#                 "molecular_properties": {},
#                 "adme_properties": {},
#                 "drug_likeness": {},
#                 "medicinal_chemistry": {},
#                 "source": "swissadme",
#                 "retrieved_at": datetime.utcnow().isoformat()
#             }
            
#             # Extract molecular properties
#             drug_properties["molecular_properties"] = self._extract_molecular_properties(soup)
            
#             # Extract ADME properties
#             drug_properties["adme_properties"] = self._extract_adme_properties(soup)
            
#             # Extract drug likeness
#             drug_properties["drug_likeness"] = self._extract_drug_likeness(soup)
            
#             # Extract medicinal chemistry properties
#             drug_properties["medicinal_chemistry"] = self._extract_medicinal_chemistry(soup)
            
#             return drug_properties
            
#         except Exception as e:
#             logger.error(f"Error parsing SwissADME results: {e}")
#             return None
    
#     def _extract_molecular_properties(self, soup: BeautifulSoup) -> Dict:
#         """Extract molecular properties from the results page"""
#         properties = {}
        
#         try:
#             # Look for molecular properties table
#             tables = soup.find_all('table')
#             for table in tables:
#                 rows = table.find_all('tr')
#                 for row in rows:
#                     cells = row.find_all(['td', 'th'])
#                     if len(cells) >= 2:
#                         key = cells[0].get_text(strip=True)
#                         value = cells[1].get_text(strip=True)
#                         if key and value:
#                             properties[key] = value
#         except Exception as e:
#             logger.error(f"Error extracting molecular properties: {e}")
        
#         return properties
    
#     def _extract_adme_properties(self, soup: BeautifulSoup) -> Dict:
#         """Extract ADME properties from the results page"""
#         properties = {}
        
#         try:
#             # Look for ADME-related content
#             # This is a simplified extraction - in practice, you'd need to identify
#             # the specific sections and tables containing ADME data
#             adme_sections = soup.find_all(text=re.compile(r'ADME|Absorption|Distribution|Metabolism|Excretion', re.I))
            
#             for section in adme_sections:
#                 parent = section.parent
#                 if parent:
#                     # Extract nearby data
#                     tables = parent.find_next_siblings('table')
#                     for table in tables:
#                         rows = table.find_all('tr')
#                         for row in rows:
#                             cells = row.find_all(['td', 'th'])
#                             if len(cells) >= 2:
#                                 key = cells[0].get_text(strip=True)
#                                 value = cells[1].get_text(strip=True)
#                                 if key and value:
#                                     properties[key] = value
#         except Exception as e:
#             logger.error(f"Error extracting ADME properties: {e}")
        
#         return properties
    
#     def _extract_drug_likeness(self, soup: BeautifulSoup) -> Dict:
#         """Extract drug likeness properties"""
#         properties = {}
        
#         try:
#             # Look for drug likeness indicators
#             drug_likeness_indicators = [
#                 'Lipinski', 'Veber', 'Egan', 'Muegge', 'Bioavailability Score'
#             ]
            
#             for indicator in drug_likeness_indicators:
#                 elements = soup.find_all(text=re.compile(indicator, re.I))
#                 for element in elements:
#                     parent = element.parent
#                     if parent:
#                         # Extract the value or status
#                         value_element = parent.find_next_sibling()
#                         if value_element:
#                             properties[indicator] = value_element.get_text(strip=True)
#         except Exception as e:
#             logger.error(f"Error extracting drug likeness: {e}")
        
#         return properties
    
#     def _extract_medicinal_chemistry(self, soup: BeautifulSoup) -> Dict:
#         """Extract medicinal chemistry properties"""
#         properties = {}
        
#         try:
#             # Look for medicinal chemistry related content
#             medchem_terms = [
#                 'PAINS', 'Brenk', 'Lead-likeness', 'Synthetic accessibility'
#             ]
            
#             for term in medchem_terms:
#                 elements = soup.find_all(text=re.compile(term, re.I))
#                 for element in elements:
#                     parent = element.parent
#                     if parent:
#                         value_element = parent.find_next_sibling()
#                         if value_element:
#                             properties[term] = value_element.get_text(strip=True)
#         except Exception as e:
#             logger.error(f"Error extracting medicinal chemistry properties: {e}")
        
#         return properties
    
#     async def search_by_drug_name(self, drug_name: str) -> List[Dict]:
#         """
#         Search for drug properties by drug name (requires SMILES conversion)
#         Note: This is a simplified implementation. In practice, you'd need
#         to convert drug names to SMILES first using another service.
#         """
#         try:
#             # For demonstration, we'll use a placeholder SMILES
#             # In a real implementation, you'd use a chemical name to SMILES converter
#             placeholder_smiles = "c1ccccc1Oc1ccccc1"  # Ethanol as placeholder
            
#             logger.warning(f"Drug name search not fully implemented. Using placeholder SMILES for: {drug_name}")
#             return await self.search_drug_properties(placeholder_smiles)
            
#         except Exception as e:
#             logger.error(f"Error searching by drug name: {e}")
#             raise
    
#     def cleanup(self):
#         """Clean up the web driver"""
#         if self.driver:
#             try:
#                 self.driver.quit()
#                 logger.info("Web driver cleaned up")
#             except Exception as e:
#                 logger.error(f"Error cleaning up web driver: {e}")
    
#     def get_source_info(self) -> Dict:
#         """Get information about the SwissADME data source"""
#         return {
#             "name": "SwissADME",
#             "description": "SwissADME is a free web tool to evaluate pharmacokinetics, drug-likeness and medicinal chemistry friendliness of small molecules",
#             "url": "http://www.swissadme.ch/",
#             "api_documentation": "Not available - web scraping required",
#             "data_types": ["drug_properties", "adme_predictions", "drug_likeness", "medicinal_chemistry"],
#             "access_method": "web_scraping",
#             "rate_limits": "No official limits, but reasonable usage expected",
#             "requirements": "SMILES notation input required"
#         }

"""
SwissADME web scraping adapter for drug property predictions
"""
 
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, WebDriverException
from typing import List, Dict, Optional
import logging
import time
import re
from datetime import datetime
import os
import pandas as pd
from PIL import Image
import json
from io import BytesIO
import base64
 
logger = logging.getLogger(__name__)
 
class SwissADMEAdapter:
    """Adapter for SwissADME web scraping"""
   
    def __init__(self):
        self.base_url = "http://www.swissadme.ch/"
        self.search_url = f"{self.base_url}index.php"
        self.driver = None
        self.setup_driver()
       
    def setup_driver(self):
        """Setup Chrome driver with headless options"""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
           
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.set_page_load_timeout(30)
            logger.info("Chrome driver initialized successfully")
           
        except Exception as e:
            logger.error(f"Failed to initialize Chrome driver: {e}")
            self.driver = None
   
    async def search_drug_properties(self, smiles: str, max_results: int = 10) -> List[Dict]:
        """
        Search for drug properties using SMILES notation
       
        Args:
            smiles: SMILES notation of the drug molecule
            max_results: Maximum number of results to return (not applicable for single molecule)
           
        Returns:
            List containing drug property dictionary
        """
        try:
            if not self.driver:
                raise Exception("Web driver not initialized")
           
            logger.info(f"Searching SwissADME for SMILES: {smiles[:50]}...")
           
            drug_properties = await self.scrape_swissadme(smiles=smiles, headless=False, timeout=80, download_csv=True, extract_images=True, output_dir="test")
 
            if drug_properties["success"] == True:
                del drug_properties["success"]
                logger.info(f"Retrieved drug properties from SwissADME")
                return [drug_properties] if drug_properties else []
            else:
                raise Exception("Something Went Wrong while Scraping SwissADME for SMILES {smiles}.")
           
        except TimeoutException:
            logger.error("Timeout while waiting for SwissADME page to load")
            raise Exception("SwissADME request timeout")
        except WebDriverException as e:
            logger.error(f"WebDriver error: {e}")
            raise Exception(f"SwissADME web scraping error: {e}")
        except Exception as e:
            logger.error(f"Error searching SwissADME: {e}")
            raise
   
    def _parse_results_page(self) -> Optional[Dict]:
        """Parse the SwissADME results page"""
        try:
            # Get page source
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
           
            # Initialize result dictionary
            drug_properties = {
                "smiles": "",
                "molecular_properties": {},
                "adme_properties": {},
                "drug_likeness": {},
                "medicinal_chemistry": {},
                "source": "swissadme",
                "retrieved_at": datetime.utcnow().isoformat()
            }
           
            # Extract molecular properties
            drug_properties["molecular_properties"] = self._extract_molecular_properties(soup)
           
            # Extract ADME properties
            drug_properties["adme_properties"] = self._extract_adme_properties(soup)
           
            # Extract drug likeness
            drug_properties["drug_likeness"] = self._extract_drug_likeness(soup)
           
            # Extract medicinal chemistry properties
            drug_properties["medicinal_chemistry"] = self._extract_medicinal_chemistry(soup)
           
            return drug_properties
           
        except Exception as e:
            logger.error(f"Error parsing SwissADME results: {e}")
            return None
   
    def _extract_molecular_properties(self, soup: BeautifulSoup) -> Dict:
        """Extract molecular properties from the results page"""
        properties = {}
       
        try:
            # Look for molecular properties table
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        key = cells[0].get_text(strip=True)
                        value = cells[1].get_text(strip=True)
                        if key and value:
                            properties[key] = value
        except Exception as e:
            logger.error(f"Error extracting molecular properties: {e}")
       
        return properties
   
    def _extract_adme_properties(self, soup: BeautifulSoup) -> Dict:
        """Extract ADME properties from the results page"""
        properties = {}
       
        try:
            # Look for ADME-related content
            # This is a simplified extraction - in practice, you'd need to identify
            # the specific sections and tables containing ADME data
            adme_sections = soup.find_all(text=re.compile(r'ADME|Absorption|Distribution|Metabolism|Excretion', re.I))
           
            for section in adme_sections:
                parent = section.parent
                if parent:
                    # Extract nearby data
                    tables = parent.find_next_siblings('table')
                    for table in tables:
                        rows = table.find_all('tr')
                        for row in rows:
                            cells = row.find_all(['td', 'th'])
                            if len(cells) >= 2:
                                key = cells[0].get_text(strip=True)
                                value = cells[1].get_text(strip=True)
                                if key and value:
                                    properties[key] = value
        except Exception as e:
            logger.error(f"Error extracting ADME properties: {e}")
       
        return properties
   
    def _extract_drug_likeness(self, soup: BeautifulSoup) -> Dict:
        """Extract drug likeness properties"""
        properties = {}
       
        try:
            # Look for drug likeness indicators
            drug_likeness_indicators = [
                'Lipinski', 'Veber', 'Egan', 'Muegge', 'Bioavailability Score'
            ]
           
            for indicator in drug_likeness_indicators:
                elements = soup.find_all(text=re.compile(indicator, re.I))
                for element in elements:
                    parent = element.parent
                    if parent:
                        # Extract the value or status
                        value_element = parent.find_next_sibling()
                        if value_element:
                            properties[indicator] = value_element.get_text(strip=True)
        except Exception as e:
            logger.error(f"Error extracting drug likeness: {e}")
       
        return properties
   
    def _extract_medicinal_chemistry(self, soup: BeautifulSoup) -> Dict:
        """Extract medicinal chemistry properties"""
        properties = {}
       
        try:
            # Look for medicinal chemistry related content
            medchem_terms = [
                'PAINS', 'Brenk', 'Lead-likeness', 'Synthetic accessibility'
            ]
           
            for term in medchem_terms:
                elements = soup.find_all(text=re.compile(term, re.I))
                for element in elements:
                    parent = element.parent
                    if parent:
                        value_element = parent.find_next_sibling()
                        if value_element:
                            properties[term] = value_element.get_text(strip=True)
        except Exception as e:
            logger.error(f"Error extracting medicinal chemistry properties: {e}")
       
        return properties
   
    async def search_by_drug_name(self, drug_name: str) -> List[Dict]:
        """
        Search for drug properties by drug name (requires SMILES conversion)
        Note: This is a simplified implementation. In practice, you'd need
        to convert drug names to SMILES first using another service.
        """
        try:
            # For demonstration, we'll use a placeholder SMILES
            # In a real implementation, you'd use a chemical name to SMILES converter
            placeholder_smiles = "CCO"  # Ethanol as placeholder
           
            logger.warning(f"Drug name search not fully implemented. Using placeholder SMILES for: {drug_name}")
            return await self.search_drug_properties(drug_name.split(","))
           
        except Exception as e:
            logger.error(f"Error searching by drug name: {e}")
            raise
   
    def cleanup(self):
        """Clean up the web driver"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("Web driver cleaned up")
            except Exception as e:
                logger.error(f"Error cleaning up web driver: {e}")
   
    def get_source_info(self) -> Dict:
        """Get information about the SwissADME data source"""
        return {
            "name": "SwissADME",
            "description": "SwissADME is a free web tool to evaluate pharmacokinetics, drug-likeness and medicinal chemistry friendliness of small molecules",
            "url": "http://www.swissadme.ch/",
            "api_documentation": "Not available - web scraping required",
            "data_types": ["drug_properties", "adme_predictions", "drug_likeness", "medicinal_chemistry"],
            "access_method": "web_scraping",
            "rate_limits": "No official limits, but reasonable usage expected",
            "requirements": "SMILES notation input required"
        }
 
    async def scrape_swissadme(self, smiles=[], headless=True, timeout=30, download_csv=True, extract_images=True, output_dir="swissadme_output"):
        """
        Scrape SwissADME website with a SMILES string
        
        Args:
            smiles (list): List of SMILES notation of the molecules
            headless (bool): Run browser in headless mode
            timeout (int): Maximum wait time for page elements
            download_csv (bool): Download CSV data if available
            extract_images (bool): Extract molecule images as PIL Image objects
            output_dir (str): Directory to save downloaded files
        
        Returns:
            dict: Results containing success status, data, CSV data, and images
        """
        
        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Configure Chrome options
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        # Configure download preferences
        # prefs = {
        #     "download.default_directory": os.path.abspath(output_dir),
        #     "download.prompt_for_download": False,
        #     "download.directory_upgrade": True,
        #     "safebrowsing.enabled": True
        # }
        # chrome_options.add_experimental_option("prefs", prefs)
        
        # Initialize the driver
        driver = None
        final_result = {
            "success": False,
            "smiles": smiles,
            "physicochemical_properties": {},
            "lipophilicity": {},
            "water_solubility": {},
            "pharmacokinetics": {},
            "druglikeness": {},
            "medicinal_chemistry": {},
            "images": {},
            "source": "swissadme",
        }
        try:
            # You may need to specify the path to chromedriver
            # service = Service("/path/to/chromedriver")
            # driver = webdriver.Chrome(service=service, options=chrome_options)
            
            for smile in smiles:
                final_result["physicochemical_properties"].update({smile: {}})
                final_result["lipophilicity"].update({smile: {}})
                final_result["water_solubility"].update({smile: {}})
                final_result["pharmacokinetics"].update({smile: {}})
                final_result["druglikeness"].update({smile: {}})
                final_result["medicinal_chemistry"].update({smile: {}})
                final_result["images"].update({smile: {}})

            driver = webdriver.Chrome(options=chrome_options)
            
            logger.info(f"Navigating to SwissADME...")
            driver.get("http://www.swissadme.ch/index.php")
            
            # Wait for the page to load
            wait = WebDriverWait(driver, timeout)
            
            # Find the SMILES input textarea
            logger.info("Looking for SMILES input field...")
            smiles_textarea = wait.until(
                EC.presence_of_element_located((By.NAME, "smiles"))
            )
            
            # Clear any existing content and enter the SMILES string
            logger.info(f"Entering SMILES: {smiles}")
            smiles_textarea.clear()
            smiles_textarea.send_keys("\n".join(smiles))
            
            # Find and click the submit button
            logger.info("Submitting form...")
            submit_button = driver.find_element(By.ID, "submitButton")
            submit_button.click()
            
            # Wait for results to load - look for specific elements that indicate processing is complete
            logger.info("Waiting for results to load...")
            
            # Wait for the results page to load (you may need to adjust this selector)
            # This waits for any element with class 'result' or similar indicator
            try:
                # Wait for the page to process and show results
                # You might need to adjust this based on the actual page structure
                results_loaded = wait.until(
                    EC.any_of(
                        EC.presence_of_element_located((By.CLASS_NAME, "result")),
                        EC.presence_of_element_located((By.ID, "results")),
                        EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'panel')]")),
                        EC.presence_of_element_located((By.XPATH, "//table")),
                    )
                )
                logger.info("Results loaded successfully!")
                
            except TimeoutException:
                logger.error("Timeout waiting for specific result elements, but page may still contain data...")
            
            # Give additional time for all content to load
            time.sleep(3)
            
            # Extract data from the results page
            logger.info("Extracting results...")
            
            # Get page title
            page_title = driver.title
            
            # Get current URL
            current_url = driver.current_url
            
            # Get the full page source if needed
            page_source = driver.page_source
            
            # Initialize result containers
            csv_data = None
            images = []
            
            # Download CSV if requested
            if download_csv:
                logger.info("Looking for CSV download button...")
                try:
                    # Look for CSV download button/link
                    csv_buttons = driver.find_elements(By.XPATH, "//a[contains(@href, 'csv') or contains(text(), 'CSV') or contains(text(), 'csv')]")
                    
                    if not csv_buttons:
                        # Alternative selectors for CSV download
                        csv_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'CSV') or contains(text(), 'csv')]")
                    
                    if not csv_buttons:
                        # Look for download buttons or links
                        csv_buttons = driver.find_elements(By.XPATH, "//a[contains(text(), 'Download') or contains(@title, 'Download')]")
                    
                    if csv_buttons:
                        logger.info(f"Found {len(csv_buttons)} potential CSV download button(s)")
                        
                        # Try clicking the first CSV button
                        csv_button = csv_buttons[0]

                        driver.execute_script("arguments[0].scrollIntoView();", csv_button)
                        time.sleep(1)

                        try:
                            csv_data = pd.read_csv(csv_button.get_attribute("href"))
                            logger.info(f"CSV data loaded with {len(csv_data)} rows and {len(csv_data.columns)} columns")
                            result = csv_data.to_json(orient="records")
                            csv_json_data = json.loads(result)

                            for i, json_object in enumerate(csv_json_data):
                                final_result["physicochemical_properties"][smiles[i]] = {
                                    "Formula": json_object["Formula"],
                                    "Molecular Weight": json_object["MW"],
                                    "No Heavy Atoms": json_object["#Heavy atoms"],
                                    "No Arom Heavy Atoms": json_object["#Aromatic heavy atoms"],
                                    "Fraction Csp3": json_object["Fraction Csp3"],
                                    "No Rotatable bonds": json_object["#Rotatable bonds"],
                                    "No H-bond acceptors": json_object["#H-bond acceptors"],
                                    "No H-bond donors": json_object["#H-bond donors"],
                                    "Molar Refractivity": json_object["MR"],
                                    "TPSA": json_object["TPSA"],
                                }

                                final_result["lipophilicity"][smiles[i]] = {
                                    "Log Po/w (iLOGP)": json_object["iLOGP"],
                                    "Log Po/w (XLOGP3)": json_object["XLOGP3"],
                                    "Log Po/w (WLOGP)": json_object["WLOGP"],
                                    "Log Po/w (MLOGP)": json_object["MLOGP"],
                                    "Log Po/w (SILICOS-IT)": json_object["Silicos-IT Log P"],
                                    "Consensus Log Po/w": json_object["Consensus Log P"]
                                }

                                final_result["water_solubility"][smiles[i]] = {
                                    "Log S (ESOL)": json_object["ESOL Log S"],
                                    "ESOL Solubility mg/ml": json_object["ESOL Solubility (mg/ml)"],
                                    "ESOL Solubility mol/l": json_object["ESOL Solubility (mol/l)"],
                                    "ESOL Class": json_object["ESOL Class"],
                                    "Log S (Ali)": json_object["Ali Log S"],
                                    "Ali Solubility mg/ml": json_object["Ali Solubility (mg/ml)"],
                                    "Ali Solubility mol/l": json_object["Ali Solubility (mol/l)"],
                                    "Ali Class": json_object["Ali Class"],
                                    "Log S (SILICOS-IT)": json_object["Silicos-IT LogSw"],
                                    "Silicos-IT Solubility mg/ml": json_object["Silicos-IT Solubility (mg/ml)"],
                                    "Silicos-IT Solubility mol/l": json_object["Silicos-IT Solubility (mol/l)"],
                                    "Silicos-IT Class": json_object["Silicos-IT class"],
                                }

                                final_result["pharmacokinetics"][smiles[i]] = {
                                    "GI absorption": json_object["GI absorption"],
                                    "BBB permeant": json_object["BBB permeant"],
                                    "Pgp substrate": json_object["Pgp substrate"],
                                    "CYP1A2 inhibitor": json_object["CYP1A2 inhibitor"],
                                    "CYP2C19 inhibitor": json_object["CYP2C19 inhibitor"],
                                    "CYP2C9 inhibitor": json_object["CYP2C9 inhibitor"],
                                    "CYP2D6 inhibitor": json_object["CYP2D6 inhibitor"],
                                    "CYP3A4 inhibitor": json_object["CYP3A4 inhibitor"],
                                    "Log Kp (skin permeation)": json_object["log Kp (cm/s)"],
                                }

                                final_result["druglikeness"][smiles[i]] = {
                                    "Lipinski": json_object["Lipinski #violations"],
                                    "Ghose": json_object["Ghose #violations"],
                                    "Veber": json_object["Veber #violations"],
                                    "Egan": json_object["Egan #violations"],
                                    "Muegge #violations": json_object["Muegge #violations"],
                                    "Bioavailability Score": json_object["Bioavailability Score"],
                                }

                                final_result["medicinal_chemistry"][smiles[i]] = {
                                    "PAINS": json_object["PAINS #alerts"],
                                    "Brenk": json_object["Brenk #alerts"],
                                    "Leadlikeness": json_object["Leadlikeness #violations"],
                                    "Synthetic accessibility": json_object["Synthetic Accessibility"],
                                }

                        except Exception as e:
                            logger.error(f"Error reading CSV: {e}")
                    else:
                        logger.info("No CSV download button found")
                        
                except Exception as e:
                    logger.error(f"Error downloading CSV: {e}")
            
            # Extract images if requested
            if extract_images:
                logger.info("Extracting images...")
                try:
                    radar_image_elements = driver.find_elements(By.XPATH, "//img[contains(@src, 'radar') and contains(@src, 'molecule')]")
                    molecule_structure_image_elements = driver.find_elements(By.XPATH, "//img[starts-with(@src, 'data:image')]")
                    
                    for i, (radar_img, mol_structure_img) in enumerate(zip(radar_image_elements, molecule_structure_image_elements)):
                        try:
                            radar_img_src = radar_img.get_attribute('src')
                            mol_structure_img_src = mol_structure_img.get_attribute('src')
                            
                            final_result["images"][smiles[i]].update({"radar_image": radar_img_src, "mol_structure_img_src": mol_structure_img_src})
                        except Exception as e:
                            logger.error(f"Something went wrong! Error: {e}")

                except Exception as e:
                    logger.info(f"Error extracting images: {e}")
            
            logger.info(f"### FINAL RESULT ###: \n\n{final_result}\n\n")
            final_result["success"] = True
            return final_result
            
        except TimeoutException as e:
            error_msg = f"Timeout error: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
        
        except Exception as e:
            error_msg = f"An error occurred: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}     
               
        finally:
            if driver:
                driver.quit()
    
# async def main():
#     adapter = SwissADMEAdapter()
#     result = await adapter.search_drug_properties(["CCO", "CC"])
#     print(result)
 
# if __name__ == "__main__":
#     import asyncio
#     asyncio.run(main())