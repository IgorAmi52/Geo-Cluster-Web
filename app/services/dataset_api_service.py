import concurrent.futures


class DatasetApiService:
    def __init__(self, api_service):
        self.api_service = api_service

    def fetch_ds_ids(self, page_ids, batch_size=500):
        """Fetch dataset IDs linked to PubMed pages."""
        ret = []
        while page_ids:
            curr_ids = page_ids[:batch_size]
            curr_ids_str = ",".join(str(id) for id in curr_ids)
            page_ids = page_ids[batch_size:]

            try:
                batch_raw = self.api_service.get(
                    "elink.fcgi",
                    {"dbfrom": "pubmed", "linkname": "pubmed_gds",
                     "id": curr_ids_str, "retmode": "json"}
                )

                # Unpack the links
                if "linksets" in batch_raw and batch_raw["linksets"]:
                    for link in batch_raw["linksets"][0]["linksetdbs"][0]["links"]:
                        ret.append(link)

            except Exception as e:
                print(f"Error fetching dataset IDs: {e}")

        return ret

    def fetch_ds_details(self, ds_ids, batch_size=20):
        """Fetch dataset details from GDS API in batches."""
        ret = {}

        def fetch_and_process_batch(curr_ids):
            """ Fetch and process a batch of dataset IDs. """
            curr_ids_str = ",".join(str(id) for id in curr_ids)
            try:
                batch_raw = self.api_service.get(
                    "esummary.fcgi",
                    {"db": "gds", "id": curr_ids_str, "retmode": "json"}
                )
                batch_raw = batch_raw.get("result", {})

                return {
                    id: {
                        "title": batch_raw[id]["title"],
                        "summary": batch_raw[id]["summary"],
                        "taxon": batch_raw[id]["taxon"],
                        "gdstype": batch_raw[id]["gdstype"],
                        "used_in": id
                    }
                    for id in curr_ids if id in batch_raw
                }

            except Exception as e:
                print(f"Error fetching data for batch {curr_ids}: {e}")
                return {}

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            while ds_ids:
                curr_ids = ds_ids[:batch_size]
                ds_ids = ds_ids[batch_size:]
                futures.append(executor.submit(
                    fetch_and_process_batch, curr_ids))

            for future in concurrent.futures.as_completed(futures):
                ret.update(future.result())

        return ret
