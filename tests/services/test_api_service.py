import pytest
from unittest.mock import patch, MagicMock
from app.services import ApiService


@pytest.fixture
def api_service():
    """Fixture to create an instance of ApiService."""
    return ApiService(base_url="https://api.example.com", api_key="test_api_key")


@patch("requests.get")  # Mock requests.get
def test_get_success(mock_get, api_service):
    """Test successful GET request."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": "test_response"}
    mock_get.return_value = mock_response

    result = api_service.get("/test-endpoint", {"param": "value"})

    assert result == {"data": "test_response"}
    mock_get.assert_called_once_with(
        "https://api.example.com/test-endpoint",
        params={"param": "value", "api_key": "test_api_key"}
    )


@patch("requests.get")
def test_get_with_no_base_url(mock_get):
    """Test that an error is raised when base_url is missing."""
    api_service = ApiService(base_url=None)

    with pytest.raises(ValueError, match="Base URL is not configured."):
        api_service.get("/test-endpoint")


@patch("requests.get")
def test_get_http_error(mock_get, api_service):
    """Test API request when an HTTP error occurs."""
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.raise_for_status.side_effect = Exception("404 Not Found")
    mock_get.return_value = mock_response

    with pytest.raises(Exception, match="404 Not Found"):
        api_service.get("/invalid-endpoint")

    mock_get.assert_called_once_with(
        "https://api.example.com/invalid-endpoint",
        params={"api_key": "test_api_key"}
    )
