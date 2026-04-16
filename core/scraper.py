import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import quote_plus

# Stable mobile user agent
HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def get_headers():
    return HEADERS

def scrape_indiamart(query: str) -> list[dict]:
    """
    Limited scraping for IndiaMART as per project rules.
    """
    try:
        url = f"https://www.indiamart.com/search.mp?ss={quote_plus(query)}"
        resp = requests.get(url, headers=get_headers(), timeout=10)
        resp.raise_for_status()
        
        soup = BeautifulSoup(resp.text, "lxml")
        results = []
        
        # Target common listing elements
        items = soup.select('.m_item') or soup.select('.lst_cl') or soup.select('.card')
        for item in items[:10]: # Limit as per rules (top 10-20)
            title = item.select_one('.pro_nm') or item.select_one('h2') or item.select_one('.pnm')
            price = item.select_one('.prc') or item.select_one('.price')
            url_tag = item.select_one('a')
            img = item.select_one('img')
            
            if title:
                link = url_tag['href'] if url_tag and url_tag.has_attr('href') else url
                if not link.startswith('http'): link = "https://www.indiamart.com" + link
                
                results.append({
                    "title": title.text.strip(),
                    "price": price.text.strip() if price else "Price on Request",
                    "source": "IndiaMART",
                    "url": link,
                    "image": img['src'] if img and img.has_attr('src') else "https://via.placeholder.com/200?text=IndiaMART"
                })
        return results
    except Exception:
        return []

def scrape_snapdeal(query: str) -> list[dict]:
    """
    Limited scraping for Snapdeal as per project rules.
    """
    try:
        url = f"https://www.snapdeal.com/search?keyword={quote_plus(query)}"
        resp = requests.get(url, headers=get_headers(), timeout=10)
        if resp.status_code != 200: return []
        
        soup = BeautifulSoup(resp.text, "lxml")
        results = []
        items = soup.select('.product-tuple-listing')
        for item in items[:8]:
            title = item.select_one('.product-title')
            price = item.select_one('.product-price')
            url_tag = item.select_one('a')
            img = item.select_one('img')
            if title and price:
                results.append({
                    "title": title.get_text(strip=True),
                    "price": price.get_text(strip=True).replace("Rs.", "₹").strip(),
                    "source": "Snapdeal",
                    "url": url_tag['href'] if url_tag else url,
                    "image": img.get('data-src') or img.get('src') or "https://via.placeholder.com/200?text=Snapdeal"
                })
        return results
    except Exception:
        return []

def scrape_fallback_all(query: str) -> list[dict]:
    """
    Aggregates results from allowed scraping sources only.
    """
    results = []
    results.extend(scrape_indiamart(query))
    results.extend(scrape_snapdeal(query))
    return results

def normalize_price(price_str: str) -> float:
    """Helper to extract float value from price string."""
    try:
        clean = "".join(re.findall(r'[\d.]+', price_str.replace(',', '')))
        return float(clean) if clean else 0.0
    except:
        return 0.0

def get_price_range(results: list[dict]) -> tuple[str, str]:
    """Calculates min and max price from normalized results."""
    prices = []
    for res in results:
        p = normalize_price(res['price'])
        if p > 0:
            prices.append(p)
            
    if not prices:
        return "N/A", "N/A"
        
    p_min = min(prices)
    p_max = max(prices)
    
    # Check if majority of sources use Rupee
    all_prices = "".join([r['price'] for r in results]).lower()
    if "₹" in all_prices or "rs" in all_prices:
        return f"₹{p_min:,.0f}", f"₹{p_max:,.0f}"
    else:
        return f"${p_min:,.2f}", f"${p_max:,.2f}"
