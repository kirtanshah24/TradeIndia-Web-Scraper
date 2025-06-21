import requests
import pandas as pd
from serpapi import GoogleSearch
from bs4 import BeautifulSoup
import time
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry  # type: ignore
from requests.exceptions import SSLError
import warnings
import os

# Suppress InsecureRequestWarning
warnings.filterwarnings("ignore", category=requests.packages.urllib3.exceptions.InsecureRequestWarning)

SERPAPI_KEY = os.environ['API_KEY']

# List of industries to search for
industries = [
    "automotive", "lighting", "construction", "agriculture",
    "oil & gas", "renewable energy", "heavy machinery"
]

# Store all extracted product details
all_products = []

# Setup a requests session with retry strategy
session = requests.Session()
retry = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
session.mount("https://", HTTPAdapter(max_retries=retry))

for industry in industries:
    print(f"🔍 Searching for {industry} industry products...")

    product_links = []  # Store all product links for this industry

    # Use pagination to get more results (fetch up to 100 results)
    for start in range(0, 100, 10):  # Fetch 10 results per request
        params = {
            "engine": "google",
            "q": f"{industry} site:tradeindia.com",
            "api_key": SERPAPI_KEY,
            "num": 10,  # Get 10 results per page
            "start": start  # Pagination: 0, 10, 20, ..., 100
        }

        search = GoogleSearch(params)
        results = search.get_dict()

        # Extract product links from search results
        links = [res["link"] for res in results.get("organic_results", []) if "tradeindia.com" in res.get("link", "")]

        if not links:
            print(f"⚠️ No more TradeIndia product links found for {industry} (page {start // 10 + 1}).")
            break  # Stop pagination if no more results

        product_links.extend(links)
        time.sleep(1)  # Prevents hitting API rate limits

    print(f"📌 Found {len(product_links)} product links for {industry}. Extracting details...")

    for link in product_links:
        try:
            # Request with SSL verification enabled
            response = session.get(link, verify=True, timeout=10)

            if response.status_code != 200:
                print(f"❌ Failed to fetch TradeIndia product page: {link}")
                continue

            # Parse HTML using BeautifulSoup
            soup = BeautifulSoup(response.text, "html.parser")

            # Extract product details safely
            def extract_text(tag, class_name=None, search_text=None):
                if search_text:
                    element = soup.find(string=search_text)
                    return element.find_next().text.strip() if element and element.find_next() else "N/A"
                found_tag = soup.find(tag, class_=class_name)
                return found_tag.text.strip() if found_tag else "N/A"

            product_data = {
                "Industry": industry,
                "Product Name": extract_text("h2"),
                "Price (INR)": extract_text("span", "price-text"),
                "MOQ": extract_text(None, search_text="MOQ"),
                "Shape": extract_text(None, search_text="Shape"),
                "Light Color": extract_text(None, search_text="Light Color"),
                "Material": extract_text(None, search_text="Material"),
                "Power Factor": extract_text(None, search_text="Power Factor"),
                "Application": extract_text(None, search_text="Application"),
                "Supplier": extract_text("a", "company-url"),
                "Location": extract_text("h3", "erNFE"),
                "Product Link": link
            }

            all_products.append(product_data)

            # Delay to prevent blocking
            time.sleep(2)

        except SSLError as e:
            print(f"⚠️ SSL Error for {link}: {e}")
            continue  # Skip this link

        except requests.exceptions.RequestException as e:
            print(f"⚠️ Network error for {link}: {e}")
            continue  # Skip this link

        except Exception as e:
            print(f"⚠️ Error extracting data from {link}: {e}")
            continue  # Skip this link

# Convert to DataFrame and save to Excel
df = pd.DataFrame(all_products)
output_file = "tradeIndia_Industry_Products.xlsx"
df.to_excel(output_file, index=False, engine="openpyxl")  

print(f"✅ Extracted {len(all_products)} product entries and saved successfully at {output_file}!")