import httpx

def search_blog(q):
    """Search Simon Willison blog"""
    response = httpx.get("https://simonwillison.net/search/", params={"q": q})
    return response.text[:2000]  # Limit response size 