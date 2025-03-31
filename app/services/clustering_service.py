from sklearn.cluster import KMeans
import numpy as np


class ClusteringService:
    def __init__(self, n_clusters=4):
        self.n_clusters = n_clusters
        self.kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)

    def cluster_data(self, data):
        """
        Clusters the 2D points into `n_clusters`.

        Parameters:
        -----------
        data : list of lists or numpy array
            2D array where each row is [x, y]

        Returns:
        --------
        np.ndarray
            Cluster labels for each data point
        """
        if len(data) == 0:
            raise ValueError("Data for clustering is empty.")
        if len(data[0]) != 2:
            raise ValueError("Data must be 2D points.")
        return self.kmeans.fit_predict(np.array(data))
