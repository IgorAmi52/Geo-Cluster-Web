import pytest
import numpy as np
from scipy import sparse
from app.services import TfIdfService


@pytest.fixture
def tfidf_service():
    return TfIdfService()


def test_preprocess_text(tfidf_service):
    text = "This is a sample TEXT, with punctuation!"
    processed_text = tfidf_service.preprocess_text(text)
    assert processed_text == "sample text punctuation"


def test_generate_ds_description(tfidf_service):
    ds_entry = {"title": "Dataset Title",
                "description": "This is a sample dataset."}
    description = tfidf_service.generate_ds_description(ds_entry)
    assert description == "dataset title sample dataset"


def test_compute_vectors(tfidf_service):
    ds_data = {
        1: {"title": "Dataset One", "description": "First dataset description."},
        2: {"title": "Dataset Two", "description": "Second dataset description."},
    }
    vectors = tfidf_service.compute_vectors(ds_data)
    assert len(vectors) == 2
    assert all(sparse.issparse(vec) for vec in vectors.values())


def test_reduce_dimensions(tfidf_service):
    vectors = [
        sparse.csr_matrix([0.1, 0.2, 0.3]),
        sparse.csr_matrix([0.4, 0.5, 0.6]),
        sparse.csr_matrix([0.7, 0.8, 0.9]),
    ]
    reduced_data = tfidf_service.reduce_dimensions(vectors)
    assert reduced_data.shape == (3, 2)  # 3 samples reduced to 2 dimensions
    assert isinstance(reduced_data, np.ndarray)
