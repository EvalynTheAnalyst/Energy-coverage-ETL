# Africa Energy Coverage Data Extractor (2000–2022)

## Project Overview

**Africa Energy Coverage Data Extractor (2000–2022)** is a Python-based data engineering project that **extracts comprehensive energy metrics for all African countries** from the [Africa Energy Portal (AEP)](https://africa-energy-portal.org).  

Using **Cloudscraper**, the project bypasses Cloudflare protection and efficiently retrieves structured data (2000–2022) directly from the portal’s backend API.  
The data is cleaned, transformed into a tabular format, and exported to a **CSV file** — with optional storage in **MongoDB Atlas** for scalable cloud access and analysis.

---

## ⚙️ Key Features

- **Full African Coverage** — Data for all 54 African countries.  
- **Time-Series (2000–2022)** — Year-by-year energy data extraction.  
- **API-Level Extraction** — Uses Cloudscraper to fetch JSON directly from AEP’s API, bypassing Cloudflare blocks.  
- **Efficient and Lightweight** — No need for Selenium or browser automation.  
- **Clean CSV Export** — Data saved in a standardized, ready-to-analyze structure.  
- **MongoDB Atlas Integration** — Optional upload to cloud database for persistent storage.  
- **Comprehensive Energy Metrics** — Covers Access, Generation, Installed Capacity, and Consumption indicators.  
- **Modular Design** — Separate scripts for web scraping, database insertion, and orchestration.

---

## 🧰 Technology Stack

| Component | Description |
|------------|-------------|
| **Language** | Python 3.x |
| **Web Scraping** | Cloudscraper (requests-like interface with Cloudflare bypass) |
| **Data Handling** | Pandas, JSON |
| **Database (optional)** | MongoDB Atlas |
| **Database Library** | PyMongo |
| **Progress Tracking** | tqdm |
| **Environment** | Virtual environment (venv) |

---

## Project Structure
**Africa_Energy_Coverage_Data_Extractor**/

│

└── README.md - Project documentation

├── requirements.txt - List of required dependencies

├── scrape.py - Core scraping logic (AfricaEnergyPortalScraper)

├── mongodb.py - MongoDB connection and upload logic

├── main.py - Main execution script to run extraction and upload


---

##  Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.8+**
- **Google Chrome Browser**
- **Git** (for cloning the repository)

---

##  Setup and Installation

### 1️ Clone the Repository
```bash
git clone https://github.com/your-username/Africa_Energy_Coverage_Data_Extractor.git
cd Africa_Energy_Coverage_Data_Extractor
```
## Create A virtual Environment
```
python -m venv venv
```
## Activate the virtual Environment
```
Source/myenv/Scripts/Activate
```
## Install Independancies
```
pip install -r requirements.txt
```
--- 
# MongoDB Atlas Setup & Configuration

This project supports MongoDB Atlas as a cloud database for persistent storage.

## 1) Create a MongoDB Atlas Cluster

- Visit MongoDB Atlas and sign up (free tier available).

- Create a new cluster and database (e.g., AfricaEnergyData).

- Obtain your MongoDB connection string (URI).

## 2) Define Environment Variables

** Set the following environment variables before running the upload script: **
Variable	Description
```
MONGO_URI	MongoDB connection string
MONGO_DATABASE	Target database name (e.g., AfricaEnergyData)
Example (Windows PowerShell)
setx MONGO_URI "your_mongodb_connection_uri"
setx MONGO_DATABASE "AfricaEnergyData"
```
<img width="834" height="267" alt="image" src="https://github.com/user-attachments/assets/a2f3de73-b597-4189-93fa-627eedea869b" />

## Usage

Step 1: Run the Extraction Script - To perform scraping and generate a CSV file:


This executes the AfricaEnergyPortalScraper class, which:

- Iterates through all African countries.

- Extracts metrics for each year from 2000–2022.

- Saves the results in energy_data.csv.

Step 2: Upload Data to MongoDB (Optional)

Once data is extracted, you can upload the CSV data to MongoDB Atlas:
```
python main.py

```
This script:

- Extracts data  and Connects to your Atlas cluster.

- Inserts data into the specified collection under the configured database.

##  Data Schema (Output Format)

Each extracted record follows the structure below:

**Field	Description**
- country:	Name of the African country
- country_serial:	ISO3 country code
- metric:Energy metric (e.g., Access to Electricity, Generation)
- value:	Numeric value of the metric
- unit: Measurement unit (e.g., %, MW, kWh)
- sector:	Primary sector classification
- sub_sector: Sub-sector under which the metric falls
- sub_sub_sector: Further breakdown of the sector hierarchy
- source_link:	Direct source link on AEP
- source	Default: “Africa Energy Portal”
- year: Year of data observation (2000–2022)

####  Example Workflow Diagram

flowchart TD

    A[Start] --> B[Initialize Selenium WebDriver]
    B --> C[Iterate Years 2000–2022]
    C --> D[Extract Energy Metrics per Country]
    D --> E[Save to CSV]
    E --> F{Upload to MongoDB?}
    F -->|Yes| G[Insert Records into MongoDB Atlas]
    F -->|No| H[End Process]
    G --> H
    
---
 ## License

This project is licensed under the MIT License — see the LICENSE
 file for details.

## Contact

Author: Evalyn Njagi
Email: evalynnjagi02@gmail.com

LinkedIn: (https://www.linkedin.com/in/evalyn-njagi-115995168/)

For any inquiries or contributions, feel free to reach out or open an issue on GitHub.


