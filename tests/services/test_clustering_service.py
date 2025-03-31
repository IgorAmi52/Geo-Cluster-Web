import pytest
import numpy as np
from sklearn.cluster import KMeans
from app.services import ClusteringService


def test_cluster_data_valid_input():
    # Arrange
    service = ClusteringService(n_clusters=3)
    data = [[1, 2], [2, 3], [10, 10], [11, 11], [50, 50], [51, 51]]

    # Act
    labels = service.cluster_data(data)

    # Assert
    assert len(labels) == len(data)
    assert set(labels) == {0, 1, 2}  # Ensure 3 clusters are formed


def test_cluster_data_empty_input():
    # Arrange
    service = ClusteringService(n_clusters=3)
    data = []

    # Act & Assert
    with pytest.raises(ValueError, match="Data for clustering is empty."):
        service.cluster_data(data)


def test_cluster_data_single_point():
    # Arrange
    service = ClusteringService(n_clusters=1)
    data = [[5, 5]]

    # Act
    labels = service.cluster_data(data)

    # Assert
    assert len(labels) == 1
    assert labels[0] == 0  # Single cluster


def test_cluster_data_high_dimensional_input():
    # Arrange
    service = ClusteringService(n_clusters=2)
    data = [[1, 2, 3], [4, 5, 6]]  # Invalid input (not 2D points)

    # Act & Assert
    with pytest.raises(ValueError):
        service.cluster_data(data)


def test_cluster_data_consistent_results():
    # Arrange
    service = ClusteringService(n_clusters=2)
    data = [[1, 1], [2, 2], [10, 10], [11, 11]]

    # Act
    labels1 = service.cluster_data(data)
    labels2 = service.cluster_data(data)

    # Assert
    # Consistent results due to random_state
    assert np.array_equal(labels1, labels2)
