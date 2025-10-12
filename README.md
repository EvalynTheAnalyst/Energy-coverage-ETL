# Africa Energy Coverage Data Extractor (2000–2022)

## Project Overview

**Africa Energy Coverage Data Extractor (2000–2022)** is a Python-based data engineering project designed to **scrape comprehensive energy metrics for all African countries** from the [Africa Energy Portal (AEP)](https://africa-energy-portal.org).  
Using **Selenium WebDriver**, the system automates data extraction across the **years 2000 to 2022**, handles dynamic web elements (such as year sliders), and compiles structured datasets containing key energy indicators.

The extracted data is stored in a **CSV file** and can optionally be uploaded to **MongoDB Atlas** for persistent cloud storage, enabling advanced analytics, visualization, and historical comparison.

---

## Key Features

- **Full African Coverage** — Includes all 54 African countries.  
- **Time-Series Data (2000–2022)** — Consistent year-by-year scraping of energy metrics.  
- **Robust Extraction Logic** — Handles dynamic elements like sliders and asynchronous page loads using Selenium.  
- **Comprehensive Energy Indicators** — Metrics include Access to Electricity, Installed Capacity, Energy Generation, and Consumption.  
- **CSV Output Generation** — Cleanly structured data export for analysis.  
- **MongoDB Integration** — Optional upload of extracted data to a MongoDB Atlas cluster for scalable storage and querying.  
- **Modular Code Structure** — Separate scripts for scraping, MongoDB operations, and main orchestration.

---

## Technology Stack

| Component | Description |
|------------|-------------|
| **Language** | Python 3.x |
| **Automation** | Selenium WebDriver |
| **Data Handling** | Pandas, NumPy |
| **Driver Management** | webdriver-manager |
| **Database** | MongoDB Atlas |
| **Database Library** | PyMongo |
| **Browser** | Google Chrome (Required for Selenium) |

---

## Project Structure
**Africa_Energy_Coverage_Data_Extractor**/

│

└── README.md - Project documentation

├── requirements.txt - List of required dependencies

├── scrape.py - Core scraping logic (AfricaEnergyPortalScraper class)

├── mongodb.py - MongoDB connection and upload logic

├── main.py - Main execution script to run extraction and upload


