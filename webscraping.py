import requests # let python talk to the internet
import json, os, time
from urllib.parse import urljoin
from selenium import webdriver # open and control a browser
from selenium.webdriver.chrome.service import Service # Start and manage chrome driver
from webdriver_manager.chrome import ChromeDriverManager # set the right chrome driver for your browser 
import cloudscraper

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))\

base_url ="https://africa-energy-portal.org"
API = "get-database-data"

def load_session():
    art = json.load(open("session_artifacts.json"))
    return art['cookies'], art['ua']

def fetch_one():
    cookies, ua = load_session()
    s = cloudscraper.create_scraper()
    headers = {
        "User-Agent": ua,
        "Accept": "application/json, text/plain, */*",
        "Origin": base_url,
        "Referer": base_url + "/database",
        # add if DevTools shows it:
        # "X-Requested-With": "XMLHttpRequest",
    }

    payload = {
        "mainGroup": "Electricity",
        "mainIndicator": ["Access", "Supply", "Technical"],
        "mainIndicatorValue": [
            "Population access to electricity-National (% of population)",
            "Population access to electricity-Rural (% of population)",
            "Population access to electricity-Urban (% of population)",
            "Population with access to electricity-National (millions of people)",
            "Population with access to electricity-Rural (millions of people)",
            "Population with access to electricity-Urban (millions of people)",
            "Population without access to electricity-National (millions of people)",
            "Population without access to electricity-Rural (millions of people)",
            "Population without access to electricity-Urban (millions of people)",
            "Electricity export (GWh)",
            "Electricity final consumption (GWh)",
            "Electricity final consumption per capita (KWh)",
            "Electricity generated from biofuels and waste (GWh)",
            "Electricity generated from fossil fuels (GWh)",
            "Electricity generated from geothermal energy (GWh)",
            "Electricity generated from hydropower (GWh)",
            "Electricity generated from nuclear power (GWh)",
            "Electricity generated from renewable sources (GWh)",
            "Electricity generated from solar, wind, tide, wave and other sources (GWh)",
            "Electricity generation per capita (KWh)",
            "Electricity generation, Total (GWh)",
            "Electricity import (GWh)",
            "Electricity: Net imports ( GWh )",
            "Electricity installed capacity in Bioenergy (MW)",
            "Electricity installed capacity in Fossil fuels (MW)",
            "Electricity installed capacity in Geothermal (MW)",
            "Electricity installed capacity in Hydropower (MW)",
            "Electricity installed capacity in Non-renewable energy (MW)",
            "Electricity installed capacity in Nuclear (MW)",
            "Electricity installed capacity in Solar (MW)",
            "Electricity installed capacity in Total renewable energy (MW)",
            "Electricity installed capacity in Wind (MW)",
            "Electricity installed capacity in other Non-renewable energy (MW)",
            "Electricity installed capacity, Total (MW)"
        ],
        "year": [str(y) for y in range(2000, 2023)],
        "name": [
            "Algeria","Angola","Benin","Botswana","Burkina Faso","Burundi","Cameroon","Cape Verde",
            "Central African Republic","Chad","Comoros","Congo Democratic Republic","Congo Republic",
            "Cote d'Ivoire","Djibouti","Egypt","Equatorial Guinea","Eritrea","Eswatini","Ethiopia",
            "Gabon","Gambia","Ghana","Guinea","Guinea Bissau","Kenya","Lesotho","Liberia","Libya",
            "Madagascar","Malawi","Mali","Mauritania","Mauritius","Morocco","Mozambique","Namibia",
            "Niger","Nigeria","Rwanda","Sao Tome and Principe","Senegal","Seychelles","Sierra Leone",
            "Somalia","South Africa","South Sudan","Sudan","Tanzania","Togo","Tunisia","Uganda","Zambia","Zimbabwe"
        ]
    }
    url = urljoin(base_url, API)

    # If DevTools shows **POST** with JSON:
    r = s.post(url, json=payload, headers=headers, cookies=cookies, timeout=60)
   
    print("status:", r.status_code)
    r.raise_for_status()
    data = r.json()
    print(json.dumps(data[:2] if isinstance(data, list) else data, indent=2))
    return data

if __name__ == "__main__":
    fetch_one()





