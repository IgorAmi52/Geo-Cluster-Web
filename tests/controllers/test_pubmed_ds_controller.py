import pytest
from unittest.mock import MagicMock
from app.controllers.pubmed_ds_controller import PubmedDSController
from app.services import DatasetApiService, FileReader


@pytest.fixture
def mock_api_service():
    mock = MagicMock(spec=DatasetApiService)
    mock.fetch_ds_ids.return_value = ["GSE12345", "GSE67890"]
    mock.fetch_ds_details.return_value = {
        "GSE12345": {"title": "Dataset 1", "summary": "Summary 1", "taxon": "Human", "gdstype": "Expression"},
        "GSE67890": {"title": "Dataset 2", "summary": "Summary 2", "taxon": "Mouse", "gdstype": "Genomic"},
    }
    return mock


@pytest.fixture
def mock_file_reader(mocker):
    mock = mocker.patch("app.services.FileReader.read_lines")
    mock.return_value = ["12345678", "87654321"]  # Mocked PMIDs
    return mock


@pytest.fixture
def pubmed_ds_controller(mock_api_service, mock_file_reader, mocker):
    # Mock ApiService
    mocker.patch("app.controllers.pubmed_ds_controller.ApiService")
    controller = PubmedDSController()
    controller.api_service = mock_api_service  # Inject mock service
    return controller


def test_get_ds_data(pubmed_ds_controller):
    ds_data = pubmed_ds_controller.get_ds_data()
    assert len(ds_data) == 2
    assert "GSE12345" in ds_data
    assert ds_data["GSE12345"]["title"] == "Dataset 1"


def test_set_ds_data_dict(pubmed_ds_controller):
    ds_data = pubmed_ds_controller.set_ds_data_dict()
    assert "GSE67890" in ds_data
    assert ds_data["GSE67890"]["summary"] == "Summary 2"


def test_get_ds_ids(pubmed_ds_controller):
    ds_ids = pubmed_ds_controller._get_ds_ids()
    assert ds_ids == ["GSE12345", "GSE67890"]
