# app/controllers/pubmed_ds_controller.py
from app.services import DatasetApiService, FileReader
from app.config import API_CONFIG, PMIDs_CONFIG
from app.services import ApiService


class PubmedDSController:
    __instance = None
    __ds_data = None

    def __new__(cls, data_location=PMIDs_CONFIG.DATA_FILE_PATH):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            api_service = ApiService(API_CONFIG.BASE_API, API_CONFIG.API_KEY)
            cls.__instance.api_service = DatasetApiService(api_service)
        return cls.__instance

    def __init__(self, data_location=PMIDs_CONFIG.DATA_FILE_PATH):
        pass  # Prevent re-initialization

    def get_ds_data(self):
        """Retrieve dataset details"""
        if self.__ds_data is None:
            self.__ds_data = self.set_ds_data_dict()
        return self.__ds_data

    def set_ds_data_dict(self):
        """Fetch dataset details"""
        ds_ids = self._get_ds_ids()
        return self.api_service.fetch_ds_details(ds_ids)

    def _get_ds_ids(self):
        """Fetch dataset IDs linked to PubMed articles."""
        fr = FileReader(PMIDs_CONFIG.DATA_FILE_PATH)

        page_ids = fr.read_lines()
        return self.api_service.fetch_ds_ids(page_ids)
