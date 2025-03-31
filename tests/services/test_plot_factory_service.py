import pytest
import numpy as np
from unittest.mock import Mock
from app.services.plot_factory_service import PlotFactory
from app.config import PLOT_MODE


@pytest.fixture
def mock_clustering_service():
    mock_service = Mock()
    mock_service.cluster_data.return_value = np.array([0, 1, 1, 0])
    return mock_service


@pytest.fixture
def plot_factory(mock_clustering_service):
    return PlotFactory(mode=PLOT_MODE.SCATTER, clustering_service=mock_clustering_service)


def test_change_mode_valid(plot_factory):
    plot_factory.change_mode(PLOT_MODE.SCATTER)
    assert plot_factory.get_mode() == PLOT_MODE.SCATTER


def test_change_mode_invalid(plot_factory):
    with pytest.raises(ValueError, match="Invalid plot mode: invalid_mode"):
        plot_factory.change_mode("invalid_mode")


def test_create_plot_invalid_data(plot_factory):
    invalid_data = {"id": 1, "value": [0.1, 0.2]}  # Not a list of dictionaries
    names = {"id": "Dataset 1"}
    with pytest.raises(ValueError, match="Data must be a list of dictionaries"):
        plot_factory.create_plot(invalid_data, names)


def test_create_plot_invalid_names(plot_factory):
    data = [{"id": 1, "value": [0.1, 0.2]}]
    invalid_names = [{"id": "Dataset 1"}]  # Not a dictionary
    with pytest.raises(ValueError, match="Names must be a dictionary"):
        plot_factory.create_plot(data, invalid_names)


def test_create_scatter_plot_with_clustering(plot_factory):
    data = [
        {"id": 1, "value": [0.1, 0.2]},
        {"id": 2, "value": [0.3, 0.4]},
        {"id": 3, "value": [0.5, 0.6]},
        {"id": 4, "value": [0.7, 0.8]},
    ]
    names = {1: "Dataset 1", 2: "Dataset 2", 3: "Dataset 3", 4: "Dataset 4"}
    fig = plot_factory.create_plot(data, names, clustering=True)

    assert fig.data[0].type == "scatter"
    assert len(fig.data[0].x) == len(data)
    assert len(fig.data[0].y) == len(data)
    assert fig.data[0].marker.showscale is True


def test_create_scatter_plot_without_clustering(plot_factory):
    data = [
        {"id": 1, "value": [0.1, 0.2]},
        {"id": 2, "value": [0.3, 0.4]},
    ]
    names = {1: "Dataset 1", 2: "Dataset 2"}
    fig = plot_factory.create_plot(data, names, clustering=False)

    assert fig.data[0].type == "scatter"
    assert fig.data[0].marker.color == "blue"
