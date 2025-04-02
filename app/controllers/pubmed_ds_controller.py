
from app.services import FileReader
from app.config import PMIDs_CONFIG
from app.services import TfIdfService, DatasetApiService


class PubmedDSController:
    __instance = None
    __ds_data = None
    __ds_vectors = None

    def __new__(cls, api_service: DatasetApiService = None, tf_idf_service: TfIdfService = None, data_location=PMIDs_CONFIG.DATA_FILE_PATH):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            cls.__instance.api_service = api_service
            cls.__instance.tf_idf_service = tf_idf_service
            if not api_service or not tf_idf_service:
                raise ValueError("Needed services must be injected.")
        return cls.__instance

    def __init__(self, api_service=None, tf_idf_service=None, data_location=PMIDs_CONFIG.DATA_FILE_PATH):
        pass  # Prevent re-initialization

    def _get_ds_ids(self):
        """Fetch dataset IDs linked to PubMed articles.
        Returns:dict
            {paper_id: ds_ids} - Paper IDs mapped to dataset IDs
        """
        fr = FileReader(PMIDs_CONFIG.DATA_FILE_PATH)
        page_ids = fr.read_lines()
        return self.api_service.fetch_ds_ids(page_ids)

    def set_ds_data_dict(self):
        """Fetch dataset details."""
        ds_ids = self._get_ds_ids()
        return self.api_service.fetch_ds_details(ds_ids)

    def get_ds_data(self):
        """Retrieve dataset details, fetching if not already available."""
        if self.__ds_data is None:
            self.__ds_data = self.set_ds_data_dict()
        return self.__ds_data

    def compute_ds_vectors(self):
        """Compute and store dataset vectors using TfIdfService."""
        if self.__ds_data is None:
            self.__ds_data = self.set_ds_data_dict()
        self.__ds_vectors = self.tf_idf_service.compute_vectors(self.__ds_data)

    def get_ds_vectors(self):
        """Retrieve dataset vectors, computing if not already available."""
        if self.__ds_vectors is None:
            self.compute_ds_vectors()
        return self.__ds_vectors

    def get_ds_names(self):
        """Retrieve dataset names."""
        if self.__ds_data is None:
            self.set_ds_data_dict()
        return {ds_id: ds_data['title'] for ds_id, ds_data in self.__ds_data.items()}

    def dimension_reduction(self):
        """
        Reduce TF-IDF vectors to 2D using PCA.

        Returns:
        --------
        list of dicts
            [{'id': ds_id, 'value': [x, y]}, ...] - Reduced 2D representations
        """
        if self.__ds_vectors is None:
            self.set_ds_vectors()

        ds_ids = list(self.__ds_vectors.keys())  # Extract dataset IDs
        vectors = list(self.__ds_vectors.values())  # Extract vector data

        reduced_values = self.tf_idf_service.reduce_dimensions(
            vectors)  # Reduce dimensions

        return [{"id": ds_id, "value": value.tolist()} for ds_id, value in zip(ds_ids, reduced_values)]

    def get_ds_data_by_id(self, ds_id):
        """Fetch dataset details by ID."""
        if self.__ds_data is None:
            self.set_ds_data_dict()
        return self.__ds_data.get(ds_id, None)
