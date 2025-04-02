import concurrent.futures
import threading
import time


class DatasetApiService:
    def __init__(self, api_service):
        self.api_service = api_service
        self.rate_limiter = threading.Semaphore(
            3)  # Limit to 3 requests per second

    def fetch_ds_ids(self, page_ids):  # Not being done in batches to have the paper ids linked
        """Fetch dataset IDs linked to PubMed pages."""
        ret = {}

        def fetch_and_process_batch(curr_id):
            """Fetch and process a batch of PubMed IDs."""
            with self.rate_limiter:
                # Simulate a delay for rate limiting
                if self.api_service.uses_api_key():
                    time.sleep(0.35)
                else:
                    time.sleep(1)
                try:
                    batch_raw = self.api_service.get(
                        "elink.fcgi",
                        {"dbfrom": "pubmed", "linkname": "pubmed_gds",
                         "id": curr_id, "retmode": "json"}
                    )
                    if "linksets" in batch_raw and batch_raw["linksets"]:
                        # Unpack the links
                        return batch_raw["linksets"][0]["linksetdbs"][0]["links"]
                except Exception as e:
                    print(f"Error fetching data for ID {curr_id}: {e}")
                    return {}

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = {executor.submit(
                fetch_and_process_batch, curr_id): curr_id for curr_id in page_ids}
            for i, future in enumerate(concurrent.futures.as_completed(futures)):
                curr_id = futures[future]
                try:
                    links = future.result()
                    if links:
                        ret[curr_id] = links
                except Exception as e:
                    print(f"Error processing batch for ID {curr_id}: {e}")

                # # Introduce a delay every 10 requests
                # if (i + 1) % 10 == 0:
                #     time.sleep(2)  # Pause for 1 second
        return ret

    def fetch_ds_details(self, paper_ds, batch_size=20):
        """Fetch dataset details from GDS API in batches.
        Args:
            paper_ds (dict): Dictionary mapping paper IDs to dataset IDs.
            batch_size (int): Number of dataset IDs to fetch in each batch."""
        ret = {}

        # Track all paper IDs associated with each dataset ID
        dataset_to_papers = {}
        for paper_id, ds_ids in paper_ds.items():
            for ds_id in ds_ids:
                if ds_id not in dataset_to_papers:
                    dataset_to_papers[ds_id] = []
                dataset_to_papers[ds_id].append(paper_id)

        def fetch_and_process_batch(curr_ids):
            """ Fetch and process a batch of dataset IDs. """
            with self.rate_limiter:
                if self.api_service.uses_api_key():
                    time.sleep(0.35)
                else:
                    time.sleep(1)
            curr_ids_str = ",".join(str(id) for id in curr_ids)
            try:
                batch_raw = self.api_service.get(
                    "esummary.fcgi",
                    {"db": "gds", "id": curr_ids_str, "retmode": "json"}
                )
                batch_raw = batch_raw.get("result", {})

                result = {}
                for id in curr_ids:
                    if id in batch_raw:
                        result[id] = {
                            "title": batch_raw[id]["title"],
                            "summary": batch_raw[id]["summary"],
                            "taxon": batch_raw[id]["taxon"],
                            "gdstype": batch_raw[id]["gdstype"],
                            # Assign the list of paper IDs
                            "paper_ids": dataset_to_papers[id]
                        }
                return result

            except Exception as e:
                print(f"Error fetching data for batch {curr_ids}: {e}")
                return {}

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            all_ds_ids = list(
                set(ds_id for ds_ids in paper_ds.values() for ds_id in ds_ids))

            for i in range(0, len(all_ds_ids), batch_size):
                curr_ids = all_ds_ids[i:i+batch_size]
                futures.append(executor.submit(
                    fetch_and_process_batch, curr_ids))
                if (i // batch_size + 1) % 10 == 0:
                    time.sleep(1)
            for future in concurrent.futures.as_completed(futures):
                ret.update(future.result())

        return ret
