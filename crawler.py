import requests
from bs4 import BeautifulSoup
import os
import time
import json

DATA_FOLDER = "data"
if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

# Orodha ya makala 50 za Wikipedia (unaweza kuongeza zaidi)
TOPICS = [
    "Python_(programming_language)", "Search_engine", "Web_crawler",
    "Machine_learning", "Artificial_intelligence", "Data_science",
    "Natural_language_processing", "Information_retrieval", "Web_scraping",
    "Flask_(web_framework)", "Django_(web_framework)", "JavaScript",
    "HTML", "CSS", "SQL", "NoSQL", "MongoDB", "PostgreSQL",
    "Linux", "Windows", "macOS", "Android_(operating_system)",
    "IOS", "Cloud_computing", "Amazon_Web_Services", "Microsoft_Azure",
    "Google_Cloud_Platform", "Docker_(software)", "Kubernetes",
    "Git", "GitHub", "Computer_network", "Internet",
    "World_Wide_Web", "HTTP", "HTTPS", "Domain_Name_System",
    "Transmission_Control_Protocol", "IP_address", "Router_(computing)",
    "Computer_security", "Cryptography", "Blockchain",
    "Bitcoin", "Ethereum", "Virtual_reality", "Augmented_reality",
    "Internet_of_things", "Big_data", "Data_mining", "Codeunion software", "Binance", "oil systems", 
    "petrolium system, inventory systems", "tesla roadster 8"
]

URLS = [f"https://en.wikipedia.org/wiki/{topic}" for topic in TOPICS]

def fetch_and_clean_page(url):
    try:
        print(f"⬇️  Downloading: {url}")
        response = requests.get(url, headers=HEADERS, timeout=30, verify=False)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        for script_or_style in soup(['script', 'style']):
            script_or_style.decompose()
        text = soup.get_text(separator=' ', strip=True)

        filename = url.split('/')[-1]
        if not filename:
            filename = "index"
        filename = filename.replace('_', ' ') + ".txt"
        filepath = os.path.join(DATA_FOLDER, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(text)

        print(f"✅ Saved: {filename} ({len(text)} characters)")
        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print(f"🚀 Crawling {len(URLS)} pages...")
    successful = 0
    for i, url in enumerate(URLS, 1):
        print(f"\n[{i}/{len(URLS)}]")
        if fetch_and_clean_page(url):
            successful += 1
        time.sleep(1)

    print(f"\n✅ Done! {successful}/{len(URLS)} pages saved.")

if __name__ == "__main__":
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    main()