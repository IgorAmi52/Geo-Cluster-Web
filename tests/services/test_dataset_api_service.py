import concurrent.futures
import pytest
from unittest.mock import MagicMock, patch
from app.services import DatasetApiService
from app.services import ApiService
from app.services import FileReader
from app.config import API_CONFIG, PMIDs_CONFIG

# Mocking FileReader to simulate reading IDs from a file


@patch("app.services.ApiService")
@patch("concurrent.futures.ThreadPoolExecutor")
def test_fetch_ds_ids(mock_executor, mock_api_service):
    """Test that fetch_ds_ids fetches dataset IDs correctly using threads."""

    # Mock API response for fetching PubMed IDs
    mock_api_service.get.return_value = {
        "linksets": [{"linksetdbs": [{"links": ["12345", "67890"]}]}]
    }

    # Create a single mock future
    mock_future = MagicMock(spec=concurrent.futures.Future)
    mock_future.result.return_value = ["12345", "67890"]

    # Mock the ThreadPoolExecutor to return our prepared future
    def mock_submit(func, *args, **kwargs):
        """Simulate future submission by returning a pre-created future."""
        return mock_future

    mock_executor.return_value.__enter__.return_value.submit = mock_submit

    # Mock as_completed to return our future
    mock_as_completed = MagicMock()
    mock_as_completed.return_value = [mock_future]

    # Patch concurrent.futures.as_completed
    with patch('concurrent.futures.as_completed', mock_as_completed):
        # Create the service instance
        api_service = DatasetApiService(mock_api_service)

        # Call the method
        ds_dict = api_service.fetch_ds_ids(["PAPER_ID"])

    # Validate the results
    assert ds_dict == {"PAPER_ID": ["12345", "67890"]}


@patch("app.services.ApiService")
@patch("concurrent.futures.ThreadPoolExecutor")
def test_fetch_ds_details(mock_executor, mock_api_service):
    """Test that fetch_ds_details fetches and processes data in batches."""

    # Prepare the mock API response
    mock_api_service.get.return_value = {
        "result": {
            "12345": {
                "title": "Dataset 1",
                "summary": "Summary 1",
                "taxon": "Taxon 1",
                "gdstype": "Type 1"
            },
            "67890": {
                "title": "Dataset 2",
                "summary": "Summary 2",
                "taxon": "Taxon 2",
                "gdstype": "Type 2"
            }
        }
    }

    # Create a single mock future
    mock_future = MagicMock(spec=concurrent.futures.Future)
    mock_future.result.return_value = {
        "12345": {
            **mock_api_service.get.return_value["result"]["12345"],
            "paper_ids": ["PAPER_1"]  # Add paper_ids to the mock response
        },
        "67890": {
            **mock_api_service.get.return_value["result"]["67890"],
            "paper_ids": ["PAPER_2"]  # Add paper_ids to the mock response
        }
    }

    # Mock the ThreadPoolExecutor to return our prepared future
    def mock_submit(func, *args, **kwargs):
        """Simulate future submission by returning a pre-created future."""
        return mock_future

    mock_executor.return_value.__enter__.return_value.submit = mock_submit

    # Mock as_completed to return our future
    mock_as_completed = MagicMock()
    mock_as_completed.return_value = [mock_future]

    # Patch concurrent.futures.as_completed
    with patch('concurrent.futures.as_completed', mock_as_completed):
        # Create the service instance
        api_service = DatasetApiService(mock_api_service)

        # Call the method with a mapping of paper IDs to dataset IDs
        paper_ds = {"PAPER_1": ["12345"], "PAPER_2": ["67890"]}
        ds_data = api_service.fetch_ds_details(paper_ds)

    # Validate the results
    assert len(ds_data) == 2, f"Expected 2 datasets, got {len(ds_data)}"
    assert "12345" in ds_data, "Dataset 12345 not found"
    assert "67890" in ds_data, "Dataset 67890 not found"
    assert ds_data["12345"]["title"] == "Dataset 1", "Incorrect data for 12345"
    assert ds_data["12345"]["paper_ids"] == [
        "PAPER_1"], "Incorrect paper IDs for 12345"
    assert ds_data["67890"]["summary"] == "Summary 2", "Incorrect data for 67890"
    assert ds_data["67890"]["paper_ids"] == [
        "PAPER_2"], "Incorrect paper IDs for 67890"


@patch("app.services.ApiService")
@patch("concurrent.futures.ThreadPoolExecutor")
def test_fetch_ds_ids_empty(mock_executor, mock_api_service):
    """Test that fetch_ds_ids handles an empty input list correctly."""
    # Mock the ThreadPoolExecutor to simulate no tasks being submitted
    mock_executor.return_value.__enter__.return_value.submit = MagicMock()
    mock_as_completed = MagicMock()
    mock_as_completed.return_value = []
    with patch('concurrent.futures.as_completed', mock_as_completed):
        api_service = DatasetApiService(mock_api_service)
        assert api_service.fetch_ds_ids([]) == {}


@patch("app.services.ApiService")
@patch("concurrent.futures.ThreadPoolExecutor")
def test_fetch_ds_details_empty(mock_executor, mock_api_service):
    """Test that fetch_ds_details handles an empty input list correctly."""
    api_service = DatasetApiService(mock_api_service)
    assert api_service.fetch_ds_details({}) == {}


@patch("app.services.ApiService")
@patch("concurrent.futures.ThreadPoolExecutor")
def test_fetch_ds_ids_api_failure(mock_executor, mock_api_service):
    """Test fetch_ds_ids gracefully handles an API failure."""
    # Simulate API failure by raising an exception
    mock_api_service.get.side_effect = Exception("API Error")

    # Mock the ThreadPoolExecutor to simulate task submission
    mock_future = MagicMock(spec=concurrent.futures.Future)
    mock_future.result.side_effect = Exception("API Error")
    mock_executor.return_value.__enter__.return_value.submit.return_value = mock_future

    mock_as_completed = MagicMock()
    mock_as_completed.return_value = [mock_future]
    with patch('concurrent.futures.as_completed', mock_as_completed):
        api_service = DatasetApiService(mock_api_service)
        ds_ids = api_service.fetch_ds_ids(["12345", "67890"])
        assert ds_ids == {}  # Ensure it returns an empty dictionary on failure
