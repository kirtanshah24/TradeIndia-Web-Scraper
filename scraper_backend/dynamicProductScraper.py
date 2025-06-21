import requests
import pandas as pd
from serpapi import GoogleSearch
from bs4 import BeautifulSoup
import time
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from requests.exceptions import SSLError
import warnings
import os
import json
from datetime import datetime
from dotenv import load_dotenv
import re

# Load environment variables from .env file
load_dotenv()

# Suppress warnings
warnings.filterwarnings("ignore", category=requests.packages.urllib3.exceptions.InsecureRequestWarning)

class DynamicTradeIndiaScraper:
    def __init__(self, api_key=None):
        """Initialize the scraper with optional API key."""
        self.api_key = api_key or os.getenv('SERPAPI_KEY')
        if not self.api_key:
            raise ValueError(
                "SERPAPI_KEY not found. Please set it in your .env file or pass it as a parameter.\n"
                "Example .env file:\n"
                "SERPAPI_KEY=your_api_key_here"
            )
        
        # Setup requests session with retry strategy
        self.session = requests.Session()
        retry = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
        self.session.mount("https://", HTTPAdapter(max_retries=retry))
        
        # Set headers to mimic a real browser
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })

    def is_valid_product_page(self, url, title):
        """Check if the URL and title suggest it's a valid product page."""
        # Exclude definitely non-product pages
        exclude_patterns = [
            r'/question-answer/',
            r'/blog/',
            r'/us/',
            r'/city-',
            r'/products/$',
            r'/products\?',
            r'/category/',
            r'/manufacturers/',
            r'/suppliers/',
            r'/seller/$',
            r'/seller\?',
            r'\.pdf$',
            r'\.doc$',
            r'\.docx$',
            r'Q\.',
            r'Question',
            r'Answer'
        ]
        
        # Check URL patterns
        for pattern in exclude_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return False
        
        # Check title patterns
        for pattern in exclude_patterns:
            if re.search(pattern, title, re.IGNORECASE):
                return False
        
        # Include pages that look like product pages
        include_patterns = [
            r'/products/.*\.html$',
            r'\.tradeindia\.com/.*\.html$',
            r'/seller/.*\.html$'
        ]
        
        for pattern in include_patterns:
            if re.search(pattern, url):
                return True
        
        return False

    def search_product_urls(self, product_name, max_results=50):
        """Search for product URLs using multiple strategies."""
        print(f"🔍 Searching for '{product_name}' products on TradeIndia...")
        
        product_links = []
        
        # Try different search strategies
        search_queries = [
            f'"{product_name}" site:tradeindia.com/products',
            f'{product_name} supplier site:tradeindia.com',
            f'{product_name} manufacturer site:tradeindia.com',
            f'{product_name} site:tradeindia.com -question -answer -blog',
            f'{product_name} site:tradeindia.com filetype:html'
        ]
        
        for query in search_queries:
            print(f"🔍 Trying: {query}")
            
            try:
                params = {
                    "engine": "google",
                    "q": query,
                    "api_key": self.api_key,
                    "num": 10
                }
                
                search = GoogleSearch(params)
                results = search.get_dict()
                
                # Extract product links from search results
                organic_results = results.get("organic_results", [])
                
                if not organic_results:
                    print(f"   ⚠️ No results for this query")
                    continue
                
                # Filter for valid product pages
                valid_links = []
                for result in organic_results:
                    link = result.get("link", "")
                    title = result.get("title", "")
                    
                    if "tradeindia.com" in link and self.is_valid_product_page(link, title):
                        valid_links.append({
                            "link": link,
                            "title": title
                        })
                
                print(f"   ✅ Found {len(valid_links)} valid product links")
                product_links.extend(valid_links)
                
                # Remove duplicates while preserving order
                seen_links = set()
                unique_links = []
                for link_info in product_links:
                    if link_info["link"] not in seen_links:
                        seen_links.add(link_info["link"])
                        unique_links.append(link_info)
                product_links = unique_links
                
                if len(product_links) >= max_results:
                    break
                
                time.sleep(1)  # Prevent API rate limiting
                
            except Exception as e:
                print(f"   ❌ Error with query: {e}")
                continue
        
        print(f" Found {len(product_links)} total valid product links")
        return product_links[:max_results]

    def extract_product_info(self, url):
        """Extract detailed product information from a TradeIndia product page using requests only."""
        try:
            print(f"   🔍 Fetching: {url}")
            
            response = self.session.get(url, timeout=15)
            
            if response.status_code != 200:
                print(f"   ❌ HTTP {response.status_code}")
                return None
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Extract product information
            product_data = {}
            
            # Product Name - try multiple selectors
            product_name_selectors = [
                "h1.product-title",
                "h1",
                ".product-title",
                ".product-name",
                "h2.product-title",
                ".product-details h1",
                ".product-info h1",
                "h1[class*='title']",
                ".product-header h1",
                ".product-name h1",
                "h1.product-name"
            ]
            
            product_name = "N/A"
            for selector in product_name_selectors:
                element = soup.select_one(selector)
                if element and element.text.strip():
                    product_name = element.text.strip()
                    break
            
            # If still N/A, try to extract from URL or page title
            if product_name == "N/A":
                # Try page title
                title_tag = soup.find("title")
                if title_tag and title_tag.text.strip():
                    title_text = title_tag.text.strip()
                    # Clean up the title
                    if " - " in title_text:
                        product_name = title_text.split(" - ")[0].strip()
                    else:
                        product_name = title_text
            
            product_data["Product Name"] = product_name
            
            # Company/Supplier Name
            company_selectors = [
                "a.company-url",
                ".company-name",
                ".supplier-name",
                ".seller-name",
                "a[href*='/seller/']",
                ".product-supplier",
                ".company-info a",
                ".supplier-info a",
                "a[class*='company']",
                "a[class*='supplier']",
                ".seller-info a",
                ".company-details a"
            ]
            
            company_name = "N/A"
            company_link = ""
            for selector in company_selectors:
                element = soup.select_one(selector)
                if element and element.text.strip():
                    company_name = element.text.strip()
                    company_link = element.get("href", "")
                    if company_link and not company_link.startswith("http"):
                        company_link = "https://www.tradeindia.com" + company_link
                    break
            
            product_data["Company Name"] = company_name
            product_data["Company Link"] = company_link
            
            # Location
            location_selectors = [
                "h3.erNFE",
                ".location",
                ".company-location",
                ".supplier-location",
                ".product-location",
                "[class*='location']",
                ".address",
                ".company-address",
                ".supplier-address",
                ".location-info",
                ".company-location-info"
            ]
            
            location = "N/A"
            for selector in location_selectors:
                element = soup.select_one(selector)
                if element and element.text.strip():
                    location = element.text.strip()
                    break
            
            product_data["Location"] = location
            
            # Price
            price_selectors = [
                "span.price-text",
                ".price",
                ".product-price",
                ".price-value",
                "[class*='price']",
                ".cost",
                ".product-cost",
                ".price-info",
                ".product-price-info"
            ]
            
            price = "N/A"
            for selector in price_selectors:
                element = soup.select_one(selector)
                if element and element.text.strip():
                    price = element.text.strip()
                    break
            
            product_data["Price (INR)"] = price
            
            # Trust Status
            trust_status = "Not Trusted"
            if soup.find("img", alt="Trusted Seller") or soup.find("span", string="Trusted Seller"):
                trust_status = "Trusted Seller"
            
            product_data["Trust Status"] = trust_status
            
            # Super Seller Status
            super_seller = "Not Super Seller"
            if soup.find("img", alt="Super Seller") or soup.find("span", string="Super Seller"):
                super_seller = "Super Seller"
            
            product_data["Super Seller"] = super_seller
            
            # Established Year
            established = soup.find("span", string="Established In:")
            if established and established.find_next("span"):
                product_data["Established Year"] = established.find_next("span").text.strip()
            else:
                product_data["Established Year"] = "N/A"
            
            # Business Type
            business_type = soup.find("span", class_="fSXCQo")
            if business_type:
                product_data["Business Type"] = business_type.text.strip()
            else:
                product_data["Business Type"] = "N/A"
            
            # Product Link
            product_data["Product Link"] = url
            
            # Scraped At
            product_data["Scraped At"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            print(f"   ✅ Extracted: {product_name} - {company_name}")
            return product_data
            
        except Exception as e:
            print(f"   ❌ Error extracting from {url}: {e}")
            return None

    def scrape_product(self, product_name, max_results=30, include_detailed_info=True):
        """Main method to scrape products by name."""
        print(f"🚀 Starting dynamic scraping for '{product_name}'...")
        
        # Step 1: Search for product URLs
        product_links = self.search_product_urls(product_name, max_results)
        
        if not product_links:
            return {"error": f"No valid product pages found for '{product_name}'"}
        
        # Step 2: Extract detailed product information
        all_products = []
        
        for i, link_info in enumerate(product_links, 1):
            print(f" Processing product {i}/{len(product_links)}: {link_info['title']}")
            
            product_info = self.extract_product_info(link_info['link'])
            if product_info:
                all_products.append(product_info)
            
            time.sleep(1)  # Prevent rate limiting
        
        # Step 3: Create results
        results = {
            "product_name": product_name,
            "total_results": len(all_products),
            "scraped_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "products": all_products
        }
        
        print(f"✅ Successfully scraped {len(all_products)} products for '{product_name}'")
        return results

    def generate_excel_data(self, results):
        """Generate Excel data for download."""
        if not results.get("products"):
            return None
        
        df = pd.DataFrame(results["products"])
        return df.to_excel(index=False, engine="openpyxl")

    def generate_json_data(self, results):
        """Generate JSON data for download."""
        if not results.get("products"):
            return None
        
        return json.dumps(results, indent=2, ensure_ascii=False)

# Example usage and testing
if __name__ == "__main__":
    try:
        # Test the scraper
        scraper = DynamicTradeIndiaScraper()
        
        # Test with steel
        results = scraper.scrape_product("steel", max_results=10, include_detailed_info=True)
        
        if "error" not in results:
            # Print summary
            print(f"\n Summary:")
            print(f"Product: {results['product_name']}")
            print(f"Total Results: {results['total_results']}")
            print(f"Scraped At: {results['scraped_at']}")
            
            # Show first few results
            if results['products']:
                print(f"\n🔍 First 3 results:")
                for i, product in enumerate(results['products'][:3], 1):
                    print(f"{i}. {product.get('Product Name', 'N/A')} - {product.get('Company Name', 'N/A')} ({product.get('Location', 'N/A')})")
        else:
            print(f"❌ {results['error']}")
            
    except ValueError as e:
        print(f"❌ Configuration Error: {e}")
        print("\n📝 To fix this:")
        print("1. Create a .env file in your project root")
        print("2. Add your SERPAPI_KEY to it:")
        print("   SERPAPI_KEY=your_actual_api_key_here")
        print("3. Make sure you have python-dotenv installed: pip install python-dotenv")
    except Exception as e:
        print(f"❌ Unexpected error: {e}") 