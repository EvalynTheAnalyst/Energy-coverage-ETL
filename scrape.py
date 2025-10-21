import pandas as pd
import cloudscraper
from tqdm import tqdm
import time

scraper = cloudscraper.create_scraper()

BASE_URL = "https://africa-energy-portal.org/get-database-data"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
}

COUNTRIES = [
    "Algeria", "Angola", "Benin", "Botswana", "Burkina Faso", "Burundi",
    "Cameroon", "Cape Verde", "Central African Republic", "Chad", "Comoros",
    "Congo Democratic Republic", "Congo Republic", "Cote d'Ivoire", "Djibouti",
    "Egypt", "Equatorial Guinea", "Eritrea", "Eswatini", "Ethiopia", "Gabon",
    "Gambia", "Ghana", "Guinea", "Guinea Bissau", "Kenya", "Lesotho",
    "Liberia", "Libya", "Madagascar", "Malawi", "Mali", "Mauritania",
    "Mauritius", "Morocco", "Mozambique", "Namibia", "Niger", "Nigeria",
    "Rwanda", "Sao Tome and Principe", "Senegal", "Seychelles", "Sierra Leone",
    "Somalia", "South Africa", "South Sudan", "Sudan", "Tanzania", "Togo",
    "Tunisia", "Uganda", "Zambia", "Zimbabwe"
]

YEARS = [str(y) for y in range(2000, 2023)]


MAINGROUP= {
    "Electricity": {
        "Access": [
            "Population access to electricity-National (% of population)",
            "Population access to electricity-Rural (% of population)",
            "Population access to electricity-Urban (% of population)",
            "Population with access to electricity-National (millions of people)",
            "Population with access to electricity-Rural (millions of people)",
            "Population with access to electricity-Urban (millions of people)",
            "Population without access to electricity-National (millions of people)",
            "Population without access to electricity-Rural (millions of people)",
            "Population without access to electricity-Urban (millions of people)",
        ],
        "Generation": [
            "Electricity generated from fossil fuels (GWh)",
            "Electricity generated from hydropower (GWh)",
            "Electricity generated from nuclear power (GWh)",
            "Electricity generated from renewable sources (GWh)",
            "Electricity generation per capita (KWh)",
            "Electricity generation, Total (GWh)",
        ],
        "Consumption": [
            "Electricity final consumption (GWh)",
            "Electricity final consumption per capita (KWh)",
            "Electricity export (GWh)",
        ],
        "Installed_capacity": [
              "Electricity installed capacity in Nuclear (MW)",
              "Electricity installed capacity in Hydropower (MW)",
              "Electricity installed capacity in Wind (MW)",
              "Electricity installed capacity in Bioenergy (MW)",
              "Electricity installed capacity in Geothermal (MW)",
              "Electricity installed capacity in Non-renewable energy (MW)",
              "Electricity installed capacity in Fossil fuels (MW)",
              "Electricity installed capacity in other Non-renewable energy (MW)",
              "Electricity installed capacity in Solar (MW)",
              "Electricity installed capacity in Total renewable energy (MW)",
              "Electricity installed capacity, Total (MW)"

        ],
    },

    "Energy": {
        "Access": [
            "Energy intensity level of primary energy (MJ/2017 PPP GDP)",
            "Energy: Population with access to clean cooking fuels (% of population)",
            "Energy: Population without access to clean cooking fuels (millions of people)",
        ]
    },

    "Social and Economic": {
        "Population": [
            "Rural population (millions of people)",
            "Urban population (millions of people)",
            "Population; Total (millions of people)",
        ],
        "Economy": [
            "GDP (current US$)",
        ]
    }
}

def fetch_data():

    fetched_records = []

    for main_group, indicators_dict in MAINGROUP.items():
        for indicator_group, indicator_list in indicators_dict.items():
            for indicator in tqdm(indicator_list, desc=f"Fetching {main_group} → {indicator_group}"):
                payload = {
                    "mainGroup": main_group,
                    "mainIndicator[]": [indicator_group],
                    "mainIndicatorValue[]": [indicator],
                    "year[]": YEARS,
                    "name[]": COUNTRIES
                }

                try:
                    response = scraper.post(BASE_URL, data=payload, headers=HEADERS, timeout=40)
                    if response.status_code != 200:
                        print(f" {indicator}: HTTP {response.status_code}")
                        continue

                    try:
                        data = response.json()
                    except Exception as e:
                        print(f" Error {indicator, str(e)}: Non-JSON or blocked response.")
                        continue

                    if not data:
                        print(f" No data for {indicator}")
                        continue

                    # Flatten JSON structure
                    for metric in data:
                        for entry in metric.get("data", []):
                            fetched_records.append({
                                "country": entry.get("name"),
                                "country_serial": entry.get("id"),
                                "metric": metric.get("_id"),
                                "unit": entry.get("unit"),
                                "sector": main_group,
                                "sub_sector": indicator_group,
                                "source": entry.get("indicator_source"),
                                "year": entry.get("year"),
                                "value": entry.get("score"),
                                "source_link": f"https://africa-energy-portal.org{entry.get('url')}"
                            })

                    time.sleep(1.2)  # polite delay

                except Exception as e:
                    print(f"Error fetching {indicator}: {e}")



    df = pd.DataFrame(fetched_records)
    # Clean numeric column
    df["value"] = pd.to_numeric(df["value"], errors="coerce")  # convert to float, set invalids to NaN

    # drop empty or NaN values
    df = df.dropna(subset=["value"])

    if df.empty:
        print("No data retrieved.")
    else:
        print(f"\n Retrieved {len(df):,} rows across {df['country'].nunique()} countries and {df['year'].nunique()} years.")
        print(f"Unique metrics: {df['metric'].nunique()}")
        # main group and metrics
        print(f"Unique sectors: {df['sector'].nunique()}")
        print(f"Unique metrics: {df['metric'].nunique()}")
        print(" Sample data:")
        print(df.head(20))

        # Pivot years to columns
        pivot_df = df.pivot_table(
            index=["country", "country_serial", "metric", "unit", "sector", "sub_sector", "source", "source_link"],
            columns="year",
            values="value"
        ).reset_index()
        
    return pivot_df

def to_csv():
    csv = fetch_data().to_csv("AEP dataset", index=False)
    return csv



if __name__ == "__main__":
    print("\n Final structure:")
    print(fetch_data().head(20))
    to_csv()
    print("Data successfull saved to csv")
    
    