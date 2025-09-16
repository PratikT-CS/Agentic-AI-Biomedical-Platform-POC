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
           
            drug_properties = await self.scrape_swissadme(smiles_string=smiles, headless=False, timeout=80, download_csv=True, extract_images=True)
 
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
            return await self.search_drug_properties(drug_name)
           
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
 
    async def scrape_swissadme(self, smiles_string, headless=True, timeout=60, download_csv=True, extract_images=True, output_dir="swissadme_output"):
        """
        Scrape SwissADME website with a SMILES string
       
        Args:
            smiles_string (str): SMILES notation of the molecule
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
        prefs = {
            "download.default_directory": os.path.abspath(output_dir),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        chrome_options.add_experimental_option("prefs", prefs)
       
        # Initialize the driver
        driver = None
        final_result = {
                    "success": False,
                    "smiles": smiles_string,
                    "physicochemical_properties": {},
                    "lipophilicity": {},
                    "water_solubility": {},
                    "pharmacokinetics": {},
                    "druglikeness": {},
                    "medicinal_chemistry": {},
                    "images": [],
                    "source": "swissadme",
                    "retrieved_at": datetime.utcnow().isoformat()
                }
        try:
            # You may need to specify the path to chromedriver
            # service = Service("/path/to/chromedriver")
            # driver = webdriver.Chrome(service=service, options=chrome_options)
            driver = webdriver.Chrome(options=chrome_options)
           
            print(f"Navigating to SwissADME...")
            driver.get("http://www.swissadme.ch/index.php")
           
            # Wait for the page to load
            wait = WebDriverWait(driver, timeout)
           
            # Find the SMILES input textarea
            print("Looking for SMILES input field...")
            smiles_textarea = wait.until(
                EC.presence_of_element_located((By.NAME, "smiles"))
            )
           
            # Clear any existing content and enter the SMILES string
            print(f"Entering SMILES: {smiles_string}")
            smiles_textarea.clear()
            smiles_textarea.send_keys(smiles_string)
           
            # Find and click the submit button
            print("Submitting form...")
            submit_button = driver.find_element(By.ID, "submitButton")
            submit_button.click()
           
            # Wait for results to load - look for specific elements that indicate processing is complete
            print("Waiting for results to load...")
           
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
                print("Results loaded successfully!")
               
            except TimeoutException:
                print("Timeout waiting for specific result elements, but page may still contain data...")
           
            # Give additional time for all content to load
            time.sleep(3)
           
            # Extract data from the results page
            print("Extracting results...")
           
            # Get page title
            page_title = driver.title
           
            # Get current URL
            current_url = driver.current_url
           
            # Extract all tables (SwissADME typically shows results in tables)
            tables = driver.find_elements(By.TAG_NAME, "table")
            table_data = []
           
            # for i, table in enumerate(tables):
            #     rows = table.find_elements(By.TAG_NAME, "tr")
            #     table_rows = []
            #     for row in rows:
            #         cells = row.find_elements(By.TAG_NAME, "td")
            #         if not cells:  # Try th elements for headers
            #             cells = row.find_elements(By.TAG_NAME, "th")
            #         row_data = [cell.text.strip() for cell in cells if cell.text.strip()]
            #         if row_data:
            #             table_rows.append(row_data)
               
            #     if table_rows:
            #         table_data.append({
            #             f"table_{i+1}": table_rows
            #         })
           
            # # Extract any div elements that might contain results
            # result_divs = driver.find_elements(By.XPATH, "//div[contains(@class, 'panel') or contains(@class, 'result')]")
            # div_data = []
           
            # for i, div in enumerate(result_divs):
            #     div_text = div.text.strip()
            #     if div_text:
            #         div_data.append({
            #             f"div_{i+1}": div_text
            #         })
           
            # Get the full page source if needed
            page_source = driver.page_source
           
            # Initialize result containers
            csv_data = None
            images = []
           
            # Download CSV if requested
            if download_csv:
                print("Looking for CSV download button...")
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
                        print(f"Found {len(csv_buttons)} potential CSV download button(s)")
                       
                        # Try clicking the first CSV button
                        csv_button = csv_buttons[0]
                        driver.execute_script("arguments[0].scrollIntoView();", csv_button)
                        time.sleep(1)
                        csv_button.click()
                       
                        # Wait for download to complete
                        print("Waiting for CSV download...")
                        time.sleep(5)
                       
                        # Look for downloaded CSV file
                        csv_files = [f for f in os.listdir(output_dir) if f.endswith('.csv')]
                        if csv_files:
                            latest_csv = max([os.path.join(output_dir, f) for f in csv_files], key=os.path.getctime)
                            print(f"CSV downloaded: {latest_csv}")
                           
                            # Read CSV data
                            try:
                                csv_data = pd.read_csv(latest_csv)
                                print(f"CSV data loaded with {len(csv_data)} rows and {len(csv_data.columns)} columns")
                                result = csv_data.to_json(orient="records")
                                csv_json_data = json.loads(result)
 
                                final_result["physicochemical_properties"] = {
                                    "formula": csv_json_data[0]["Formula"],
                                    "molecular_weight": csv_json_data[0]["MW"],
                                    "no_heavy_atoms": csv_json_data[0]["#Heavy atoms"],
                                    "no_arom_heavy_atoms": csv_json_data[0]["#Aromatic heavy atoms"],
                                    "fraction_csp3": csv_json_data[0]["Fraction Csp3"],
                                    "no_rotatable_bonds": csv_json_data[0]["#Rotatable bonds"],
                                    "no_h-bond_acceptors": csv_json_data[0]["#H-bond acceptors"],
                                    "no_h-bond_donors": csv_json_data[0]["#H-bond donors"],
                                    "molar_refractivity": csv_json_data[0]["MR"],
                                    "TPSA": csv_json_data[0]["TPSA"],
                                }
 
                                final_result["lipophilicity"] = {
                                    "Log Po/w (iLOGP)": csv_json_data[0]["iLOGP"],
                                    "Log Po/w (XLOGP3)": csv_json_data[0]["XLOGP3"],
                                    "Log Po/w (WLOGP)": csv_json_data[0]["WLOGP"],
                                    "Log Po/w (MLOGP)": csv_json_data[0]["MLOGP"],
                                    "Log Po/w (SILICOS-IT)": csv_json_data[0]["Silicos-IT Log P"],
                                    "Consensus Log Po/w": csv_json_data[0]["Consensus Log P"]
                                }
 
                                final_result["water_solubility"] = {
                                    "Log S (ESOL)": csv_json_data[0]["ESOL Log S"],
                                    "ESOL Solubility mg/ml": csv_json_data[0]["ESOL Solubility (mg/ml)"],
                                    "ESOL Solubility mol/l": csv_json_data[0]["ESOL Solubility (mol/l)"],
                                    "ESOL Class": csv_json_data[0]["ESOL Class"],
                                    "Log S (Ali)": csv_json_data[0]["Ali Log S"],
                                    "Ali Solubility mg/ml": csv_json_data[0]["Ali Solubility (mg/ml)"],
                                    "Ali Solubility mol/l": csv_json_data[0]["Ali Solubility (mol/l)"],
                                    "Ali Class": csv_json_data[0]["Ali Class"],
                                    "Log S (SILICOS-IT)": csv_json_data[0]["Silicos-IT LogSw"],
                                    "Silicos-IT Solubility mg/ml": csv_json_data[0]["Silicos-IT Solubility (mg/ml)"],
                                    "Silicos-ITSolubility mol/l": csv_json_data[0]["Silicos-IT Solubility (mol/l)"],
                                    "Silicos-IT Class": csv_json_data[0]["Silicos-IT class"],
                                }
                                print(f"Pharmacokinetics properties: {final_result['pharmacokinetics']}")
                                final_result["pharmacokinetics"] = {
                                    "GI absorption": csv_json_data[0]["GI absorption"],
                                    "BBB permeant": csv_json_data[0]["BBB permeant"],
                                    "Pgp substrate": csv_json_data[0]["Pgp substrate"],
                                    "CYP1A2 inhibitor": csv_json_data[0]["CYP1A2 inhibitor"],
                                    "CYP2C19 inhibitor": csv_json_data[0]["CYP2C19 inhibitor"],
                                    "CYP2C9 inhibitor": csv_json_data[0]["CYP2C9 inhibitor"],
                                    "CYP2D6 inhibitor": csv_json_data[0]["CYP2D6 inhibitor"],
                                    "CYP3A4 inhibitor": csv_json_data[0]["CYP3A4 inhibitor"],
                                    "Log Kp (skin permeation)": csv_json_data[0]["log Kp (cm/s)"],
                                }
                                print(f"Drug likeness properties: {final_result['druglikeness']}")
                                final_result["druglikeness"] = {
                                    "Lipinski": csv_json_data[0]["Lipinski #violations"],
                                    "Ghose": csv_json_data[0]["Ghose #violations"],
                                    "Veber": csv_json_data[0]["Veber #violations"],
                                    "Egan": csv_json_data[0]["Egan #violations"],
                                    "Muegge": csv_json_data[0]["Muegge #violations"],
                                    "Bioavailability Score": csv_json_data[0]["Bioavailability Score"],
                                }
                                print(f"Medicinal chemistry properties: {final_result['medicinal_chemistry']}")
                                final_result["medicinal_chemistry"] = {
                                    "PAINS": csv_json_data[0]["PAINS #alerts"],
                                    "Brenk": csv_json_data[0]["Brenk #alerts"],
                                    "Leadlikeness": csv_json_data[0]["Leadlikeness #violations"],
                                    "Synthetic accessibility": csv_json_data[0]["Synthetic Accessibility"],
                                }

                            except Exception as e:
                                print(f"Error reading CSV: {e}")
                        else:
                            print("No CSV file found in download directory")
                    else:
                        print("No CSV download button found")
                       
                except Exception as e:
                    print(f"Error downloading CSV: {e}")
           
            # Extract images if requested
            if extract_images:
                print("Extracting images...")
                try:
                    # Look for images - common selectors for molecule images
                    img_elements = driver.find_elements(By.XPATH, "//img[contains(@src, 'mol') or contains(@alt, 'molecule') or contains(@class, 'mol') or starts-with(@src, 'data:image')]")
                   
                    if not img_elements:
                        # Alternative: look for all images and filter
                        all_images = driver.find_elements(By.TAG_NAME, "img")
                        img_elements = [img for img in all_images if img.get_attribute('src') and
                                    ('mol' in img.get_attribute('src').lower() or
                                    'structure' in img.get_attribute('src').lower() or
                                    'compound' in img.get_attribute('src').lower())]
                   
                    if not img_elements:
                        # Get all images if no specific molecule images found
                        img_elements = driver.find_elements(By.TAG_NAME, "img")
                   
                    print(f"Found {len(img_elements)} image(s)")
                   
                    for i, img_element in enumerate(img_elements[:2]):  # Limit to first 2 images as mentioned
                        try:
                            img_src = img_element.get_attribute('src')
                            if img_src:
                                print(f"Processing image {i+1}: {img_src[:100]}...")
                               
                                if img_src.startswith('data:image'):
                                    # Handle base64 encoded images
                                    header, data = img_src.split(',', 1)
                                    img_data = base64.b64decode(data)
                                    img = Image.open(BytesIO(img_data))
                                    images.append({
                                        'image': img,
                                        'type': 'base64',
                                        'source': f'image_{i+1}',
                                        'format': img.format
                                    })
                                    # final_result["images"].append(img)
                                   
                                elif img_src.startswith('http'):
                                    # Handle URL images
                                    response = requests.get(img_src, timeout=10)
                                    if response.status_code == 200:
                                        img = Image.open(BytesIO(response.content))
                                        images.append({
                                            'image': img,
                                            'type': 'url',
                                            'source': img_src,
                                            'format': img.format
                                        })
                                    # final_result["images"].append(img_src)                                    

                                else:
                                    # Handle relative URLs
                                    full_url = driver.current_url.rsplit('/', 1)[0] + '/' + img_src
                                    response = requests.get(full_url, timeout=10)
                                    if response.status_code == 200:
                                        img = Image.open(BytesIO(response.content))
                                        images.append({
                                            'image': img,
                                            'type': 'relative_url',
                                            'source': full_url,
                                            'format': img.format
                                        })
                                    # final_result["images"].append(full_url)                                    
                       
                        except Exception as e:
                            print(f"Error processing image {i+1}: {e}")
                            continue
                   
                    print(f"Successfully extracted {len(images)} images")
                except Exception as e:
                    print(f"Error extracting images: {e}")
           
            final_result["success"] = True
            if csv_data is not None:
                print(f"CSV data: {len(csv_data)} rows × {len(csv_data.columns)} columns")
            print(f"Images extracted: {len(images)}")
            print(f"Final result: {final_result}")
            return final_result
           
        except TimeoutException as e:
            error_msg = f"Timeout error: {str(e)}"
            print(error_msg)
            return {"success": False, "error": error_msg}
           
        except Exception as e:
            error_msg = f"An error occurred: {str(e)}"
            print(error_msg)
            return {"success": False, "error": error_msg}
           
        finally:
            if driver:
                driver.quit()
 
# async def main():
#     adapter = SwissADMEAdapter()
#     result = await adapter.search_drug_properties("CCO")
#     print(result)
 
# if __name__ == "__main__":
#     import asyncio
#     asyncio.run(main())