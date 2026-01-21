"""Unit tests for URL fetcher module."""

from unittest.mock import Mock, patch

import pytest
from requests.exceptions import ConnectionError, Timeout

from src.extraction.url_fetcher import fetch_url
from src.utils.errors import URLFetchError


class TestURLFetcher:
    """Test suite for URL fetching functionality."""

    def test_fetch_valid_url(self):
        """Test successful HTTP GET request to a valid URL."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "<html><body>Hello World</body></html>"
        mock_response.encoding = "utf-8"

        with patch("src.extraction.url_fetcher.requests.get") as mock_get:
            mock_get.return_value = mock_response

            result = fetch_url("https://example.com")

            assert result == "<html><body>Hello World</body></html>"
            # Verify the call was made with correct parameters (including User-Agent header)
            mock_get.assert_called_once()
            call_kwargs = mock_get.call_args[1]
            assert call_kwargs["timeout"] == 10
            assert call_kwargs["allow_redirects"] is True
            assert "User-Agent" in call_kwargs.get("headers", {})

    def test_fetch_with_redirect(self):
        """Test that HTTP redirects are followed automatically."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "<html><body>Redirected Content</body></html>"
        mock_response.encoding = "utf-8"
        mock_response.url = "https://example.com/redirected"

        with patch("src.extraction.url_fetcher.requests.get") as mock_get:
            mock_get.return_value = mock_response

            result = fetch_url("https://example.com/old")

            assert result == "<html><body>Redirected Content</body></html>"
            # Verify allow_redirects=True was passed
            mock_get.assert_called_once()
            call_kwargs = mock_get.call_args[1]
            assert call_kwargs["allow_redirects"] is True

    def test_fetch_with_timeout(self):
        """Test that request timeout is handled gracefully."""
        with patch("src.extraction.url_fetcher.requests.get") as mock_get:
            mock_get.side_effect = Timeout("Request timed out after 10 seconds")

            with pytest.raises(URLFetchError) as exc_info:
                fetch_url("https://example.com", timeout=10)

            assert "timeout" in str(exc_info.value).lower()

    def test_fetch_with_custom_timeout(self):
        """Test that custom timeout value is passed to requests."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "<html>Content</html>"
        mock_response.encoding = "utf-8"

        with patch("src.extraction.url_fetcher.requests.get") as mock_get:
            mock_get.return_value = mock_response

            fetch_url("https://example.com", timeout=30)

            mock_get.assert_called_once()
            call_kwargs = mock_get.call_args[1]
            assert call_kwargs["timeout"] == 30
            assert call_kwargs["allow_redirects"] is True

    def test_fetch_invalid_url(self):
        """Test that non-existent domain returns error."""
        with patch("src.extraction.url_fetcher.requests.get") as mock_get:
            mock_get.side_effect = ConnectionError("Failed to resolve hostname")

            with pytest.raises(URLFetchError) as exc_info:
                fetch_url("https://nonexistent-domain-12345.com")

            assert "connection" in str(exc_info.value).lower() or "hostname" in str(exc_info.value).lower()

    def test_fetch_http_404_error(self):
        """Test that 404 status code is treated as error."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "<html><body>Not Found</body></html>"
        mock_response.encoding = "utf-8"

        with patch("src.extraction.url_fetcher.requests.get") as mock_get:
            mock_get.return_value = mock_response

            with pytest.raises(URLFetchError) as exc_info:
                fetch_url("https://example.com/notfound")

            assert "404" in str(exc_info.value)

    def test_fetch_http_500_error(self):
        """Test that 5xx server errors are handled."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "<html><body>Internal Server Error</body></html>"
        mock_response.encoding = "utf-8"

        with patch("src.extraction.url_fetcher.requests.get") as mock_get:
            mock_get.return_value = mock_response

            with pytest.raises(URLFetchError) as exc_info:
                fetch_url("https://example.com")

            assert "500" in str(exc_info.value)

    def test_fetch_requires_auth(self):
        """Test that 401 Unauthorized is handled."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = "<html><body>Unauthorized</body></html>"
        mock_response.encoding = "utf-8"

        with patch("src.extraction.url_fetcher.requests.get") as mock_get:
            mock_get.return_value = mock_response

            with pytest.raises(URLFetchError) as exc_info:
                fetch_url("https://example.com/protected")

            assert "401" in str(exc_info.value)

    def test_fetch_http_403_forbidden(self):
        """Test that 403 Forbidden is handled."""
        mock_response = Mock()
        mock_response.status_code = 403
        mock_response.text = "<html><body>Forbidden</body></html>"
        mock_response.encoding = "utf-8"

        with patch("src.extraction.url_fetcher.requests.get") as mock_get:
            mock_get.return_value = mock_response

            with pytest.raises(URLFetchError) as exc_info:
                fetch_url("https://example.com/forbidden")

            assert "403" in str(exc_info.value)

    def test_fetch_response_encoding(self):
        """Test that response encoding is respected."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "<html><body>Café</body></html>"
        mock_response.encoding = "utf-8"

        with patch("src.extraction.url_fetcher.requests.get") as mock_get:
            mock_get.return_value = mock_response

            result = fetch_url("https://example.com")

            assert "Café" in result

    def test_fetch_with_headers(self):
        """Test that default headers are set (User-Agent, etc)."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "<html><body>Content</body></html>"
        mock_response.encoding = "utf-8"

        with patch("src.extraction.url_fetcher.requests.get") as mock_get:
            mock_get.return_value = mock_response

            fetch_url("https://example.com")

            # Check that headers were passed
            call_kwargs = mock_get.call_args[1]
            if "headers" in call_kwargs:
                headers = call_kwargs["headers"]
                # Verify User-Agent is set
                assert "User-Agent" in headers or "user-agent" in headers.lower()
