from serpapi import GoogleSearch
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

def fetch_market_prices(query: str) -> list[dict]:
    """
    Primary data fetching service using SerpAPI (Google Shopping).
    Returns a normalized list of product dicts as per project rules.
    """
    if not settings.SERPAPI_KEY or "your-serpapi-key" in settings.SERPAPI_KEY:
        logger.warning("SerpAPI Key not configured. Skipping API call.")
        return []

    params = {
        "engine": "google_shopping",
        "q": query,
        "api_key": settings.SERPAPI_KEY,
        "hl": "en",
        "gl": "in", # Target India market
    }

    try:
        search = GoogleSearch(params)
        results = search.get_dict()
        
        shopping_results = results.get("shopping_results", [])
        if not shopping_results:
            logger.info(f"SerpAPI returned no results for query: {query}")
            return []

        normalized_results = []
        for item in shopping_results[:20]: # Limit to top 20
            # Strictly following the project rule structure: title, price, source, url
            # Adding 'image' as a bonus for better UI
            normalized_results.append({
                "title": item.get("title"),
                "price": item.get("price"),
                "source": item.get("source"),
                "url": item.get("link"),
                "image": item.get("thumbnail")
            })
            
        return normalized_results
    except Exception as e:
        logger.error(f"SerpAPI Error: {e}")
        return []
