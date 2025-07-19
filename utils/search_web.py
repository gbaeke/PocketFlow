"""
DuckDuckGo web search utility function.
"""
import requests
from bs4 import BeautifulSoup
import time


def search_web(query, max_results=3):
    """
    Search the web using DuckDuckGo and return formatted results.
    
    Args:
        query (str): The search query
        max_results (int): Maximum number of results to return
        
    Returns:
        str: Formatted search results
    """
    try:
        # Use DuckDuckGo search
        search_url = "https://duckduckgo.com/html/"
        params = {
            'q': query,
            'b': '',  # no ads
            'kl': 'us-en',  # language
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        
        response = requests.get(search_url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find search results
        results = []
        result_elements = soup.find_all('div', class_='result')
        
        for i, element in enumerate(result_elements[:max_results]):
            try:
                # Extract title and snippet
                title_elem = element.find('a', class_='result__a')
                snippet_elem = element.find('a', class_='result__snippet')
                
                if title_elem and snippet_elem:
                    title = title_elem.get_text().strip()
                    snippet = snippet_elem.get_text().strip()
                    url = title_elem.get('href', '')
                    
                    results.append({
                        'title': title,
                        'snippet': snippet,
                        'url': url
                    })
            except Exception as e:
                print(f"Error parsing result {i}: {e}")
                continue
        
        # Format results
        if not results:
            return f"No results found for query: {query}"
        
        formatted_results = f"Search results for '{query}':\n\n"
        for i, result in enumerate(results, 1):
            formatted_results += f"{i}. {result['title']}\n"
            formatted_results += f"   {result['snippet']}\n"
            if result['url']:
                formatted_results += f"   URL: {result['url']}\n"
            formatted_results += "\n"
        
        return formatted_results
        
    except requests.RequestException as e:
        return f"Search error for '{query}': Network request failed - {e}"
    except Exception as e:
        return f"Search error for '{query}': {e}"


def search_technology_info(technology_name):
    """
    Search for specific technology information including latest versions.
    
    Args:
        technology_name (str): Name of the technology to search
        
    Returns:
        str: Formatted search results with technology information
    """
    queries = [
        f"{technology_name} latest version 2024 2025",
        f"{technology_name} recent updates features",
        f"what is {technology_name} programming language framework"
    ]
    
    all_results = []
    for query in queries:
        results = search_web(query, max_results=2)
        all_results.append(results)
        time.sleep(1)  # Be respectful to the service
    
    combined_results = f"Research results for {technology_name}:\n\n"
    combined_results += "\n".join(all_results)
    
    return combined_results


if __name__ == "__main__":
    # Test the function
    test_query = "Python programming language latest version"
    try:
        result = search_web(test_query)
        print("Test successful!")
        print(f"Query: {test_query}")
        print(f"Results:\n{result}")
    except Exception as e:
        print(f"Test failed: {e}")
