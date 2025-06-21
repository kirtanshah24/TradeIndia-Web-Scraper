import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

def scroll_to_end(driver):
    """Scrolls down to load all products dynamically."""
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)  # Wait for new data to load
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break  # No new content is loading
        last_height = new_height

def scrape_tradeindia(url):
    """Scrapes product and supplier details from TradeIndia."""
    options = Options()
    options.add_argument("--headless")  # Run in background
    options.add_argument("--disable-blink-features=AutomationControlled")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    driver.get(url)
    scroll_to_end(driver)  # Scroll to get all products
    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()  # Close browser

    data = []

    # Find all product containers
    listings = soup.find_all("div", class_="product-info-cnt")
    
    for listing in listings:
        try:
            product_name = listing.find("h2", class_="h2-title").text.strip()
            product_link = listing.find("h2", class_="h2-title").find("a")["href"]
            product_image = listing.find("div", class_="product-image").find("img")["src"]
            product_description = listing.find("span", class_="spec-value description").text.strip() if listing.find("span", class_="spec-value description") else "N/A"
            
            company_name = listing.find("a", class_="company-url").text.strip()
            company_link = listing.find("a", class_="company-url")["href"]
            location = listing.find("h3", class_="erNFE").text.strip()
            
            established = listing.find("span", string="Established In:")
            established_year = established.find_next("span").text.strip() if established else "N/A"
            
            business_type = listing.find("span", class_="fSXCQo").text.strip() if listing.find("span", class_="fSXCQo") else "N/A"

            trust_status = "Trusted Seller" if listing.find("img", alt="Trusted Seller") else "Not Trusted"
            super_seller = "Super Seller" if listing.find("img", alt="Super Seller") else "Not Super Seller"

            data.append({
                "Product Name": product_name,
                "Product Link": product_link,
                "Product Image": product_image,
                "Product Description": product_description,
                "Company Name": company_name,
                "Company Link": company_link,
                "Location": location,
                "Established Year": established_year,
                "Business Type": business_type,
                "Trust Status": trust_status,
                "Super Seller": super_seller,
                "Scraped URL": url  # Store the source URL for reference
            })

        except Exception as e:
            print(f"Error scraping product: {e}")

    return data

if __name__ == "__main__":
    # Load URLs from the Excel file
    input_file = "latestTradeIndia_Industry_Products.xlsx"  # Update this with your actual Excel file name
    output_file = "final_data.xlsx"

    df_urls = pd.read_excel(input_file)  # Read the Excel file
    all_data = []

    # Loop through each URL
    for index, row in df_urls.iterrows():
        url = row["Product Link"]  # Assuming the column is named 'product url'
        print(f"🔄 Scraping: {url} ({index + 1}/{len(df_urls)})")
        scraped_data = scrape_tradeindia(url)
        all_data.extend(scraped_data)

        # Save progress after each URL
        pd.DataFrame(all_data).to_excel(output_file, index=False)

    print("✅ Scraping completed! Data saved to", output_file)
