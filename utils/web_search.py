from duckduckgo_search import DDGS

def perform_web_search(query: str, num_results: int = 3) -> str:
    """
    Performs a web search using DuckDuckGo and returns a formatted string of results.
    Args:
        query (str): The search query.
        num_results (int): The number of results to return.
    Returns:
        str: A string containing the search results (title, link, snippet).
    """
    print(f"Performing web search for: {query}")
    try:
        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=num_results)
            if not results:
                return "No results found."

            output = f"Search results for '{query}':\n"
            for i, r in enumerate(results):
                output += f"{i+1}. Title: {r['title']}\n   Link: {r['href']}\n   Snippet: {r['body']}\n---\n"
            return output
    except Exception as e:
        return f"Error during web search: {str(e)}"
