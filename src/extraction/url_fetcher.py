"""URL fetcher module for retrieving HTML content from web pages."""

import requests
from requests.exceptions import ConnectionError, RequestException, Timeout

from src.utils.errors import URLFetchError


def fetch_url(url: str, timeout: int = 10) -> str:
    """
    Fetch HTML content from a given URL.

    Args:
        url: The URL to fetch (e.g., "https://example.com")
        timeout: Request timeout in seconds (default: 10)

    Returns:
        str: The HTML content of the page

    Raises:
        URLFetchError: If the URL cannot be fetched or returns an error status

    Examples:
        >>> html = fetch_url("https://example.com")
        >>> "<html>" in html
        True
    """
    try:
        # Set default User-Agent header
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

        # Perform GET request with redirects allowed
        response = requests.get(url, timeout=timeout, allow_redirects=True, headers=headers)

        # Check for HTTP errors
        if response.status_code == 401:
            raise URLFetchError(f"Authentication required (401): {url}")
        elif response.status_code == 403:
            raise URLFetchError(f"Access forbidden (403): {url}")
        elif response.status_code == 404:
            raise URLFetchError(f"Page not found (404): {url}")
        elif response.status_code >= 500:
            raise URLFetchError(f"Server error ({response.status_code}): {url}")
        elif response.status_code >= 400:
            raise URLFetchError(f"Client error ({response.status_code}): {url}")

        # Raise exception for bad status codes
        response.raise_for_status()

        return response.text

    except Timeout as e:
        raise URLFetchError(f"Request timeout after {timeout} seconds: {url}") from e
    except ConnectionError as e:
        raise URLFetchError(f"Connection failed (hostname resolution or network error): {url}") from e
    except RequestException as e:
        raise URLFetchError(f"Failed to fetch URL {url}: {str(e)}") from e
    except Exception as e:
        raise URLFetchError(f"Unexpected error fetching {url}: {str(e)}") from e
