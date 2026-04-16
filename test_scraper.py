import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import quote_plus

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
TIMEOUT = 8

def test_indiamart(query):
    print(f"Testing IndiaMART for '{query}'...")
    url = f"https://dir.indiamart.com/search.mp?ss={quote_plus(query)}"
    headers = {"User-Agent": USER_AGENT}
    try:
        resp = requests.get(url, headers=headers, timeout=TIMEOUT)
        print(f"Status: {resp.status_code}")
        soup = BeautifulSoup(resp.text, "lxml")
        
        # Look for titles and prices
        items = soup.select('.m_item') or soup.select('.lst_cl') or soup.select('.card') or soup.select('.m-item')
        print(f"Found {len(items)} items.")
        
        for i, item in enumerate(items[:3]):
            title_tag = item.select_one('.pro_nm') or item.select_one('.pnm')
            price_tag = item.select_one('.prc') or item.select_one('.price')
            print(f"Item {i+1}: {title_tag.text if title_tag else 'No Title'} - {price_tag.text if price_tag else 'No Price'}")
            
    except Exception as e:
        print(f"Error: {e}")

def test_google(query):
    print(f"\nTesting Google Shopping for '{query}'...")
    url = f"https://www.google.com/search?q={quote_plus(query)}+price&tbm=shop"
    headers = {"User-Agent": USER_AGENT}
    try:
        resp = requests.get(url, headers=headers, timeout=TIMEOUT)
        print(f"Status: {resp.status_code}")
        soup = BeautifulSoup(resp.text, "lxml")
        
        items = soup.select('.sh-dgr__content') or soup.select('.sh-prfr__product-results-grid > div')
        print(f"Found {len(items)} items using standard selectors.")
        
        if len(items) == 0:
            items = soup.select('div[class*="product"]') or soup.select('div[class*="shopping"]')
            print(f"Found {len(items)} items using fallback selectors.")
            
        for i, item in enumerate(items[:3]):
            print(f"Item {i+1} HTML snippet: {str(item)[:200]}...")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_indiamart("macbook air")
    test_google("macbook air")
