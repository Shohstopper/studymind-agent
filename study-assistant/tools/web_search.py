"""
Web Search Tool
Provides agents with the ability to search and fetch web content.
"""

import os
import urllib.parse
import urllib.request
import json
from google.adk.tools import FunctionTool


def search_web(query: str, num_results: int = 5) -> dict:
    """
    Search the web for study-related information using Google Custom Search API.
    
    Args:
        query: The search query string
        num_results: Number of results to return (max 10)
    
    Returns:
        Dictionary with search results containing titles, snippets, and URLs
    """
    api_key = os.getenv("GOOGLE_SEARCH_API_KEY", "")
    cx = os.getenv("GOOGLE_SEARCH_CX", "")
    
    if not api_key or not cx:
        # Fallback: return a helpful message if API not configured
        return {
            "status": "no_api_key",
            "message": "Web search requires GOOGLE_SEARCH_API_KEY and GOOGLE_SEARCH_CX environment variables.",
            "query": query,
            "suggestion": f"Please search manually for: {query}",
        }
    
    encoded_query = urllib.parse.quote(query)
    url = (
        f"https://www.googleapis.com/customsearch/v1"
        f"?key={api_key}&cx={cx}&q={encoded_query}&num={min(num_results, 10)}"
    )
    
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode())
        
        results = []
        for item in data.get("items", []):
            results.append({
                "title": item.get("title", ""),
                "snippet": item.get("snippet", ""),
                "url": item.get("link", ""),
            })
        
        return {
            "status": "success",
            "query": query,
            "results": results,
            "total_results": len(results),
        }
    except Exception as e:
        return {"status": "error", "message": str(e), "query": query}


def fetch_page_content(url: str) -> dict:
    """
    Fetch and extract text content from a URL for summarization.
    
    Args:
        url: The URL to fetch content from
    
    Returns:
        Dictionary with page title and text content
    """
    # Security: only allow http/https
    if not url.startswith(("http://", "https://")):
        return {"status": "error", "message": "Only HTTP/HTTPS URLs are allowed."}
    
    # Block internal/private URLs
    blocked = ["localhost", "127.0.0.1", "0.0.0.0", "192.168.", "10.", "172."]
    if any(b in url for b in blocked):
        return {"status": "error", "message": "Access to internal URLs is not permitted."}
    
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "StudyMind-Agent/1.0"})
        with urllib.request.urlopen(req, timeout=10) as response:
            raw = response.read().decode("utf-8", errors="ignore")
        
        # Basic HTML stripping
        import re
        text = re.sub(r"<script[^>]*>.*?</script>", "", raw, flags=re.DOTALL)
        text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.DOTALL)
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        
        # Limit to first 3000 chars to avoid token overflow
        return {
            "status": "success",
            "url": url,
            "content": text[:3000],
            "truncated": len(text) > 3000,
        }
    except Exception as e:
        return {"status": "error", "message": str(e), "url": url}
