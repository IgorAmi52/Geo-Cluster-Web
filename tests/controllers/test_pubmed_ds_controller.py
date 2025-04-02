import pytest
from unittest.mock import MagicMock
from app.controllers import PubmedDSController
from app.services import DatasetApiService, FileReader, TfIdfService
from app.config import PMIDs_CONFIG
import numpy as np  # Add this import for NumPy


@pytest.fixture
def mock_api_service():
    mock = MagicMock(spec=DatasetApiService)
    mock.fetch_ds_ids.return_value = {"PAPER_ID": ["GSE12345", "GSE67890"]}
    mock.fetch_ds_details.return_value = {
        "GSE12345": {"title": "Dataset 1", "summary": "Summary 1", "taxon": "Human", "gdstype": "Expression"},
        "GSE67890": {"title": "Dataset 2", "summary": "Summary 2", "taxon": "Mouse", "gdstype": "Genomic"},
    }
    return mock


@pytest.fixture
def mock_tfidf_service():
    mock = MagicMock(spec=TfIdfService)
    mock.compute_vectors.return_value = {
        "GSE12345": [0.1, 0.2, 0.3],
        "GSE67890": [0.4, 0.5, 0.6],
    }
    mock.reduce_dimensions.return_value = np.array(
        [[1.0, 2.0], [3.0, 4.0]])  # Return NumPy array
    return mock


@pytest.fixture
def mock_file_reader(mocker):
    mock = mocker.patch("app.services.FileReader.read_lines")
    mock.return_value = ["12345678", "87654321"]  # Mocked PMIDs
    return mock


@pytest.fixture
def pubmed_ds_controller(mock_api_service, mock_tfidf_service):
    controller = PubmedDSController(
        mock_api_service, mock_tfidf_service, PMIDs_CONFIG.DATA_FILE_PATH)
    return controller


def test_get_ds_data(pubmed_ds_controller):
    ds_data = pubmed_ds_controller.get_ds_data()
    assert len(ds_data) == 2
    assert "GSE12345" in ds_data
    assert ds_data["GSE12345"]["title"] == "Dataset 1"
    assert ds_data["GSE12345"]["taxon"] == "Human"


def test_set_ds_data_dict(pubmed_ds_controller):
    ds_data = pubmed_ds_controller.set_ds_data_dict()
    assert "GSE67890" in ds_data
    assert ds_data["GSE67890"]["summary"] == "Summary 2"
    assert ds_data["GSE67890"]["gdstype"] == "Genomic"


def test_get_ds_ids(pubmed_ds_controller):
    ds_dict = pubmed_ds_controller._get_ds_ids()
    assert ds_dict == {"PAPER_ID": ["GSE12345", "GSE67890"]}


def test_compute_ds_vectors(pubmed_ds_controller):
    pubmed_ds_controller.compute_ds_vectors()
    assert pubmed_ds_controller._PubmedDSController__ds_vectors is not None
    assert "GSE12345" in pubmed_ds_controller._PubmedDSController__ds_vectors
    assert len(
        pubmed_ds_controller._PubmedDSController__ds_vectors["GSE12345"]) == 3


def test_get_ds_vectors(pubmed_ds_controller):
    ds_vectors = pubmed_ds_controller.get_ds_vectors()
    assert len(ds_vectors) == 2
    assert "GSE12345" in ds_vectors
    assert ds_vectors["GSE12345"] == [0.1, 0.2, 0.3]


def test_get_ds_names(pubmed_ds_controller):
    ds_names = pubmed_ds_controller.get_ds_names()
    assert len(ds_names) == 2
    assert ds_names["GSE12345"] == "Dataset 1"
    assert ds_names["GSE67890"] == "Dataset 2"


def test_dimension_reduction(pubmed_ds_controller):
    pubmed_ds_controller.compute_ds_vectors()  # Ensure vectors are computed
    reduced_data = pubmed_ds_controller.dimension_reduction()
    assert len(reduced_data) == 2
    assert reduced_data[0]["id"] == "GSE12345"
    assert reduced_data[0]["value"] == [1.0, 2.0]
    assert reduced_data[1]["id"] == "GSE67890"
    assert reduced_data[1]["value"] == [3.0, 4.0]
