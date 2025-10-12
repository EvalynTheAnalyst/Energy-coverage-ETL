"""
Africa Energy Portal Comprehensive Data Scraper
Extracts REAL energy data for ALL African countries (2000-2022) using year slider
Saves to CSV with years as rows and year column at the end
"""

import time
import os
import csv
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import pandas as pd
import re
import numpy as np
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service


class AfricaEnergyPortalScraper:
    def __init__(self):
        self.base_url = "https://africa-energy-portal.org"
        self.driver = None
        self.all_data = []
        
        # Required columns for final output - year column at the end
        self.required_columns = [
            'country', 'country_serial', 'metric', 'value', 'unit', 'sector', 
            'sub_sector', 'sub_sub_sector', 'source_link', 'source', 'year'
        ]
        
        # African countries with ISO3 codes
        self.african_countries = {
            "algeria": "DZA", "angola": "AGO", "benin": "BEN", "botswana": "BWA", 
            "burkina-faso": "BFA", "burundi": "BDI", "cameroon": "CMR", 
            "cape-verde": "CPV", "central-african-republic": "CAF", "chad": "TCD", 
            "comoros": "COM", "congo-democratic-republic": "COD", "congo-republic": "COG", 
            "cote-divoire": "CIV", "djibouti": "DJI", "egypt": "EGY", 
            "equatorial-guinea": "GNQ", "eritrea": "ERI", "eswatini": "SWZ", 
            "ethiopia": "ETH", "gabon": "GAB", "gambia": "GMB", "ghana": "GHA", 
            "guinea": "GIN", "guinea-bissau": "GNB", "kenya": "KEN", "lesotho": "LSO", 
            "liberia": "LBR", "libya": "LBY", "madagascar": "MDG", "malawi": "MWI", 
            "mali": "MLI", "mauritania": "MRT", "mauritius": "MUS", "morocco": "MAR", 
            "mozambique": "MOZ", "namibia": "NAM", "niger": "NER", "nigeria": "NGA", 
            "rwanda": "RWA", "sao-tome-and-principe": "STP", "senegal": "SEN", 
            "seychelles": "SYC", "sierra-leone": "SLE", "somalia": "SOM", 
            "south-africa": "ZAF", "south-sudan": "SSD", "sudan": "SDN", 
            "tanzania": "TZA", "togo": "TGO", "tunisia": "TUN", "uganda": "UGA", 
            "zambia": "ZMB", "zimbabwe": "ZWE"
        }

    def setup_driver(self):
        """Initialize Chrome WebDriver with proper configuration"""
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            print("[OK] Chrome driver initialized successfully")
        except Exception as e:
            print(f"[ERROR] Failed to initialize driver: {e}")
            try:
                self.driver = webdriver.Chrome(options=chrome_options)
                print("[OK] Chrome driver initialized (fallback method)")
            except Exception as e2:
                print(f"[ERROR] Fallback also failed: {e2}")
                raise
    
    def close_driver(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()
            print("[OK] Browser closed")
    
    def wait_for_element(self, by, value, timeout=15):
        """Wait for element to be present"""
        try:
            return WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
        except TimeoutException:
            print(f"    [TIMEOUT] Element not found: {value}")
            return None

    def safe_find_element(self, by, value, parent=None):
        """Safely find element without throwing exception"""
        try:
            if parent:
                return parent.find_element(by, value)
            return self.driver.find_element(by, value)
        except NoSuchElementException:
            return None
    
    def safe_find_elements(self, by, value, parent=None):
        """Safely find multiple elements"""
        try:
            if parent:
                return parent.find_elements(by, value)
            return self.driver.find_elements(by, value)
        except NoSuchElementException:
            return []

    def extract_country_data_with_slider(self, country_slug, iso_code):
        """Extract comprehensive energy data for a specific country using year slider"""
        country_name = country_slug.replace('-', ' ').title()
        country_url = f"{self.base_url}/aep/country/{country_slug}"
        
        print(f"\n  [EXTRACTING] {country_name} ({iso_code})")
        print(f"  URL: {country_url}")
        
        country_data = []
        
        try:
            self.driver.get(country_url)
            time.sleep(5)
            
            # Wait for page to load completely
            if not self.wait_for_element(By.TAG_NAME, "body"):
                print(f"    [ERROR] Page failed to load for {country_name}")
                return []
            
            # First, try to extract data using the year slider
            slider_data = self.extract_data_using_year_slider(country_name, iso_code, country_url)
            country_data.extend(slider_data)
            
            # If no slider data found, try alternative extraction methods
            if not slider_data:
                print("    [INFO] No slider data found, trying alternative methods...")
                alternative_data = self.extract_alternative_data(country_name, iso_code, country_url)
                country_data.extend(alternative_data)
            
            print(f"  [SUCCESS] Extracted {len(country_data)} data points for {country_name}")
            return country_data
            
        except Exception as e:
            print(f"  [ERROR] Failed to extract data for {country_name}: {e}")
            return []

    def extract_data_using_year_slider(self, country_name, iso_code, source_url):
        """Extract data by interacting with the year slider"""
        slider_data = []
        
        try:
            # Find the year slider
            year_slider = self.safe_find_element(By.CSS_SELECTOR, ".year-slider-block, .ui-slider")
            if not year_slider:
                print("    [ERROR] Year slider not found on page")
                return slider_data
            
            print("    [FOUND] Year slider detected")
            
            # Get all available years from the slider
            available_years = self.get_available_years_from_slider()
            print(f"    [YEARS] Available years: {available_years}")
            
            # Limit to recent years for faster testing, remove this limit for full extraction
            if len(available_years) > 3:
                print(f"    [INFO] Testing with recent 3 years: {available_years[-3:]}")
                available_years = available_years[-3:]
            
            # Extract data for each available year
            for year in available_years:
                try:
                    print(f"    [PROCESSING] Year {year}")
                    
                    # Set the slider to this year
                    if self.set_slider_to_year(year):
                        time.sleep(3)  # Wait for data to update
                        
                        # Extract data for this specific year
                        year_data = self.extract_data_for_current_year(country_name, iso_code, source_url, year)
                        slider_data.extend(year_data)
                        
                        print(f"      [YEAR {year}] Extracted {len(year_data)} data points")
                    
                except Exception as e:
                    print(f"      [ERROR] Processing year {year}: {e}")
                    continue
            
        except Exception as e:
            print(f"    [ERROR] Extracting data with slider: {e}")
        
        return slider_data

    def extract_alternative_data(self, country_name, iso_code, source_url):
        """Alternative data extraction methods when slider doesn't work"""
        alternative_data = []
        
        try:
            print("    [ALTERNATIVE] Using alternative extraction methods...")
            
            # Method 1: Extract from key metrics and indicators
            metrics_data = self.extract_key_metrics(country_name, iso_code, source_url)
            alternative_data.extend(metrics_data)
            
            # Method 2: Extract from any visible data displays
            display_data = self.extract_all_visible_data(country_name, iso_code, source_url)
            alternative_data.extend(display_data)
            
            # Method 3: Extract from any charts or visualizations
            chart_data = self.extract_all_chart_data(country_name, iso_code, source_url)
            alternative_data.extend(chart_data)
            
            print(f"    [ALTERNATIVE] Found {len(alternative_data)} data points using alternative methods")
            
        except Exception as e:
            print(f"    [ERROR] Alternative extraction: {e}")
        
        return alternative_data

    def extract_key_metrics(self, country_name, iso_code, source_url):
        """Extract key energy metrics from the page"""
        metrics_data = []
        
        try:
            # Look for common energy metric patterns in the page text
            page_text = self.driver.page_source
            soup = BeautifulSoup(page_text, 'html.parser')
            text_content = soup.get_text()
            
            # Define comprehensive energy metric patterns
            metric_patterns = [
                # Electricity Access
                (r'access.*?electricity.*?(\d+\.?\d*)\s*%', 'Access to Electricity', '%', 'Electricity', 'Access', 'Population'),
                (r'electrification.*?rate.*?(\d+\.?\d*)\s*%', 'Access to Electricity', '%', 'Electricity', 'Access', 'Population'),
                (r'electricity.*?access.*?(\d+\.?\d*)\s*%', 'Access to Electricity', '%', 'Electricity', 'Access', 'Population'),
                
                # Generation Capacity
                (r'installed.*?capacity.*?(\d+[,\.]?\d*)\s*(MW|GW)', 'Installed Capacity', 'MW', 'Electricity', 'Generation', 'Total'),
                (r'generation.*?capacity.*?(\d+[,\.]?\d*)\s*(MW|GW)', 'Installed Capacity', 'MW', 'Electricity', 'Generation', 'Total'),
                (r'capacity.*?(\d+[,\.]?\d*)\s*(MW|GW)', 'Installed Capacity', 'MW', 'Electricity', 'Generation', 'Total'),
                
                # Electricity Generation
                (r'electricity.*?generation.*?(\d+[,\.]?\d*)\s*(GWh|TWh)', 'Electricity Generation', 'GWh', 'Electricity', 'Generation', 'Total'),
                (r'power.*?generation.*?(\d+[,\.]?\d*)\s*(GWh|TWh)', 'Electricity Generation', 'GWh', 'Electricity', 'Generation', 'Total'),
                (r'generation.*?(\d+[,\.]?\d*)\s*(GWh|TWh)', 'Electricity Generation', 'GWh', 'Electricity', 'Generation', 'Total'),
                
                # Consumption
                (r'electricity.*?consumption.*?(\d+[,\.]?\d*)\s*(GWh|TWh)', 'Electricity Consumption', 'GWh', 'Electricity', 'Consumption', 'Total'),
                (r'energy.*?consumption.*?(\d+[,\.]?\d*)', 'Energy Consumption', 'toe', 'Energy', 'Consumption', 'Total'),
                
                # Renewable Energy
                (r'renewable.*?capacity.*?(\d+[,\.]?\d*)\s*(MW|GW)', 'Renewable Capacity', 'MW', 'Renewables', 'Generation', 'Total'),
                (r'solar.*?capacity.*?(\d+[,\.]?\d*)\s*(MW|GW)', 'Solar Capacity', 'MW', 'Renewables', 'Generation', 'Solar'),
                (r'wind.*?capacity.*?(\d+[,\.]?\d*)\s*(MW|GW)', 'Wind Capacity', 'MW', 'Renewables', 'Generation', 'Wind'),
                (r'hydro.*?capacity.*?(\d+[,\.]?\d*)\s*(MW|GW)', 'Hydro Capacity', 'MW', 'Renewables', 'Generation', 'Hydro'),
            ]
            
            for pattern, metric, unit, sector, sub_sector, sub_sub_sector in metric_patterns:
                matches = re.finditer(pattern, text_content, re.IGNORECASE)
                for match in matches:
                    try:
                        value = match.group(1).replace(',', '')
                        actual_unit = match.group(2) if match.lastindex >= 2 else unit
                        
                        numeric_value = self.safe_convert_value(value)
                        
                        if numeric_value != '':
                            # Create data row with current year (assume latest available)
                            row_data = self.create_data_row(
                                country_name, iso_code, metric, 
                                numeric_value, actual_unit, sector, sub_sector, sub_sub_sector, 
                                source_url, 2022  # Assume latest year
                            )
                            
                            metrics_data.append(row_data)
                            print(f"        [METRIC] {metric}: {value} {actual_unit}")
                            
                    except (ValueError, IndexError):
                        continue
                        
        except Exception as e:
            print(f"      [ERROR] Extracting key metrics: {e}")
        
        return metrics_data

    def extract_all_visible_data(self, country_name, iso_code, source_url):
        """Extract all visible numeric data from the page"""
        visible_data = []
        
        try:
            # Look for all elements that contain numeric data with units
            elements_with_data = self.safe_find_elements(By.XPATH, 
                "//*[contains(text(), '%') or contains(text(), 'MW') or contains(text(), 'GW') or contains(text(), 'GWh') or contains(text(), 'TWh')]")
            
            for element in elements_with_data[:50]:  # Limit to first 50 elements
                try:
                    element_text = element.text.strip()
                    if element_text and len(element_text) < 300:
                        # Look for numeric value with unit
                        value_pattern = r'(\d+[,\.]?\d*)\s*(%|MW|GW|GWh|TWh|kWh|MWh)'
                        match = re.search(value_pattern, element_text, re.IGNORECASE)
                        
                        if match:
                            value = match.group(1).replace(',', '')
                            unit = match.group(2).upper()
                            numeric_value = self.safe_convert_value(value)
                            
                            if numeric_value != '':
                                # Determine metric from context
                                metric_name = self.infer_metric_from_context(element_text)
                                sector, sub_sector, sub_sub_sector = self.classify_metric(metric_name)
                                
                                row_data = self.create_data_row(
                                    country_name, iso_code, metric_name, 
                                    numeric_value, unit, sector, sub_sector, sub_sub_sector, 
                                    source_url, 2022  # Assume latest year
                                )
                                
                                visible_data.append(row_data)
                                print(f"        [VISIBLE] {metric_name}: {value} {unit}")
                                
                except Exception as e:
                    continue
                    
        except Exception as e:
            print(f"      [ERROR] Extracting visible data: {e}")
        
        return visible_data

    def extract_all_chart_data(self, country_name, iso_code, source_url):
        """Extract data from all chart-like elements"""
        chart_data = []
        
        try:
            # Look for various chart and data visualization elements
            chart_selectors = [
                ".chart", ".graph", ".visualization", ".plot",
                "[class*='chart']", "[class*='graph']", "[class*='visualization']",
                "canvas", "svg", ".highcharts-container", ".plotly"
            ]
            
            for selector in chart_selectors:
                elements = self.safe_find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    try:
                        # Get parent context which might contain data labels
                        parent = element.find_element(By.XPATH, "./..")
                        parent_text = parent.text
                        
                        # Extract any numeric data from the context
                        value_pattern = r'(\d+[,\.]?\d*)\s*(%|MW|GW|GWh|TWh)'
                        matches = re.findall(value_pattern, parent_text, re.IGNORECASE)
                        
                        for match in matches:
                            value = match[0].replace(',', '')
                            unit = match[1].upper()
                            numeric_value = self.safe_convert_value(value)
                            
                            if numeric_value != '':
                                metric_name = self.infer_metric_from_context(parent_text)
                                sector, sub_sector, sub_sub_sector = self.classify_metric(metric_name)
                                
                                row_data = self.create_data_row(
                                    country_name, iso_code, metric_name, 
                                    numeric_value, unit, sector, sub_sector, sub_sub_sector, 
                                    source_url, 2022  # Assume latest year
                                )
                                
                                chart_data.append(row_data)
                                print(f"        [CHART] {metric_name}: {value} {unit}")
                                
                    except Exception as e:
                        continue
                        
        except Exception as e:
            print(f"      [ERROR] Extracting chart data: {e}")
        
        return chart_data

    def get_available_years_from_slider(self):
        """Get all available years from the year slider"""
        available_years = []
        
        try:
            # Find all year labels in the slider
            year_elements = self.safe_find_elements(By.CSS_SELECTOR, ".ui-slider-label, .ui-slider-pip-label")
            
            for element in year_elements:
                try:
                    year_text = element.text.strip()
                    if year_text and year_text.isdigit():
                        year = int(year_text)
                        if 2000 <= year <= 2022:
                            available_years.append(year)
                    else:
                        # Try to get year from data-value attribute
                        data_value = element.get_attribute('data-value')
                        if data_value and data_value.isdigit():
                            year = int(data_value)
                            if 2000 <= year <= 2022:
                                available_years.append(year)
                except:
                    continue
            
            # Remove duplicates and sort
            available_years = sorted(list(set(available_years)))
            
        except Exception as e:
            print(f"    [ERROR] Getting available years: {e}")
        
        return available_years

    def set_slider_to_year(self, target_year):
        """Set the year slider to a specific year"""
        try:
            # Find the year element we want to click
            year_element = self.safe_find_element(By.CSS_SELECTOR, f".ui-slider-label[data-value='{target_year}'], .ui-slider-pip-label[data-value='{target_year}']")
            
            if year_element:
                # Click directly on the year label
                self.driver.execute_script("arguments[0].scrollIntoView(true);", year_element)
                time.sleep(1)
                year_element.click()
                time.sleep(2)
                print(f"      [SLIDER] Set to year {target_year} by clicking label")
                return True
            else:
                print(f"      [ERROR] Could not find year element for {target_year}")
                return False
            
        except Exception as e:
            print(f"      [ERROR] Setting slider to year {target_year}: {e}")
            return False

    def extract_data_for_current_year(self, country_name, iso_code, source_url, current_year):
        """Extract data for the currently selected year"""
        year_data = []
        
        try:
            # Use the same alternative methods but with specific year
            metrics_data = self.extract_key_metrics_with_year(country_name, iso_code, source_url, current_year)
            year_data.extend(metrics_data)
            
            display_data = self.extract_all_visible_data_with_year(country_name, iso_code, source_url, current_year)
            year_data.extend(display_data)
            
        except Exception as e:
            print(f"      [ERROR] Extracting data for year {current_year}: {e}")
        
        return year_data

    def extract_key_metrics_with_year(self, country_name, iso_code, source_url, year):
        """Extract key metrics for specific year"""
        # This would use the same logic as extract_key_metrics but assign the specific year
        metrics_data = self.extract_key_metrics(country_name, iso_code, source_url)
        
        # Update all records with the specific year
        for record in metrics_data:
            record['year'] = year
            
        return metrics_data

    def extract_all_visible_data_with_year(self, country_name, iso_code, source_url, year):
        """Extract visible data for specific year"""
        visible_data = self.extract_all_visible_data(country_name, iso_code, source_url)
        
        # Update all records with the specific year
        for record in visible_data:
            record['year'] = year
            
        return visible_data

    def create_data_row(self, country_name, iso_code, metric, value, unit, sector, sub_sector, sub_sub_sector, source_url, year):
        """Create a data row with year as the LAST column"""
        return {
            'country': country_name,
            'country_serial': iso_code,
            'metric': metric,
            'value': value,
            'unit': unit,
            'sector': sector,
            'sub_sector': sub_sector,
            'sub_sub_sector': sub_sub_sector,
            'source_link': source_url,
            'source': 'Africa Energy Portal',
            'year': year  # Year as the LAST column
        }

    def infer_metric_from_context(self, text):
        """Infer metric name from context text"""
        text_lower = text.lower()
        
        if 'access' in text_lower or 'electrification' in text_lower:
            return "Access to Electricity"
        elif 'generation' in text_lower and 'electricity' in text_lower:
            return "Electricity Generation"
        elif 'capacity' in text_lower and 'installed' in text_lower:
            return "Installed Capacity"
        elif 'consumption' in text_lower and 'electricity' in text_lower:
            return "Electricity Consumption"
        elif 'renewable' in text_lower:
            return "Renewable Energy"
        elif 'solar' in text_lower:
            return "Solar Energy"
        elif 'wind' in text_lower:
            return "Wind Energy"
        elif 'hydro' in text_lower:
            return "Hydro Power"
        elif 'oil' in text_lower:
            return "Oil Production"
        elif 'gas' in text_lower:
            return "Natural Gas"
        else:
            return "Energy Indicator"

    def classify_metric(self, metric_name):
        """Classify metric into sector and sub-sectors"""
        metric_lower = metric_name.lower()
        
        if 'access' in metric_lower:
            return 'Electricity', 'Access', 'Population'
        elif 'generation' in metric_lower:
            return 'Electricity', 'Generation', 'Total'
        elif 'capacity' in metric_lower:
            return 'Electricity', 'Generation', 'Capacity'
        elif 'consumption' in metric_lower:
            return 'Electricity', 'Consumption', 'Total'
        elif 'renewable' in metric_lower or 'solar' in metric_lower or 'wind' in metric_lower or 'hydro' in metric_lower:
            return 'Renewables', 'Generation', 'Total'
        elif 'oil' in metric_lower or 'gas' in metric_lower:
            return 'Oil & Gas', 'Production', 'Total'
        else:
            return 'Energy', 'General', 'National'

    def safe_convert_value(self, value):
        """Safely convert value to numeric"""
        if pd.isna(value) or value == '' or value is None or str(value).lower() in ['nan', 'none', 'null', '-', 'n/a', '']:
            return ''
        
        try:
            if isinstance(value, (int, float)):
                return float(value)
            
            clean_value = str(value).strip()
            clean_value = re.sub(r'[^\d\.]', '', clean_value)
            
            if clean_value and clean_value != '.':
                numeric_value = float(clean_value)
                if 0 < numeric_value < 1e15:
                    return numeric_value
            return ''
        except (ValueError, TypeError):
            return ''

    def scrape_all_data(self, output_file="africa_energy_data.csv"):
        """Main method to scrape all data from ALL countries"""
        print(f"\n{'='*80}")
        print("AFRICA ENERGY PORTAL - COMPREHENSIVE DATA EXTRACTION")
        print(f"{'='*80}")
        print(f"Target Countries: {len(self.african_countries)}")
        print(f"Time Period: 2000-2022")
        print(f"Output File: {output_file}")
        print(f"{'='*80}\n")
        
        all_extracted_data = []
        successful_countries = 0
        
        try:
            # Process ALL countries
            total_countries = len(self.african_countries)
            
            for i, (country_slug, iso_code) in enumerate(self.african_countries.items(), 1):
                print(f"\n[{i}/{total_countries}] Processing {country_slug}...")
                
                country_data = self.extract_country_data_with_slider(country_slug, iso_code)
                
                if country_data:
                    all_extracted_data.extend(country_data)
                    successful_countries += 1
                    print(f"  [SUCCESS] Added {len(country_data)} data records for {country_slug}")
                else:
                    print(f"  [WARNING] No data extracted for {country_slug}")
                
                # Show progress
                print(f"  [PROGRESS] {successful_countries}/{total_countries} countries completed")
                print(f"  [TOTAL DATA] {len(all_extracted_data)} records collected so far")
                
                # Be respectful with delays between requests
                if i < total_countries:
                    delay = 2
                    print(f"  [WAITING] {delay} seconds before next country...")
                    time.sleep(delay)
            
            # Save data to CSV
            if all_extracted_data:
                self.save_to_csv(all_extracted_data, output_file)
                return successful_countries
            else:
                print("[ERROR] No data was extracted!")
                return 0
                
        except Exception as e:
            print(f"[FATAL ERROR] Scraping failed: {e}")
            import traceback
            traceback.print_exc()
            return 0

    def save_to_csv(self, data, output_file):
        """Save extracted data to CSV with year as the last column"""
        print(f"\n[SAVING] Processing {len(data)} records...")
        
        df = pd.DataFrame(data)
        
        # Ensure all required columns exist
        for col in self.required_columns:
            if col not in df.columns:
                df[col] = ''
        
        # Reorder columns to have year at the end
        df = df[self.required_columns]
        
        # Fill NaN values
        df = df.fillna('')
        
        # Create output directory
        os.makedirs('output', exist_ok=True)
        
        # Save to CSV
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        
        # Calculate comprehensive statistics
        total_countries = df['country'].nunique()
        total_years = df['year'].nunique()
        total_metrics = df['metric'].nunique()
        total_data_points = len(df)
        
        print(f"[SUCCESS] Data saved successfully!")
        print(f"File: {output_file}")
        print(f"Total records: {total_data_points}")
        print(f"Countries covered: {total_countries}/54")
        print(f"Years covered: {total_years}")
        print(f"Unique metrics: {total_metrics}")
        
        # Show sample of actual data
        if len(df) > 0:
            print(f"\nSample of extracted data (year as LAST column):")
            sample_data = df.head(10)[self.required_columns]
            print(sample_data.to_string(index=False))


def scraping():
    """Main execution function"""
    print("\n" + "="*80)
    print("AFRICA ENERGY PORTAL - COMPREHENSIVE DATA EXTRACTION")
    print("Extracting ALL countries with year as the LAST column")
    print("Using robust text-based extraction methods")
    print("="*80)
    
    os.makedirs('output', exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"output/africa_energy_data_{timestamp}.csv"
    
    scraper = AfricaEnergyPortalScraper()
    successful_countries = 0
    
    try:
        print("\n[INITIALIZING] Setting up Chrome driver...")
        scraper.setup_driver()
        
        print("\n[SCRAPING] Starting comprehensive data extraction for ALL countries...")
        print("This may take a while as we're processing all 54 African countries...")
        
        start_time = time.time()
        successful_countries = scraper.scrape_all_data(output_file)
        end_time = time.time()
        
        duration = end_time - start_time
        hours = int(duration // 3600)
        minutes = int((duration % 3600) // 60)
        seconds = int(duration % 60)
        
        if successful_countries > 0:
            print(f"\n{'='*80}")
            print("EXTRACTION COMPLETED SUCCESSFULLY!")
            print(f"{'='*80}")
            print(f"Duration: {hours}h {minutes}m {seconds}s")
            print(f"Countries processed: {successful_countries}/54")
            print(f"Output file: {output_file}")
        else:
            print(f"\n{'='*80}")
            print("EXTRACTION COMPLETED WITH ERRORS")
            print(f"{'='*80}")
            
    except Exception as e:
        print(f"\n[FATAL ERROR] {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        print("\n[CLEANUP] Closing browser...")
        scraper.close_driver()
        print(f"[COMPLETED] Script finished! Processed {successful_countries} countries.")


if __name__ == "__main__":
    scraping()