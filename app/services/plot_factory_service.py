import numpy as np
from app.config import PLOT_MODE
import plotly.graph_objs as go


class PlotFactory:
    def __init__(self, mode='scatter', clustering_service=None):
        self.mode = mode
        self.clustering_service = clustering_service

    def change_mode(self, mode):
        """Change the plot mode"""
        if mode not in PLOT_MODE.__members__.values():
            raise ValueError(f"Invalid plot mode: {mode}")
        self.mode = mode

    def get_mode(self):
        """Get the current plot mode"""
        return self.mode

    def create_plot(self, data, names, clustering=True):
        """Creates a plot based on the selected mode
        Args:
            data (dictionary): dictionary containing 'id' and 'value' keys.
            names (dictionary): dictionary containing 'id' and 'name' keys.
            clustering (bool): whether to apply clustering or not."""
        if not isinstance(data, list) or not all(isinstance(d, dict) for d in data):
            raise ValueError(
                "Data must be a list of dictionaries with 'id' and 'value' keys.")
        if not isinstance(names, dict):
            raise ValueError(
                "Names must be a dictionary with 'id' and 'name' keys.")
        if self.mode == PLOT_MODE.SCATTER:
            return self._create_scatter_plot(data, names, clustering)
        else:
            raise ValueError(f"Unsupported plot mode: {self.mode}")

    def _create_scatter_plot(self, data, names, clustering=True):
        """ Data is a list of dictionaries with 'id' and 'value' keys. """
        x_coords = []
        y_coords = []
        id_names = []
        for point in data:
            x_coords.append(point['value'][0])
            y_coords.append(point['value'][1])
            id_names.append((names[point['id']], point['id']))

        if clustering:
            coordinates = np.column_stack((x_coords, y_coords))
            cluster_labels = self.clustering_service.cluster_data(coordinates)
            normalized_labels = (cluster_labels - cluster_labels.min()) / \
                (cluster_labels.max() - cluster_labels.min())
        else:
            normalized_labels = 'blue'

        # Create scatter plot
        scatter = go.Scatter(
            x=x_coords,
            y=y_coords,
            mode='markers',
            marker=dict(
                size=10,
                colorscale='Viridis',
                color=normalized_labels,
                showscale=True,  # Show color scale for clustering
                opacity=0.7
            ),
            customdata=id_names,  # Attach dataset name and ID
            hovertemplate='Name: %{customdata[0]}<br>Dataset ID: %{customdata[1]}<extra></extra>'
        )

        # Create layout
        layout = go.Layout(
            hovermode='closest',
            plot_bgcolor='white',
            autosize=True,
            height=650
        )

        # Create figure
        fig = go.Figure(data=[scatter], layout=layout)

        # Add annotations for clarity
        fig.update_layout(
            annotations=[
                dict(
                    x=0.5,
                    y=-0.1,
                    xref='paper',
                    yref='paper',
                    text='Each point represents a dataset, positioned by its TF-IDF vector characteristics',
                    showarrow=False,
                    font=dict(size=10)
                )
            ]
        )

        return fig
