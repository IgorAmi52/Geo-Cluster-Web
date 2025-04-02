class PaperApiService:
    def __init__(self, api_service):
        self.api_service = api_service

    def fetch_paper_details(self, paper_id):
        """Fetch details for a list of paper IDs."""
        response = self.api_service.get(
            "esummary.fcgi",
            {"db": "pubmed", "id": paper_id, "retmode": "json"}
        )
        if "result" in response and str(paper_id) in response["result"]:
            return response["result"][str(paper_id)]
