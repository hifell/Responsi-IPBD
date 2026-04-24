from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_FILE = os.path.join(DATA_DIR, "wired_data.json")

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

print("Mulai scraping...")

options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

driver.get("https://www.wired.com")
time.sleep(5)

for i in range(3):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)

elements = driver.find_elements(By.TAG_NAME, "a")
article_links = []
for el in elements:
    href = el.get_attribute("href")
    if href and "/story/" in href and href not in article_links:
        article_links.append(href)
    if len(article_links) >= 25: 
        break

articles_data = []

for link in article_links:
    try:
        driver.get(link)
        wait = WebDriverWait(driver, 5)
        title = driver.title.replace(" | WIRED", "").strip()
        author = "Unknown"
        selectors = ['a[rel="author"]', '[class*="Byline"] a', '[data-testid="Byline"] a']
        for selector in selectors:
            try:
                el = driver.find_element(By.CSS_SELECTOR, selector)
                if el.text.strip():
                    raw_author = el.text.strip()
                    author = raw_author.replace("By ", "").replace("by ", "").strip()
                    break
            except: continue
        description = "N/A"
        try:
            desc_element = driver.find_element(By.CSS_SELECTOR, 'meta[name="description"]')
            description = desc_element.get_attribute("content")
        except:
            description = "N/A"
        articles_data.append({
            "title": title,
            "url": link,
            "description": description,
            "author": author,
            "scraped_at": datetime.now().isoformat(),
            "source": "Wired.com"
        })
        print(f"Berhasil scrape: {title[:30]}...")
        
    except Exception as e:
        print(f"Gagal akses {link}: {e}")
final_output = [{
    "session_id": f"wired_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
    "timestamp": datetime.now().isoformat(),
    "articles_count": len(articles_data),
    "articles": articles_data
}]

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(final_output, f, indent=2)

print(f"\nData disimpan di: {OUTPUT_FILE}")
driver.quit()